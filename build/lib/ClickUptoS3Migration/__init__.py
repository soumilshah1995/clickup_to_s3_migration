try:
    import os
    import re
    import json
    import requests
    import threading
    import logging
    from logging import StreamHandler
    import os
    import json
    import boto3
    import uuid
    import re
    import datetime
    import logging
    import base64
    from tqdm import tqdm
    from datetime import datetime
    import ssl
    import boto3
    import urllib3
except Exception as e:
    pass

try:
    urllib3.disable_warnings()
except Exception as e:
    pass


class Logging(object):
    def __init__(self):
        format = "[%(asctime)s] %(name)s %(levelname)s %(message)s"
        # Logs to file
        logging.basicConfig(
            filename="migrationlog",
            filemode="a",
            format=format,
            level=logging.INFO,
        )
        self.logger = logging.getLogger("batch_jobs")
        formatter = logging.Formatter(
            format,
        )
        # Logs to Console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


class AWSS3(object):
    """Helper class to which add functionality on top of boto3 """

    def __init__(self,
                 bucket="",
                 aws_access_key_id="",
                 aws_secret_access_key="",
                 region_name="",
                 ):
        self.BucketName = bucket
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def put_files(self, Response=None, Key=None):
        """
        Put the File on S3
        :return: Bool
        """
        try:
            DATA = bytes(json.dumps(Response).encode("UTF-8"))
            response = self.s3_client.put_object(
                ACL="private", Body=DATA, Bucket=self.BucketName, Key=Key
            )
            return "ok"
        except Exception as e:
            print("Error : {} ".format(e))
            return "error"

    def item_exists(self, Key):
        """Given key check if the items exists on AWS S3 """
        try:
            response_new = self.s3_client.get_object(Bucket=self.BucketName, Key=str(Key))
            return True
        except Exception as e:
            return False

    def get_item(self, Key):
        """Gets the Bytes Data from AWS S3 """
        try:
            response_new = self.s3_client.get_object(Bucket=self.BucketName, Key=str(Key))
            return response_new["Body"].read()
        except Exception as e:
            print("Error :{}".format(e))
            return False

    def find_one_update(self, data=None, key=None):
        """
        This checks if Key is on S3 if it is return the data from s3
        else store on s3 and return it
        """
        flag = self.item_exists(Key=key)
        if flag:
            data = self.get_item(Key=key)
            return data
        else:
            self.put_files(Key=key, Response=data)
            return data

    def delete_object(self, Key):
        response = self.s3_client.delete_object(Bucket=self.BucketName, Key=Key, )
        return response

    def get_all_keys(self, Prefix=""):
        """
        :param Prefix: Prefix string
        :return: Keys List
        """
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.BucketName, Prefix=Prefix)
            tmp = []
            for page in pages:
                for obj in page["Contents"]:
                    tmp.append(obj["Key"])
            return tmp
        except Exception as e:
            return []

    def print_tree(self):
        keys = self.get_all_keys()
        for key in keys:
            print(key)
        return None

    def find_one_similar_key(self, searchTerm=""):
        keys = self.get_all_keys()
        return [key for key in keys if re.search(searchTerm, key)]

    def __repr__(self):
        return "AWS S3 Helper class "


global aws_helper
logger = Logging()


class Request(object):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def make_http_get(self, verify=False, params={}):
        r = requests.get(
            url=self.url, headers=self.headers, verify=verify, params=params
        )
        r = r.json()
        return r

    def make_http_post(self, data, verify=False):
        if data is None:
            r = requests.post(
                url=self.url.__str__(), headers=self.headers, verify=verify
            )
            r = r.json()
            return r
        else:
            r = requests.post(
                url=self.url, headers=self.headers, data=json.dumps(data), verify=verify
            )
            r = r.json()
            return r


