# Logging Simulation Application App

This application provides a test application for demonstrating an AWS Logging pipeline.

## This application includes infrastructure for
- Necessary Buckets for log and tsv storage, Athena output, and grafana queries
- Lambda Handler for Parsing
- Athena workgroup, database, and query

## To use this app
1. Clone repository
2. In `log_generation/log_generator.py`, replace the link to the bucket with a link to the bucket named LogBucket.
3. Deploy infrastructure via `cdk synth && deploy`
4. Go to Athena console and run the saved Athena query
5. Run `log_generation/log_generator.py`, run as long as desired. Enter blank statement in order to finish. Note that 
there is a 20% chance that a randomly generated error will be written to log instead of entered statement.
5. Import  `Dashboard.json` to Grafana
6. Enjoy!