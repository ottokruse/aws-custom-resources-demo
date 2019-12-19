sam validate
sam package --output-template-file packaged.yaml --s3-bucket sam.otto-aws.com
sam deploy --template-file packaged.yaml --stack-name customresources --capabilities CAPABILITY_IAM
