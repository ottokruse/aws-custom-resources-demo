# AWS Custom Resources demo

This repo contains an example of an AWS CloudFormation [custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) to showcase how to build them.

## So what is a custom resource?

Read the official docs (link above).

__TL;DR__ When you want to do something in AWS CloudFormation that isn't supported out-of-the-box you write a custom resource and code it yourself.

In your code, the implementation of the custom resource, you typically call into AWS API's (using the SDK) or do whatever else you want.

Examples of when to do this:

- You want to include in your stack an AWS service that has no CloudFormation support yet

- You want to include in your stack an AWS service that does have CloudFormation support, but it doesn't support the latest features that are supported by the service API (and SDK's)

- You want to include in your stack a non-AWS component, maybe even one that should be deployed on-premise. For tracking purposes you like it to be part of the stack in AWS

- Upon deploying your cloudformation stack, you want to run some custom logic

## The example

To showcase how custom resources are built, we'll demonstrate the implementation of a custom resource that deploys an S3 bucket. Not just a normal S3 bucket (because you can do that with CloudFormation natively) but an S3 bucket that can be deleted by CloudFormation, even if it has objects in it. This is nice because when you delete a CloudFormation stack you often want the S3 buckets inside it to be deleted also, even if they contain objects. The native CloudFormation S3 resource "protects you" from doing this. That is probably wise in the general case, but if you know what you are doing it can be really annoying! So let's build a custom resource that will not protect us from ourselves.

- [lambda-handler](./lambda-handler): this is the implementation of the Custom Resource Lambda function (in Python)

- [cloudformation](./cloudformation): this shows how to include the Custom Resource in a CloudFormation (/SAM) template

- [cdk](./cdk): this shows how to include the Custom Resource in a CDK app

## Implementing an AWS CloudFormation Custom Resource

There are several ways to implement a Custom Resource:

- You code a Lambda Function that will be invoked by CloudFormation, when performing Stack creates/updates/deletes. This mechanism is showcased in this repository and is probably the easiest way to create CloudFormation resources. Several libraries out can help you code such Lambda's (although once you understand it you'll find it is quite simple).

- You provide an SNS topic that CloudFormation will send messages to, when performing Stack creates/updates/deletes. You need to subscribe to this SNS topic and react accordingly. Using SNS opens up a lot of possibilities, like e.g. listening to such messages using an on-premise process, for creating on-premise resources. This mechanism is not showcased in this repo.

- Use the [CloudFormation Provider Development Toolkit](https://github.com/aws-cloudformation/cloudformation-cli) and [register your custom resource provider](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/resource-type-register.html) to the [CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html). This is a way more elaborate approach than using a simple Lambda, but has the benefit of being able to make your Custom Resource available for re-use by others. __TODO__: provide example - will accept __PR's__ :)

### Libraries and frameworks to help you develop Custom Resources

The following is a list of libraries and frameworks to help you develop custom resources.

(Confession: I usually write Custom Resources without such libraries and frameworks; because I'm comfortable doing it the "plain" way as demo-ed in this repo, and like to avoid extra layers.)

- [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/latest/guide/home.html) includes a "mini-framework" for implementing providers for AWS CloudFormation custom resources: [CDK custom-resources module](https://docs.aws.amazon.com/cdk/api/latest/docs/custom-resources-readme.html)

- [cfn-custom-resource](https://pypi.org/project/cfn-custom-resource/) is a Python library that makes it a easier to write the Lambda code to implement a Custom Respource.

- ... __TODO__: mention other relevant ones
