import unittest
import json
from user.status_user.app import lambda_handler

mock_body_update = {
    'body': json.dumps({
        "id_user": 5,
        "name": "John",
        "lastname": "Doe",
        "second_lastname": "Smith",
        "email": "20213tn011@utez.edu.mx",
        "phone": "1234567890",
        "password": "16=m=WAsc8WO",
        "id_rol": 2
    })
}

mock_body = {
    'body': json.dumps({
        "id_user": 4
    })
}

mock_body_status = {
    'body': json.dumps({
        "id_user": 5,
        "status": False
    })
}

class MyTestCase(unittest.TestCase):
    def test_lambda_handler(self):
        result = lambda_handler(mock_body_status, None)
        print(result)
