"""
This is a helper utility to send responses to the CloudFormation callback URL.

If you're looking for a NodeJS variant, here's one:
    https://gist.github.com/ottokruse/f08099eea65412f7376525d5d1cd968b

Typically you invoke this utility at the end of your Custom Resource Lambda code,
    or as soon as a (non-recoverable) error occurs in your code.

Your Lambda code should ALWAYS report back to CloudFormation,
    otherwise CloudFormation will wait for 1 hour in vain.

This utility is an alternative to the bundled one:
    https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html

I rather use this utility instead of the bundled one because:

  - The bundled cfn-response module is available only when you use the ZipFile property
    to write your source code. It isn't available for source code that's stored in
    Amazon S3 buckets (like SAM packaged Lambda code).

  - The bundled cfn-response module does not allow you to provide a custom error
    message, but instead always refers to CloudWatch logs. I like to have my error
    message visible in the CloudFormation events tab, without having to search for
    it in CloudWatch logs.
"""

__all__ = ("CfnResponse",)

from urllib.request import Request, urlopen
import json
from typing import Union, Dict, Literal, Optional


class CfnResponse:
    """Helper class to send a response to the CloudFormation callback URL.
    
    Attributes:
        SUCCESS (str): constant to indicate success to CloudFormation
        FAILED (str): constant to indicate failure to CloudFormation
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @staticmethod
    def send(
        event,
        context,
        response_status: Union[Literal["SUCCESS"], Literal["FAILED"]],
        reason: Optional[str] = "See CloudWatch Logs",
        response_data: Optional[Dict[str, str]] = None,
        physical_resource_id: Optional[str] = None,
    ):
        """Use send() to send the response back to CloudFormation,
        indicating that your Custom Resource code is "done": it has
        either deployed the Custom Resource or it failed.

        Args:
            event (obj): the Lambda handler invocation's event object
            context (obj): the Lambda handler invocation's context object
            response_status (str): SUCCESS or FAILED. To help you remember the exact
                string you can also use CfnResponse.SUCCESS or CfnResponse.FAILED
            reason (str): your custom error message in case of response_status FAILED
            response_data (dict): dictionary with key-value pairs that you can !GetAtt
                in your CloudFormation template
            physical_resource_id (str): the physical resource id of your Custom Resource.
                This is an important field that you probaby want to specify explicitly.
                If you change the value of this field during a CloudFormation Update,
                CloudFormation will issue a Delete against the previous value.
        """

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
