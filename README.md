# AWS Custom Resources demo

This repo contains several examples of [custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html).

## So what is a custom resource?

When you want to do something in AWS CloudFormation that isn't supported out-of-the-box you write a custom resource to do it yourself.

Examples:

- You want to include in your stack an AWS service that has no CloudFormation support yet at all
- You want to include in your stack an AWS service that does have CloudFormation support, but it doesn't support the latest services features that are supported by the service API (and SDK's)
- Upon deploying you cloudformation stack, you want to run some custom logic in a Lambda function
