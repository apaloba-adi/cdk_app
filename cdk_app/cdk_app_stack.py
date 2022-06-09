from aws_cdk import (
    # Duration,
    CustomResource,
    Duration,
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
            self, "LogBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS
        )

        s3_deploy.BucketDeployment(
            self, "DeployLog",
            sources=[s3_deploy.Source.asset("/Users/apaloba/Library/Application Support/Google/Chrome/", exclude=["**", "!chrome_debug.log"])],
            destination_bucket=bucket
        )

        parsing_role = iam.Role(self, "S3toLambdatoDynamoDB", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))

        parsing = _lambda.Function(
            self, "ParsingLambda",
            code=_lambda.Code.from_asset("lambda"),
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler= "parser.handler",
            events=[_lambda_event_sources.S3EventSource(
                bucket, 
                events=[s3.EventType.OBJECT_CREATED],
                filters=[s3.NotificationKeyFilter(prefix="", suffix=".log")]
            )],
            timeout=Duration.minutes(5),
            role=parsing_role
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid="S3Policy",
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

        #process_id = dynamodb.Attribute(name="ProcessID", type=dynamodb.AttributeType.NUMBER)
        #thread_id = dynamodb.Attribute(name="ThreadID", type=dynamodb.AttributeType.NUMBER)
        date = dynamodb.Attribute(name="Date", type=dynamodb.AttributeType.STRING)
        time = dynamodb.Attribute(name="Time", type=dynamodb.AttributeType.STRING)
        #logging_level = dynamodb.Attribute(name="LoggingLevel", type=dynamodb.AttributeType.STRING)
        source_code = dynamodb.Attribute(name="Source-Code File", type=dynamodb.AttributeType.STRING)
        line_number = dynamodb.Attribute(name="Line Number",type=dynamodb.AttributeType.NUMBER)

        table = dynamodb.Table(
            self, "LogItems",
            partition_key=source_code,
            sort_key=line_number,
            billing_mode=dynamodb.BillingMode.PROVISIONED
        )

        table.add_global_secondary_index(
            index_name="Date-Time",
            partition_key=date,
            sort_key=time
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid="DynamoDBPolicy",
            actions=["dynamodb:*"],
            resources=[table.table_arn, "{}/*".format(table.table_arn)],
            effect=iam.Effect.ALLOW
        ))