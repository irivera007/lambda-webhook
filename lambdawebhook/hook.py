#!/usr/bin/env python
import os
import sys
import hashlib

# Add the ./site-packages directory to the path for Lambda to load our libs
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import requests  # NOQA
import hmac  # NOQA


def verify_signature(secret, signature, payload):
    computed_hash = hmac.new(str(secret), payload, hashlib.sha1)
    computed_signature = '='.join(['sha1', computed_hash.hexdigest()])
    return hmac.compare_digest(computed_signature, str(signature))


def lambda_handler(event, context):
    print 'Webhook received'
    print event['secret']
    verified = verify_signature(event['secret'],
                                event['x_hub_signature'],
                                event['payload'])
    print 'Signature verified: ' + str(verified)
    if verified:
        response = requests.post(event['jenkins_url'],
                                 headers={
                                    'X-GitHub-Delivery': event['x_github_delivery'],
                                    'X-GitHub-Event': event['x_github_event'],
                                    'X-Hub-Signature':  event['x_hub_signature']
                                 },
                                 json=event['payload'])
        return {'status': {response.status_code: response.reason}}
    else:
        return {'status': {403: 'Forbidden'}}


if __name__ == "__main__":
    pass
