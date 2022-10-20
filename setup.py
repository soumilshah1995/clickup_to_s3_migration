from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="clickup_to_s3_migration",
    version="1.0.0",
    description=""" My coworkers and I created this free and open-source library. Anyone can now transfer entire clicks folders, tickets, and comments to AWS S3. When we switched from Clickup to JIRA software, this task was essentially done to backup the entire Clickup system. This threaded script employs the maximum number of threads to use ClickUP APIS and migrate all data into Data Lake S3 so that users or teams can use Athena to query using regular SQL if necessary. """,
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/soumilshah1995/clickup_to_s3_migration",
    author="Soumil Nitin Shah",
    author_email="shahsoumil519@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ClickUptoS3Migration"],
    include_package_data=True,
    install_requires=["boto3", "tqdm"]
)