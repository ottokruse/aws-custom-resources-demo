# CDK Examples

This folder contains CDK examples, to show how to use a Custom resource in CDK.

- [./cdk-template.ts](./cdk-template.ts): this CDK template includes our custom resource ([../lambda-handler](../lambda-handler)) and is equivalent with the CloudFormation [template](../cloudformation/template.yaml) in this repo.
- [./cdk-template-simple-cr.ts](./cdk-template-simple-cr.ts): this CDK template does not use our custom resource but rather a CDK-specific mechanism that is more simple (but more limited too)
