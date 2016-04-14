# lambda-webhook

An AWS Lambda function to receive GitHub webhooks from API gateway and relay them to an EC2 instance.


## Usage

1. Create a Security Group for the Lambda function
  - Inbound: None
  - Outbound: Only allow HTTPS/HTTP to the receiving instance

1. Create a Lambda function:
  - Runtime: Python 2.7
  - Handler: hook.lambda_handler
  - Role: Basic With VPC
  - Memory: 128MB
  - Timeout: 30sec
  - VPC: The VPC of the receiving instance
  - Subnets: At least 2 private subnets within the VPC
  - Security Groups: The Security Group configured previously

1. Install dependencies locally:

  `$ pip install -r requirements.txt -t lambdawebhook/lib/`

1. Create a ZIP archive of the `lambdawebhook` directory:

  `$ cd lambdawebhook`
  `$ zip -r lambdawebhook.zip *`

1. Upload the zipped code to the Lambda function created previously

1. Create an API in API gateway

1. Create a resource for `/github`

1. Create a POST method for `/github`
  - Integration type: Lambda Function
  - Lambda Region: The region of the Lamba function created previously
  - Lambda Function: The Lambda function created previously

1. Integration Request -> Mapping Templates:
  - Content-Type: `application/json`
  - Mapping Template (replace `secret` and `jenkins_url` as appropriate for your configuration):

          {
              "x_github_delivery": "$util.escapeJavaScript($input.params().header.get('X-GitHub-Delivery'))",
              "x_github_event": "$util.escapeJavaScript($input.params().header.get('X-GitHub-Event'))",
              "x_hub_signature": "$util.escapeJavaScript($input.params().header.get('X-Hub-Signature'))",
              "secret": "some_secret",
              "jenkins_url": "https://jenkins/github-webhook/",
              "payload": "$util.base64Encode($input.body)"
          }

1. Method Response:
  - HTTP Status: `400`

1. Integration Response -> Add integration response:
  - Lambda Error Regex: `400 Client Error: Bad Request`
  - Method response status: `400`
  - Mapping Templates:
    - Content-Type: `application/json`
    - Template:

            {
                "message": $input.json('$.errorMessage')
            }

1. Deploy API

1. Configure the webhook and secret for the GitHub repository using the API URL provided in the previous step, and `secret` set above.

1. Test by pushing some code to the repository.

## Development

Linting (flake8) and testing (unittest) are executed using `tox` in the root directory of this repository:

    $ pip install tox
    $ tox
