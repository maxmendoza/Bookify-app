import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.change_password.app import lambda_handler, handle_response  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoChangePassword(unittest.TestCase):

    @patch('cognito.change_password.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client):
        # Configuración del mock para Cognito
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Evento simulado con un email válido
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'],
                         'Password reset initiated. Check your email for the verification code.')

        # Verificar que se llamó a Cognito con los parámetros correctos
        mock_cognito_client.forgot_password.assert_called_once_with(
            ClientId=os.getenv('CLIENT_ID'),
            Username='user@example.com'
        )

    @patch('cognito.change_password.app.boto3.client')
    def test_lambda_handler_missing_email(self, mock_boto_client):
        # Evento simulado sin email
        mock_event = {
            'body': json.dumps({})
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'Invalid input')
        self.assertEqual(json.loads(response['body'])['error'], 'Missing email')

    @patch('cognito.change_password.app.boto3.client')
    def test_lambda_handler_cognito_exception(self, mock_boto_client):
        # Configuración del mock para que Cognito lance una excepción
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client
        mock_cognito_client.forgot_password.side_effect = ClientError(
            error_response={'Error': {'Code': 'UserNotFoundException', 'Message': 'User not found'}},
            operation_name='ForgotPassword'
        )

        # Evento simulado con un email válido
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error initiating forgot password', json.loads(response['body'])['message'])
        self.assertIn('UserNotFoundException', json.loads(response['body'])['error'])

if __name__ == '__main__':
    unittest.main()
