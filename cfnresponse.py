"""
This is a helper utility to do a HTTP PUT to the CloudFormation callback URL

Typically you invoke this utility at the end of your Lambda code,
or as soon as a (non-recoverable) error occurs in your code.

Your Lambda code should ALWAYS report back to CloudFormation,
otherwise CloudFormation will wait for 1 hour.

There are alternatives to this little utility out there on the internet,
some more full fledged in helping you write custom resources.
Have a look and see which one you like.
This one here workes well for me, I like that it doesn't have any dependencies.
"""

from urllib.request import Request, urlopen
import json


class CfnResponse:

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @staticmethod
    def send(
        event,  # the Lambda event object
        context,  # the Lambda context object
        response_status,
        reason="See CloudWatch Logs",
        response_data=None,
        physical_resource_id=None,
    ):
        response_data = response_data or {}
        response = {
            "Status": response_status,
            "Reason": reason,
            "PhysicalResourceId": physical_resource_id or context.log_stream_name,
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "Data": response_data,
        }
        urlopen(
            Request(
                event["ResponseURL"],
                data=json.dumps(response).encode(),
                headers={"content-type": ""},
                method="PUT",
            )
        )
