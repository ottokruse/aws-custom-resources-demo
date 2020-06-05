from typing import TypedDict, Optional, Tuple
import os
import time
import random
import string
import boto3
import json
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
        return bucket_name, {"MyBucketName": bucket_name, "Hello": "world"}

    @classmethod
    def Update(cls, event: UpdateDeleteEvent):
        return cls.Create(event)

    @staticmethod
    def Delete(event: UpdateDeleteEvent) -> None:
        bucket_name = event["PhysicalResourceId"]
        S3_RESOURCE.Bucket(name=bucket_name).objects.all().delete()
        S3_RESOURCE.Bucket(name=bucket_name).delete()
        return event["PhysicalResourceId"], None


def handler(event, context):
    print(json.dumps(event, indent=2).replace('\n', '\r'))

    try:
        physical_resource_id, response_data = getattr(Handlers, event["RequestType"])(
            event
        )
        CfnResponse.send(
            event,
            context,
            CfnResponse.SUCCESS,
            response_data=response_data,
            physical_resource_id=physical_resource_id,
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
