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

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid='AthenaPolicy',
            actions=['athena:*'],
            resources=['arn:aws:athena:us-east-1:051270296548:workgroup/log_work_group'],
            effect=iam.Effect.ALLOW
        ))

        '''
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid='AccessPolicy',
            principals=[lambda_role, iam.AccountPrincipal(self.account)],
            actions=['s3:*'],
            effect=iam.Effect.ALLOW,
            resources=[bucket.bucket_arn, '{}/*'.format(bucket.bucket_arn)]
        ))
        

        #process_id = dynamodb.Attribute(name='ProcessID', type=dynamodb.AttributeType.NUMBER)
        #thread_id = dynamodb.Attribute(name='ThreadID', type=dynamodb.AttributeType.NUMBER)
        date = dynamodb.Attribute(name='Date', type=dynamodb.AttributeType.STRING)
        time = dynamodb.Attribute(name='Time', type=dynamodb.AttributeType.STRING)
        #logging_level = dynamodb.Attribute(name='LoggingLevel', type=dynamodb.AttributeType.STRING)
        source_code = dynamodb.Attribute(name='Source-Code File', type=dynamodb.AttributeType.STRING)
        line_number = dynamodb.Attribute(name='Line Number',type=dynamodb.AttributeType.NUMBER)
        tag = dynamodb.Attribute(name='Tag', type=dynamodb.AttributeType.STRING)

        table = dynamodb.Table(
            self, 'LogItems',
            partition_key=tag,
            sort_key=date,
            billing_mode=dynamodb.BillingMode.PROVISIONED
        )

        table.add_global_secondary_index(
            index_name='Date_Time',
            partition_key=date,
            sort_key=time
        )

        table.add_global_secondary_index(
            index_name='Source-Code_Line-Number',
            partition_key=source_code,
            sort_key=line_number
        )

        parsing.add_to_role_policy(iam.PolicyStatement(
            sid='DynamoDBPolicy',
            actions=['dynamodb:*'],
            resources=[table.table_arn, '{}/*'.format(table.table_arn)],
            effect=iam.Effect.ALLOW
        ))

        '''

        athena_bucket = s3.Bucket(
            self, 'AthenaTable',
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        grafana_bucket = s3.Bucket(
            self, 'grafana-athena-query-results-test',
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
            sid='GrafanaPolicy',
            actions=['managedgrafana:*'],
            resources=['arn:aws:athena:us-east-1:051270296548:workgroup/{}'.format(work_group.name)],
            effect=iam.Effect.ALLOW
        ))

        database = glue.CfnDatabase(
            self, 'LogDatabase',
            catalog_id='051270296548',
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
                        "\t`user` string\n" +
                        "\t`char_count` int,\n" +
                        "\t`word_count` int,\n" +
                        ")\nROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'\n" + 
                        "WITH SERDEPROPERTIES (\n" +
                            "\t'serialization.format' = '	',\n"+
                            "\t'field.delim' = '	'\n" +
                        ") LOCATION 's3://cdkappstack-logbucketcc3b17e8-1ms8j0ohr6djo/'\n" +
                         "TBLPROPERTIES ('has_encrypted_data'='false');\n",
            name='table_generation',
            work_group=work_group.name
        )