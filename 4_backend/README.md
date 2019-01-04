# Backend

## Prequisites

- Python 3.6
- Flask

The following Python modules need to be installed in the the `modules` directory because they have to be part of the function and cannot be installed globally in AWS:
- spacy
- PyPDF2
- python-dateutil
- pymongo

## Setup Instructions

1. Install the module dependencies locally:
```
pip install <module_name> -t ./modules
```

2. Replace the MongoDB connection setup in `lambda_function.py#30` in case a local instance is used

3. Start the development server using Flask:
```
FLASK_APP=server.py flask run
```

## Update the Function

**This part is not necessary for grading** and needs access to the AWS Account.

Use the following command to update the lambda function and send it to AWS, executed in the root directory of the repo:

```
zip -r jobApi.zip * -x ".git" \
&& aws s3 cp jobApi.zip s3://cse6242-t2-raw/application/jobApi.zip \
&& aws lambda update-function-code \
--function-name arn:aws:lambda:us-east-1:333040789555:function:jobApi \
--s3-bucket cse6242-t2-raw \
--s3-key application/jobApi.zip \
&& rm jobApi.zip
```
