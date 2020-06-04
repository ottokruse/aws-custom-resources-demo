# AWS Custom Resources demo

This repo contains several examples of [custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html).

## So what is a custom resource?

Read the official docs (link above).

__TL;DR__ When you want to do something in AWS CloudFormation that isn't supported out-of-the-box you write a custom resource and code it yourself. In your code, the implementation of the custom resource, you can call into AWS API's (using the SDK) or do whatever else you want.

Examples:

- You want to include in your stack an AWS service that has no CloudFormation support yet
- You want to include in your stack an AWS service that does have CloudFormation support, but it doesn't support the latest services features that are supported by the service API (and SDK's)
- Upon deploying your cloudformation stack, you want to run some custom logic in a Lambda function
