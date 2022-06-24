from aws_cdk import (
    CfnTag,
    Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_iam as iam,
    aws_athena as athena,
    aws_glue as glue
)
import aws_cdk
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        start_bucket = s3.Bucket(
            self, 'LogBucket',
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        lambda_role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description='Role for giving permissions to the Parsing Lambda Script.'
        )

        parsing = _lambda.Function(
            self, 'ParsingLambda',
            code=_lambda.Code.from_asset('lambda'),
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler= 'parser.handler',
            events=[_lambda_event_sources.S3EventSource(
                start_bucket, 
                events=[s3.EventType.OBJECT_CREATED],
                filters=[s3.NotificationKeyFilter(prefix='', suffix='.log')]
            )],
            timeout=Duration.minutes(5),
            role=lambda_role
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid='S3Policy',
            actions=['s3:*'],
            resources=[start_bucket.bucket_arn, '{}/*'.format(start_bucket.bucket_arn)],
            effect=iam.Effect.ALLOW
        ))


        athena_bucket = s3.Bucket(
            self, 'AthenaTable',
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        work_group = athena.CfnWorkGroup(
            self, 'LogWorkGroup',
            name='log_work_group',
            recursive_delete_option=None,
            state='ENABLED',
            tags=[CfnTag(key='GrafanaDataSource', value='true')],
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location='s3://{}'.format(athena_bucket.bucket_name)
                )
            )
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid='AthenaPolicy',
            actions=['athena:*'],
            resources=['arn:aws:athena:{}:{}:workgroup/{}'.format(self.region, self.account, work_group.name)],
            effect=iam.Effect.ALLOW
        ))

        grafana_bucket = s3.Bucket(
            self, 'grafana-athena-query-results-test',
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid='GrafanaPolicy',
            actions=['managedgrafana:*'],
            resources=['arn:aws:athena:{}:{}:workgroup/{}'.format(self.region, self.account, work_group.name)],
            effect=iam.Effect.ALLOW
        ))

        database = glue.CfnDatabase(
            self, 'LogDatabase',
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name='log_database',
                description='Database of Chrome Log Information'
            )
        )

        table_generation = athena.CfnNamedQuery(
            self, 'TableGenerationQuery',
            database='log_database',
            query_string="CREATE EXTERNAL TABLE IF NOT EXISTS `log_database`.`log_table` (\n" +
                        "\t`date_time` timestamp,\n" +
                        "\t`err_class` string,\n" +
                        "\t`user` string,\n" +
                        "\t`char_count` int,\n" +
                        "\t`word_count` int,\n" +
                        "\t`tag` string\n" +
                        ")\nROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'\n" + 
                        "WITH SERDEPROPERTIES (\n" +
                            "\t'serialization.format' = '	',\n"+
                            "\t'field.delim' = '	'\n" +
                        ") LOCATION -- Insert Bucket Name in quotes\n" + #In Athena, update with correct bucket name once deployed
                         "TBLPROPERTIES ('has_encrypted_data'='false');\n",
            name='table_generation',
            description='Query to generate table. Only needs to be run once unless you change table format.',
            work_group=work_group.name
        )

        bucket_arn = aws_cdk.CfnOutput(
            self, 'Output',
            value=start_bucket.bucket_arn
        )