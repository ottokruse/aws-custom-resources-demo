from typing import TypedDict, Optional, Tuple, cast, Any, Union, Literal, Dict
import os
import time
import random
import string
import boto3
import json
from cfnresponse import CfnResponse

AWS_REGION = os.environ["AWS_REGION"]
S3_RESOURCE = boto3.resource("s3", region_name=os.environ["AWS_REGION"])


class Handlers:
    @staticmethod
    def Create(event: CreateEvent) -> Tuple[PhysicalResourceId, Data]:
        """Handle a CloudFormation Create request.

        CloudFormation sends a Create request:
            - When the stack is created initially for a CloudFormation template
                that includes this Custom Resource
            - When this Custom Resource is included (with a new LogicalResourceID)
                in an existing CloudFormation stack
        """

        bucket_name = event["ResourceProperties"].get("BucketName")
        if not bucket_name:
            # The user did not provide a BucketName explicitly so we'll generate one
            bucket_name = f'{event["LogicalResourceId"].lower()}{randomString()}'

        S3_RESOURCE.Bucket(name=bucket_name).create(
            CreateBucketConfiguration={"LocationConstraint": cast(Any, AWS_REGION)},
        )
        return bucket_name, {"MyBucketName": bucket_name, "Hello": "world"}

    @classmethod
    def Update(cls, event: UpdateEvent) -> Tuple[PhysicalResourceId, Data]:
        """Handle a CloudFormation Update request.

        CloudFormation sends an Update Request when the ResourceProperties of
            the Custom Resource were changed in the CloudFormation template.

        In our implementation we just proxy this to the Create handler, so that
            a new bucket is created using the new ResourceProperties. This
            will lead to a new PhysicalResourceId, prompting CloudFormation to send
            a Delete request for the previous PhysicalResourceId. This works for us,
            as we use the bucket name as PhysicalResourceId.
        """

        return cls.Create(event)

    @staticmethod
    def Delete(event: DeleteEvent) -> Tuple[PhysicalResourceId, Data]:
        """Handle a CloudFormation Delete request.

        This is what this Custom Resource is all about! Before deleting the actual
            bucket, it will throw away the objects inside it.

        The PhysicalResourceId is expected to contain the name of the bucket.

        Several scenario's might lead a CloudFormation Delete request:
            - The Custom Resource needs to be deleted because it was removed from the
                  CloudFormation stack's template
            - The Custom Resource needs to be deleted because it's logical ID in the
                  CloudFormation stack's template was changed (this Delete would be
                  accompanied by a separate Create request for the new logical ID)
            - The Custom Resource needs to be deleted from the Stack because the
                  CloudFormation stack is being deleted
        """

        bucket_name = event["PhysicalResourceId"]
        S3_RESOURCE.Bucket(name=bucket_name).objects.delete()
        S3_RESOURCE.Bucket(name=bucket_name).delete()

        return event["PhysicalResourceId"], {}


def handler(event: Union[CreateEvent, UpdateEvent, DeleteEvent], context):

    # Log the event to CloudWatch Logs for debugging (if needed)
    # Using /r instead of /n makes the log entry nicely expandable in CloudWatch logs
    print(json.dumps(event, indent=2).replace("\n", "\r"))

    # The outer try-except block ensures that a response is ALWAYS send to CloudFormation
    try:

        # Use the "RequestType" from the event (Create/Update/Delete),
        #   to determine the right function to call, and then call it passing the event.
        #
        #   Each handling function should return a tuple containing:
        #     - physical_resource_id (str): the physical resource id of your Custom Resource.
        #         This is an important field that you should specify explicitly.
        #         If you change the value of this field during a CloudFormation Update,
        #         CloudFormation will issue a Delete against the previous value.
        #     - response_data (dict): dictionary with key-value pairs that you can !GetAtt
        #         in your CloudFormation template
        physical_resource_id, response_data = getattr(Handlers, event["RequestType"])(
            event
        )

        # All done! Let CloudFormation know about our success
        CfnResponse.send(
            event,
            context,
            CfnResponse.SUCCESS,
            response_data=response_data,
            physical_resource_id=physical_resource_id,
        )

    except Exception as e:

        # Oops, we failed! Let's tell CloudFormation about this, so it knows
        #    and can rollback other changes in the stack
        CfnResponse.send(
            event,
            context,
            CfnResponse.FAILED,
            str(e),
            physical_resource_id=cast(Union[UpdateEvent, DeleteEvent], event).get(
                "PhysicalResourceId"
            ),
        )

        # Do raise the error again after sending the CloudFormation response:
        #  - this makes the error (and stack) visible in CloudWatch Logs
        #  - this reflects the invocation failure in CloudWatch metrics
        raise


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


# The definitions below are for typings, which are optional in Python, but can
#     be helpful during development


class ResourceProperties(TypedDict):
    BucketName: Optional[str]


class CloudFormationEvent(TypedDict):
    RequestType: Union[Literal["Create"], Literal["Update"], Literal["Delete"]]
    LogicalResourceId: str
    ResourceProperties: ResourceProperties


class CreateEvent(CloudFormationEvent):
    pass


class UpdateEvent(CloudFormationEvent):
    PhysicalResourceId: str
    OldResourceProperties: ResourceProperties


class DeleteEvent(CloudFormationEvent):
    PhysicalResourceId: str


PhysicalResourceId = str
Data = Dict[str, str]
