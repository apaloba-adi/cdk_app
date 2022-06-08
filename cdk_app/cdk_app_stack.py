from aws_cdk import (
    # Duration,
    CustomResource,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_iam as iam,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "LogBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS
        )

        s3_deploy.BucketDeployment(
            self,
            "DeployLog",
            sources=[s3_deploy.Source.asset("/Users/apaloba/Library/Application Support/Google/Chrome/", exclude=["**", "!chrome_debug.log"])],
            destination_bucket=bucket
        )

        lambda_role = iam.Role(self, "S3toLambdaRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))

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
            )],
            role=lambda_role
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid="RolePolicy",
            actions=["s3:*"],
            resources=[bucket.bucket_arn, "{}/*".format(bucket.bucket_arn)],
            effect=iam.Effect.ALLOW
        ))
        """
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="AccessPolicy",
            principals=[lambda_role, iam.AccountPrincipal(self.account)],
            actions=["s3:*"],
            effect=iam.Effect.ALLOW,
            resources=[bucket.bucket_arn, "{}/*".format(bucket.bucket_arn)]
        ))
        """