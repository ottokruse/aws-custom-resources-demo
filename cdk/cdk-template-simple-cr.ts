#!/usr/bin/env node

/*
This is an implementation of a custom resource using the method described here:
    https://docs.aws.amazon.com/cdk/api/latest/docs/custom-resources-readme.html

TL;DR Use this method if all you want to do is make an (1) AWS SDK call.

This is often useful when you want to enable a new AWS service feature which is not yet
supported by CloudFormation (e.g. turning on HTTPS enforcement on an ElasticSearch cluster).

The example below is just a bogus example that creates an S3 bucket (for which you would not
need a custom resource because native CloudFormation can do that).

Note that the other feature we implemented in this repo, deleting the objects in the bucket,
cannot be done using this method, as there is no corresponding AWS SDK call to do that.
*/

import "source-map-support/register";
import * as cdk from "@aws-cdk/core";
import * as cr from "@aws-cdk/custom-resources";

export class CustomS3Bucket extends cdk.Construct {
  public bucketName: string;
  public hello: string;
  public location: string;

  constructor(
    scope: cdk.Construct,
    id: string,
    props: { bucketName: string; region: string }
  ) {
    super(scope, id);

    // To figure out the "service", "action" and "parameters" to use,
    //   look up the corresponding service object name, function and parameters
    //   in the docs of the AWS JS SDK: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS.html

    const s3bucketResource = new cr.AwsCustomResource(
      scope,
      `${id}-s3-bucket-cr`,
      {
        policy: cr.AwsCustomResourcePolicy.fromSdkCalls({ resources: ["*"] }), // Let CDK infer the needed permissions from you SDK call
        onCreate: {
          service: "S3",// This is the AWS service as used in the AWS JS SDK when constructing a service interface object, e.g. as in `const s3client = new AWS.S3()`
          action: "createBucket", // This is the function you want to call, as you would in the AWS JS SDK, e.g. as in `s3client.createBucket(...)`
          parameters: {
            // These are the parameters for the function call, exactly as you would need to provide them in the AWS JS SDK
            Bucket: props.bucketName,
            CreateBucketConfiguration: {
              LocationConstraint:
                props.region !== "us-east-1" ? props.region : undefined,
            },
          },
          physicalResourceId: cr.PhysicalResourceId.of(props.bucketName),
          outputPath: "Location",
        },
        onUpdate: {
          service: "S3",
          action: "createBucket",
          parameters: {
            Bucket: props.bucketName,
            CreateBucketConfiguration: {
              LocationConstraint:
                props.region !== "us-east-1" ? props.region : undefined,
            },
          },
          physicalResourceId: cr.PhysicalResourceId.of(props.bucketName),
          outputPath: "Location",
        },
        onDelete: {
          service: "S3",
          action: "deleteBucket",
          parameters: {
            Bucket: props.bucketName,
          },
        },
      }
    );

    this.bucketName = props.bucketName;
    this.hello = "world";
    this.location = s3bucketResource.getResponseField("Location");
  }
}

export class CustomResourceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new CustomS3Bucket(this, "CustomS3Bucket", {
      bucketName: "test",
      region: "us-east-1",
    });

    new cdk.CfnOutput(this, "BucketName", {
      value: bucket.bucketName,
    });

    new cdk.CfnOutput(this, "Hello", {
      value: bucket.hello,
    });
  }
}

const app = new cdk.App();
new CustomResourceStack(app, "s3bucket");
