# ClickUp to Data Lake (S3) Migration and backup All Data Scripts

[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)]

* My coworkers and I created this free and open-source library. Anyone can now transfer entire clicks folders, tickets, and comments to AWS S3. When we switched from Clickup to JIRA software, this task was essentially done to backup the entire Clickup system. This threaded script employs the maximum number of threads to use ClickUP APIS and migrate all data into Data Lake S3 so that users or teams can use Athena to query using regular SQL if necessary.

### Authors 
* Soumil Nitin Shah
* April Love Ituhat  
* Divyansh Patel

#### NOTE:
* This is migration script which will move all the data from ClickUp we will add  more features and methods in case if you want to just backup a given workspace or Folde. But For now this will Back up Everything feel free to add more functionality and submit Merge Request so other people can use the functionality. Note this is more than 500 Lines of code I will cleanup and add some amazing functionality during my free time


----------------------------------------------------------------------------

<img width="941" alt="c3" src="https://user-images.githubusercontent.com/39345855/197051580-514532f5-7161-4007-bdb1-b109dc3b355c.PNG">


clickup_to_s3_migration

## Installation

```bash
pip install clickup_to_s3_migration
```
## Usage

```python
import sys
from ClickUptoS3Migration import ClickUptoS3Migration


def main():
    helper = ClickUptoS3Migration(
        aws_access_key_id="<ACCESS KEY>",
        aws_secret_access_key="<SECRET KEY GOES HERE>",
        region_name="<AWS REGION>",
        bucket="<BUCKET NAME >",
        clickup_api_token="<CLICKUP API KEY>"
    )
    ressponse = helper.run()


main()

```
It’s really that easy this will iterate over all Workspaces For Each Workspaces it will call all Spaces and For Each Space it will get all Folders and For Each Folder it will Call List and For Each list call Tickets and Each Tickets call Comments

------------------------------------------------------------------

#### Explanation on the code works and Flow
* Company can have several WorkSpace. The Code calls API and get all workspaces. Each work spaces can have several spaces and each spaces can have several folders and Each folder has many Lists and Each list has many tickets and Each tickets can have several Comments
  ![image](https://user-images.githubusercontent.com/39345855/197052204-fa7a5509-e65e-4173-bc17-2b3db2ba5894.png)

##### Figure Shows the structure how click up stores data and shows how we need to iterate and get all data

# End Goal 
![image](https://user-images.githubusercontent.com/39345855/197052634-f4d0e059-9fa2-4477-b2b7-feed655ff498.png)

* Once the Script is complete running which might take 1 or 2 days depending upon how much data you have 
* you can Then create glue crawler and then  Query the data using Athena (SQL Query)




## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

