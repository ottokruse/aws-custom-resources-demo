#!/usr/bin/env node

import "source-map-support/register";
import cdk = require("@aws-cdk/core");
import lambda = require("@aws-cdk/aws-lambda");
import cfn = require("@aws-cdk/aws-cloudformation");
import iam = require("@aws-cdk/aws-iam");
import path = require("path");

export class CustomS3Bucket extends cdk.Construct {
  public bucketName: string;
  public hello: string;

  constructor(scope: cdk.Construct, id: string, props: { bucketName: string }) {
    super(scope, id);

    const lambdaHandler = new lambda.SingletonFunction(
      this,
      "CustomS3BucketHandler",
      {
        uuid: "cdk-custom-resource-handler",
        lambdaPurpose: "cdk-custom-resource-handler",
        code: new lambda.AssetCode(path.join(__dirname, "..", "lambda-handler")),
        handler: "main.handler",
        runtime: lambda.Runtime.PYTHON_3_8,
        timeout: cdk.Duration.seconds(30),
      }
    );

    lambdaHandler.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["s3:*"],
        effect: iam.Effect.ALLOW,
        resources: ["*"],
      })
    );

    const resource = new cfn.CustomResource(this, `${id}-s3-bucket`, {
      provider: cfn.CustomResourceProvider.fromLambda(lambdaHandler),
      resourceType: "Custom::S3Bucket", // Invent your own resource type, just start with Custom::
      properties: {
        BucketName: props.bucketName,
      },
    });

    this.bucketName = resource.getAtt("MyBucketName").toString();
    this.hello = resource.getAtt("Hello").toString();
  }
}

export class CustomResourceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new CustomS3Bucket(this, "CustomS3Bucket", { bucketName: "test-cr.otto-aws.com" });

    new cdk.CfnOutput(this, 'BucketName', {
      value: bucket.bucketName
    });

    new cdk.CfnOutput(this, 'Hello', {
      value: bucket.hello
    });
  }
}

const app = new cdk.App();
new CustomResourceStack(app, "s3bucket");
