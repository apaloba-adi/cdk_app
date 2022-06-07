from email.policy import Policy
from sys import prefix
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_iam as iam
)
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "LogBucket",
            versioned=True
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

        bucket.grant_read_write(parsing)

        role = iam.Role(self, "S3AccessRole", assumed_by=iam.ServicePrincipal("s3.amazonaws.com"))

        bucket.add_to_resource_policy(iam.PolicyStatement(
            principals=[role],
            actions=["s3:PutBucketPolicy", "s3:GetObject", "s3:GetObjectAttributes"],
            effect=iam.Effect.ALLOW,
            resources=[bucket.bucket_arn, "{}/*".format(bucket.bucket_arn)]
        ))