from typing import TypedDict, Optional, Tuple
import os
import time
import random
import string
import boto3
from cfnresponse import CfnResponse

AWS_REGION = os.environ["AWS_REGION"]
S3_RESOURCE = boto3.resource("s3", region_name=os.environ["AWS_REGION"])


class S3BucketProps(TypedDict):
    BucketName: str


class CreateEvent(TypedDict):
    LogicalResourceId: str
    ResourceProperties: S3BucketProps


class UpdateDeleteEvent(TypedDict):
    LogicalResourceId: str
    PhysicalResourceId: str
    ResourceProperties: S3BucketProps
    OldResourceProperties: S3BucketProps


class Handlers:
    @staticmethod
    def Create(event: CreateEvent):
        bucket_name = event["ResourceProperties"]["BucketName"]
        S3_RESOURCE.Bucket(name=bucket_name).create(
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        return {"MyBucketName": bucket_name, "Hello": "world"}

    @staticmethod
    def Update(event: UpdateDeleteEvent):
        new_bucket_name = event["ResourceProperties"]["BucketName"]
        old_bucket_name = event["OldResourceProperties"]["BucketName"]
        if new_bucket_name != old_bucket_name:
            S3_RESOURCE.Bucket(name=old_bucket_name).objects.all().delete()
            S3_RESOURCE.Bucket(name=old_bucket_name).delete()
            S3_RESOURCE.Bucket(name=new_bucket_name).create(
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
            )
        return {"MyBucketName": new_bucket_name, "Hello": "world"}

    @staticmethod
    def Delete(event: UpdateDeleteEvent):
        bucket_name = event["ResourceProperties"]["BucketName"]
        S3_RESOURCE.Bucket(name=bucket_name).objects.all().delete()
        S3_RESOURCE.Bucket(name=bucket_name).delete()


def handler(event, context):
    print(event, end="\r")

    try:
        response_data = getattr(Handlers, event["RequestType"])(event)
        CfnResponse.send(
            event, context, CfnResponse.SUCCESS, response_data=response_data
        )
    except Exception as e:
        CfnResponse.send(
            event,
            context,
            CfnResponse.FAILED,
            str(e),
            physical_resource_id=event.get("PhysicalResourceId"),
        )
        raise
