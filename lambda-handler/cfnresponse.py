"""
This is a helper utility to send responses to the CloudFormation callback URL.

Typically you invoke this utility at the end of your Custom Resource Lambda code,
    or as soon as a (non-recoverable) error occurs in your code.

Your Lambda code should ALWAYS report back to CloudFormation,
    otherwise CloudFormation will wait for 1 hour in vain.

There are alternatives to this little utility out there:

    - there's the bundled one which I don't really like, because it does not allow you to provide
          a custom error message: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
    - Other example are more full fledged in helping you write custom resources,
          e.g. https://pypi.org/project/cfn-custom-resource/

The utility file you're looking at now works well enough for me:

    - It allows you to use a custom error message that will be
        visible in CloudFormation events tab
    - It doesn't have any dependencies beyond stdlib
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
        reason: str = "See CloudWatch Logs",
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
