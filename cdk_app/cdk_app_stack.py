from sys import prefix
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    aws_s3_deployment as s3_deploy,
    aws_s3_notifications as s3_notifs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources
)
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "LogBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        s3_deploy.BucketDeployment(
            self,
            "DeployLog",
            sources=[s3_deploy.Source.asset("/Users/apaloba/Library/Application Support/Google/Chrome/", exclude=["**", "!chrome_debug.log"])],
            destination_bucket=bucket
        )

        parsing = _lambda.Function(
            self,
            "ParsingLambda",
            code=_lambda.Code.from_asset("lambda"),
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler= "parser.handler",
            events=[_lambda_event_sources.S3EventSource(
                bucket, 
                events=[s3.EventType.OBJECT_CREATED],
                filters=[s3.NotificationKeyFilter(prefix="", suffix=".log")]
            )]
        )

        bucket.grant_read(parsing)