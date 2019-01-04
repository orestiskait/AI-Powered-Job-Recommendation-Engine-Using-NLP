# Spark

This repository contains all the information and code necessary to achieve the preprocessing of the job data on S3 using Spark on Amazon EMR.

**Note:** Make sure to use python `v3.4.x` since this version is running on EMR.

## Prequisites

- Python 3.4 (!)
- boto3
- spacy
- Spark 2.3.2 with hadoop 2.7
- AWS SDK in classpath

## Spark Application

The `process.py` is built as a Spark application that can be deployed on Amazon EMR. The third party dependencies (Python modules) that are used in this script have to be installed in `bootstrap.sh` that is executed in the bootstrap process of the cluster and bootstraps each instance.

The two files mentioned above need to be copied to the respective S3 bucket under:
```
s3://cse6242-t2-raw/application
```

## Create a Cluster

The following command creates a cluster and adds a step to execute `process.py`. The cluster spins up and terminates automatically after the job is done. The `step.json` file contains the configuration of the application that is run, thus `process.py`. The `cluster_config.json` file contains further config for the cluster that is created.

```
aws emr create-cluster \
--name "Job Processing Cluster" \
--ec2-attributes KeyName=EC2 \
--use-default-roles --release-label emr-5.19.0 --applications Name=Spark \
--instance-type c5.xlarge --instance-count 20 --configurations file://./cluster_config.json \
--bootstrap-actions Path=s3://cse6242-t2-raw/application/bootstrap.sh,Args=[] \
--steps file://./step.json --auto-terminate
```
