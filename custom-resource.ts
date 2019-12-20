#!/usr/bin/env node
import "source-map-support/register";
import cdk = require("@aws-cdk/core");
import s3 = require("@aws-cdk/aws-s3");
import s3d = require("@aws-cdk/aws-s3-deployment");
import lambda = require("@aws-cdk/aws-lambda");
import cfn = require("@aws-cdk/aws-cloudformation");
import iam = require("@aws-cdk/aws-iam");
import path = require("path");
import cr = require("@aws-cdk/custom-resources");

export class CustomS3Bucket extends cdk.Construct {
  public bucketName: string;

  constructor(scope: cdk.Construct, id: string) {
    super(scope, id);

    const lambdaHandler = new lambda.SingletonFunction(this, `${id}-handler`, {
      uuid: "cdk-custom-resource-handler",
      lambdaPurpose: "cdk-custom-resource-handler",
      code: new lambda.AssetCode(path.join(__dirname, "s3bucket_random")),
      handler: "main.handler",
      runtime: lambda.Runtime.PYTHON_3_8,
      timeout: cdk.Duration.seconds(30),
      functionName: `${
        cdk.Stack.of(this).stackName
      }-cdk-custom-resource-handler`
    });

    lambdaHandler.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["s3:*"],
        effect: iam.Effect.ALLOW,
        resources: ["*"]
      })
    );

    const resource = new cfn.CustomResource(this, `${id}-s3-bucket`, {
      provider: cfn.CustomResourceProvider.fromLambda(lambdaHandler),
      resourceType: "Custom::S3BucketWithRandomName",
      properties: {
        Dummy: "dummy"
      }
    });

    this.bucketName = resource.getAtt("MyBucketName").toString();
  }
}

export class CustomS3BucketSimple extends cdk.Construct {
  constructor(scope: cdk.Construct, id: string) {
    super(scope, id);

    const bucketName = "simple-custom-resource.otto-aws.com";

    new cr.AwsCustomResource(this, `${id}-simple-custom-resource`, {
      onCreate: {
        service: "S3",
        action: "createBucket",
        parameters: {
          Bucket: bucketName
        },
        physicalResourceId: bucketName,
      },
      onDelete: {
        service: "S3",
        action: "deleteBucket",
        parameters: {
          Bucket: bucketName
        },
        physicalResourceId: bucketName,
      }
    });
  }
}

export class CustomResourceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const customBucket = new CustomS3Bucket(this, "my-custom-s3-bucket");
    const customS3Bucket = s3.Bucket.fromBucketName(
      this,
      "bucket-ref",
      customBucket.bucketName
    );
    const normalS3Bucket = new s3.Bucket(this, "normal-bucket", {
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    [customS3Bucket, normalS3Bucket].forEach((bucket, index) => {
      new s3d.BucketDeployment(this, `s3-upload-${index}`, {
        destinationBucket: bucket,
        sources: [s3d.Source.asset(path.join(__dirname, "s3bucket_random"))]
      });
    });

    new CustomS3BucketSimple(this, 'simple-custom-resource-s3');
  }
}

const app = new cdk.App();
new CustomResourceStack(app, "custom-resource-cdk-demo");
