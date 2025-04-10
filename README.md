**Description**:

This project is a POC demonstrating how to build and deploy a serverless FastAPI application using SST and AWS Lambda.

✅ Features

- FastAPI CRUD Operations – Create, read, update, and delete data using FastAPI.
- DynamoDB Integration – Store and retrieve data with Amazon DynamoDB.
- Serverless Deployment – Deploys the application to AWS Lambda.
- Infrastructure as Code – Uses SST to define and manage cloud infrastructure.

**Prerequisites**:
- Python installed
- AWS credentials configured to work with SST

To run this project locally and to do live Lambda debugging
```
npx sst dev
```
To deploy the changes to Lambda
```
npx sst deploy
```
To remove the deployed resources from AWS
```
npx sst remove
```
**Note:**

Once the changes are deployed to Lambda using SST, a url will be generated where we can access application related endpoints.
```
Check <lambda-url>/docs for endpoint details.
```