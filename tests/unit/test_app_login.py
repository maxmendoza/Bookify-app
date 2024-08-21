import unittest
from unittest.mock import patch
from cognito.forgot_password.app import lambda_handler
import json

mock_body = {
    'body': json.dumps({
        'email': '20213tn011@utez.edu.mx',
    })
}


class MyTestCase(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(mock_body, None)
        print(result)
