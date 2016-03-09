#!/usr/bin/env python
import os
import sys
import hashlib

# Add the lib directory to the path for Lambda to load our libs
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import requests  # NOQA
import hmac  # NOQA


def verify_signature(secret, signature, payload):
    computed_hash = hmac.new(str(secret), payload, hashlib.sha1)
    computed_signature = '='.join(['sha1', computed_hash.hexdigest()])
    return hmac.compare_digest(computed_signature, str(signature))


def lambda_handler(event, context):
    print 'Webhook received'
    verified = verify_signature(event['secret'],
                                event['x_hub_signature'],
                                event['payload'])
    print 'Signature verified: ' + str(verified)
    if verified:
        response = requests.post(event['jenkins_url'],
                                 headers={
                                    'Content-Type': 'application/json',
                                    'X-GitHub-Delivery': event['x_github_delivery'],
                                    'X-GitHub-Event': event['x_github_event'],
                                    'X-Hub-Signature':  event['x_hub_signature']
                                 },
                                 data=event['payload'])
        response.raise_for_status()
    else:
        raise requests.HTTPError('400 Client Error: Bad Request')


if __name__ == "__main__":
    pass