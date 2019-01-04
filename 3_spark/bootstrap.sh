#!/bin/bash -xe
sudo pip-3.4 install boto3 spacy

aws s3 cp --recursive s3://cse6242-t2-raw/application/job_degree /tmp/job_degree
aws s3 cp --recursive s3://cse6242-t2-raw/application/job_experience /tmp/job_experience
aws s3 cp --recursive s3://cse6242-t2-raw/application/job_skill /tmp/job_skill

sudo python3 -m spacy download en_core_web_sm
