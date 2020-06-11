# Implementation of an AWS CloudFormation Custom Resource in AWS Lambda

The code in this folder demonstrates how you can implement a Custom Resource.

- [./main.py](./main.py): the implementation of the Custom Resource by a Lambda function

- [./cfnresponse.py](./cfnresponse.py): helper utility to send responses to the CloudFormation callback URL

## Outline: creating a Custom Resource in AWS Lambda

You code a Lambda function:

- Your handler will receive events from CloudFormation
- The event will contain (a.o.):
  - Request type: Create / Update / Delete
  - Parameters: you provide these in your CloudFormation template (optional)
  - Callback URL: you need to HTTP PUT to this, at the end of your code
- Your handler does what it needs to do (call API's, do whatever)
- Your handler does the HTTP PUT to the callback URL to signal to CloudFormation that it is done (SUCCES / FAILED)
