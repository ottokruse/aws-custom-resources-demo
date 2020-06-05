# AWS Custom Resources demo

This repo contains several examples of [custom resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) to showcase how to build them.

## So what is a custom resource?

Read the official docs (link above).

__TL;DR__ When you want to do something in AWS CloudFormation that isn't supported out-of-the-box you write a custom resource and code it yourself.

In your code, the implementation of the custom resource, you typically call into AWS API's (using the SDK) or do whatever else you want.

Examples of when to do this:

- You want to include in your stack an AWS service that has no CloudFormation support yet
- You want to include in your stack an AWS service that does have CloudFormation support, but it doesn't support the latest services features that are supported by the service API (and SDK's)
- Upon deploying your cloudformation stack, you want to run some custom logic in a Lambda function

## The examples

To showcase how custom resources are built, we'll demonstrate the implementation of a custom resource that deploys an S3 bucket. Not just a normal S3 bucket (because you can do that with CloudFormation natively) but an S3 bucket that can be deleted by CloudFormation, even if it has objects in it. This is nice because when you delete a CloudFormation stack you often want the S3 buckets inside it to be deleted also, even if they contain objects. The native CloudFormation S3 resource "protects you" from doing this. That is probably wise in the general case, but if you know what you are doing it can be really annoying! So let's build a custom resource that will not protect us from ourselves.

The examples build up (if you just want to see a good example, pick the last one):

- s3bucket_simple: naive implementation that does not utilize CloudFormation functionality around "Physical Resource ID"
- s3bucket_simple_with_output: same implementation as `s3bucket_simple`, but shows how you can give outputs to your custom resource (that you can !GetAtt in your CloudFormation template)
- s3bucket: proper example that uses "Physical Resource ID" to let CloudFormation handle deletes for you, if you change the BucketName input parameter
- s3bucket_random: same implementation as `s3bucket`, but will generate a bucket name itself, if not provided explicitly.


## High level way of implementing

You code a Lambda:

- Your handler will receives events from CloudFormation
- The event will contain (a.o.):
  - type: Create / Update / Delete
  - parameters: you provide these in your CloudFormation template (optional)
  - callback URL: you need to HTTP PUT to this, at then end of your code
- Your handler does what it needs to do (call API's, do whatever)
- Your handler does the HTTP PUT to the callback URL to signal to CloudFormation that it is done (SUCCES / FAILED)

You can also use SNS instead of Lambda, but that is not covered in this repo.