from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    aws_s3_deployment as s3_deploy
)
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "LogBucket", versioned=True, block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        s3_deploy.BucketDeployment(self, "DeployLog",
            sources=[s3_deploy.Source.asset("/Users/apaloba/Library/Application Support/Google/Chrome/", exclude=["**", "!chrome_debug.log"])],
            destination_bucket=bucket)