class Task(Request):

    def __init__(self, list_id, page_no="0"):
        self.list_id = list_id
        self.page_no = page_no
        Request.__init__(self,
                         url="""https://api.clickup.com/api/v2/list/{}/task?page={}&subtasks=true&include_closed=true""".format(
                             self.list_id, page_no),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_tasks(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("tasks"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class Comments(Request):

    def __init__(self, task_id):
        self.task_id = task_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/task/{}/comment".format(self.task_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_comments(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("comments"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class Lists(Request):
    def __init__(self, list_id):
        self.list_id = list_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/folder/{}/list".format(self.list_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_lists(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("lists"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class Folders(Request):
    def __init__(self, space_id):
        self.space_id = space_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/space/{}/folder".format(self.space_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_folders(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("folders"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class Spaces(Request):
    def __init__(self, space_id):
        self.space_id = space_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/team/{}/space".format(self.space_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_spaces(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("spaces"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class Tags(Request):
    def __init__(self, tag_id):
        self.tag_id = tag_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/space/{}/tag".format(self.tag_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_tags(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("tags"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class FoldersLists(Request):
    def __init__(self, space_id):
        self.space_id = space_id
        Request.__init__(self, url="https://api.clickup.com/api/v2/space/{}/list".format(self.space_id),
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_folders_lists(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("lists"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class GetTeams(Request):
    def __init__(self):
        Request.__init__(self, url="https://api.clickup.com/api/v2/team",
                         headers={
                             'Content-Type': 'application/json',
                             'Authorization': os.getenv("clickup_api_token")
                         }
                         )

    def get_all_teams(self):
        tickets = self.make_http_get()
        responses = []
        for items in tickets.get("teams"):
            try:
                responses.append(items)
            except Exception as e:
                pass
        return responses


class MyHasher(object):
    def __init__(self, key):
        self.key = key

    def get(self):
        keys = str(self.key).encode("UTF-8")
        keys = base64.b64encode(keys)
        keys = keys.decode("UTF-8")
        return keys

    def decode(self):
        keys = base64.b64decode(self.key)
        keys = keys.decode("utf-8")
        return keys


def get_spaces(org_id):
    space_helper = Spaces(space_id=org_id)
    spaces = space_helper.get_spaces()
    return spaces


def get_tags(space_id):
    tags = Tags(tag_id=space_id)
    tags_data = tags.get_tags()
    """Tags"""
    for tag in tqdm(tags_data):
        try:
            hasher_instance = MyHasher(key=tag)
            tag_id = hasher_instance.get()
            aws_helper.put_files(Key="tags/{}.json".format(tag_id), Response=tag)
        except Exception as e:
            pass


def get_folders(space_id):
    """Folders"""
    list_folder = Folders(space_id=space_id)
    list_folders_data = list_folder.get_folders()
    for folder in tqdm(list_folders_data):
        try:
            folder_id = folder.get("id")
            logger.logger.info(" get_folders | folder_id | " + str(folder_id))
            aws_helper.put_files(Key="folders/{}.json".format(folder_id), Response=folder)
            get_list(folder_id=folder_id)
        except Exception as e:
            pass
    return list_folders_data


def get_folder_less_list(space_id):
    helper_folder = FoldersLists(space_id=space_id)
    lists = helper_folder.get_folders_lists()
    for list_ in tqdm(lists):
        try:
            list_id = list_.get("id")
            logger.logger.info(" get_folder_less_list | list_id " + str(list_id))
            aws_helper.put_files(Key="lists/{}.json".format(list_id), Response=list_)
            get_tasks(list_id=list_id)
        except Exception as e:
            pass

    return lists


def get_list(folder_id):
    listhelper = Lists(list_id=folder_id)
    list_data = listhelper.get_lists()
    for list_ in tqdm(list_data):
        try:
            list_id = list_.get("id")
            logger.logger.info("get_list | list_id | " + str(list_id))
            aws_helper.put_files(Key="lists/{}.json".format(list_id), Response=list_)
            task = get_tasks(list_id=list_id)
        except Exception as e:
            pass


def get_tasks(list_id):
    for page_number in range(0, 10):
        try:
            task_helper = Task(list_id=list_id, page_no=str(page_number))
            tasks_data = task_helper.get_tasks()
            logger.logger.info(" Task Page Number  | " + str(page_number))

            if tasks_data == []:
                break

            for task in tqdm(tasks_data):
                try:
                    task_id = task.get("id")
                    logger.logger.info(" task_id | " + str(task_id))
                    aws_helper.put_files(Key="tasks/{}.json".format(task_id), Response=task)
                    get_comments(task_id=task_id)
                except Exception as e:
                    pass
        except Exception as e:
            break

    return None


def get_comments(task_id):
    commenthelper = Comments(task_id=task_id)
    comments_data = commenthelper.get_comments()
    for comment in tqdm(comments_data):
        try:
            comment_id = comment.get("id")
            comment['task_id'] = task_id
            aws_helper.put_files(Key="comment/{}.json".format(comment_id), Response=comment)
        except Exception as e:
            pass
    return None


class ClickUptoS3Migration(GetTeams):

    def __init__(self, aws_access_key_id,
                 aws_secret_access_key,
                 region_name,
                 bucket,
                 clickup_api_token):

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bucket = bucket
        self.clickup_api_token = clickup_api_token

        self.__set_enviroments()
        GetTeams.__init__(self)

    def __set_enviroments(self):

        os.environ['clickup_api_token'] = self.clickup_api_token
        os.environ['aws_access_key_id'] = self.aws_access_key_id
        os.environ['aws_secret_access_key'] = self.aws_secret_access_key
        os.environ['bucket'] = self.bucket
        os.environ['region_name'] = self.region_name

        global aws_helper

        aws_helper = AWSS3(
            aws_access_key_id=os.getenv("aws_access_key_id"),
            aws_secret_access_key=os.getenv("aws_secret_access_key"),
            region_name=os.getenv("region_name"),
            bucket=os.getenv("bucket")
        )

    def run(self):

        team_data = self.get_all_teams()

        for team in team_data:

            org_id = team.get("id")

            aws_helper.put_files(Key="team/{}.json".format(org_id), Response=team)
            spaces = get_spaces(org_id=org_id)

            for space in tqdm(spaces):
                start_time = datetime.now()

                space_name = space.get("name")
                logger.logger.info("space name " + space_name)
                space_id = space.get("id")
                aws_helper.put_files(Key="space/{}.json".format(space_id), Response=space)

                thread_tags = threading.Thread(target=get_tags, args=(space_id,))
                thread_folders = threading.Thread(target=get_folder_less_list, args=(space_id,))
                thread_folder = threading.Thread(target=get_folders, args=(space_id,))

                thread_tags.start()
                thread_folders.start()
                thread_folder.start()

                thread_tags.join()
                thread_folders.join()
                thread_folder.join()

                end_time = datetime.now()

                total_time = end_time - start_time
                logger.logger.info("Completed Migrating {} Took {}".format(str(space_name), str(total_time)))

# def main():
#     helper = ClickUptoS3Migration(
#         aws_access_key_id="<ACCESS KEY>",
#         aws_secret_access_key="<SECRET KEY GOES HERE>",
#         region_name="<AWS REGION>",
#         bucket="<BUCKET NAME >",
#         clickup_api_token="<CLICKUP API KEY>"
#     )
#     ressponse = helper.run()
#
