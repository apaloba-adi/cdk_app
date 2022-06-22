# Logging Simulation Application App

This application provides a test application for demonstrating an AWS Logging pipeline.

## This application includes infrastructure for
- Necessary Buckets for log and tsv storage, Athena output, and grafana queries
- Lambda Handler for Parsing
- Athena workgroup, database, and query

## To use this app
1. Clone repository
2. Deploy infrastructure via `cdk synth && deplot`