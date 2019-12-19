from urllib.request import Request, urlopen
import json


class CfnResponse:

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @staticmethod
    def send(
        event,
        context,
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
