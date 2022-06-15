# Chrome Log Parsing App

### This application creates the infrastructure for
- Uploading chrome debug logs to an S3 Bucket
- Parsing debug logs via Lambda to generate a CSV File based off of log data
- Generating a bucket, workgroup, and database for Athena

### Not done from this application
- Creating table from Athena
- Visualizations done by Grafana

### Functionality Removed
- Uploading log data to DynamoDB