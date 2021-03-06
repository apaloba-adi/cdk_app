# Logging Simulation Application App

This application provides a test application for demonstrating an AWS Logging pipeline. It takes text input from `log_generation/log_generator.py`, and uploads logs from input straight to Grafana. These logs generate information you might find in general log files, including a randomly generated user. In order to simulate an entry with errors, there is a 1/25 chance of generating a randomly selected error. 

## This application includes infrastructure for
- Necessary Buckets for log and tsv storage, Athena output, and grafana queries
- Lambda Handler for Parsing
- Athena workgroup, database, and query

## To use this app for the first time
1. Clone repository 
2. Deploy infrastructure via `cdk synth && cdk deploy --outputs-file outputs.txt`
3. Go to Athena console and run the saved Athena query, insert bucket name with generated full 'LogBucket' name (found in outputs.txt).
4. Run `log_generation/log_generator.py`, input as many statements as desired. Enter blank statement in order to finish.
5. Import `Dashboard.json` to Grafana
6. Enjoy!

### To use this app after, simply repeat step 4