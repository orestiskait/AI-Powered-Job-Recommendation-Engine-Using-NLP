# AI-Powered-Job-Recommendation-Engine-Using-NLP

## ./1_utils

This package contains utilities created in Python to handle datasets and convert the data into various formats as well as SQL code used to process and inspect data in Amazon Athena. The Python utilities to e.g. convert our job descriptions to the format required by Prodigy or extract the text out of PDF files in order to be able to annotate the resumes.

## ./2_scraper

Contains the Scrapy code used to scrape the job postings from Glassdoor.

## ./3_spark

Spark application for Amazon EMR used to apply the NLP code and some other processing steps on the raw data fetched from Glassdoor and produce the processed dataset which was loaded into MongoDB.

## ./4_backend

AWS Lambda function written in Python which sits behind AWS Api Gateway and provides the data API for the frondend.

## ./5_frontend

Vue web application which is deployed to Amazon S3 and accessed through Amazon Cloudfront.
