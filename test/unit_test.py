import unittest
import lambdawebhook.hook
import os
import json
import httpretty


def load_test_event():
    mypath = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(mypath, 'data/testevent.json'), 'r') as eventfile:
        githubevent = json.load(eventfile)
        githubevent['payload'] = json.dumps(githubevent['payload'])
    return githubevent


githubevent = load_test_event()


class VerifySignatureTestCase(unittest.TestCase):
    def runTest(self):
        # This signature is missing the 'sha1=' prefix and will fail validation
        self.assertFalse(lambdawebhook.hook.verify_signature(str(githubevent['secret']),
                                                             '952548c8f23303f4925411b09b0c5d0c13d0cfb5',
                                                             githubevent['payload']))
        # This signature should validate the payload
        self.assertTrue(lambdawebhook.hook.verify_signature(str(githubevent['secret']),
                                                            githubevent['x_hub_signature'],
                                                            githubevent['payload']))


class LambdaHandlerTestCase(unittest.TestCase):
    @httpretty.activate
    def runTest(self):
        # Check return codes
        httpretty.register_uri(httpretty.POST, 'https://localhost/github-webhook/',
                               status=200)
        self.assertEqual(lambdawebhook.hook.lambda_handler(githubevent, ''), {'status': {200: 'OK'}})

        httpretty.register_uri(httpretty.POST, 'https://localhost/github-webhook/',
                               status=403)
        self.assertEqual(lambdawebhook.hook.lambda_handler(githubevent, ''), {'status': {403: 'Forbidden'}})
