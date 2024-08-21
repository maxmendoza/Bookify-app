import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.forgot_password.app import lambda_handler  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoForgotPassword(unittest.TestCase):

    @patch('cognito.forgot_password.app.get_secret')
    @patch('cognito.forgot_password.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_get_secret):
        # Configuración de los mocks
        mock_get_secret.return_value = {'client_id': 'test_client_id', 'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Simular respuesta de admin_get_user
        mock_cognito_client.admin_get_user.return_value = {
            'UserAttributes': [
                {'Name': 'email_verified', 'Value': 'true'}
            ]
        }

        # Evento simulado con email
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Código de confirmación enviado al correo electrónico", json.loads(response['body'])['message'])

        # Verificar que se llamó a admin_get_user con los parámetros correctos
        mock_cognito_client.admin_get_user.assert_called_once_with(
            UserPoolId='test_user_pool_id',
            Username='user@example.com'
        )

        # Verificar que se llamó a forgot_password con los parámetros correctos
        mock_cognito_client.forgot_password.assert_called_once_with(
            ClientId='test_client_id',
            Username='user@example.com'
        )

    @patch('cognito.forgot_password.app.boto3.client')
    def test_lambda_handler_invalid_json(self, mock_boto_client):
        # Evento simulado con JSON inválido
        mock_event = {
            'body': "invalid-json"
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid JSON format in request body", json.loads(response['body'])['error_message'])

    @patch('cognito.forgot_password.app.get_secret')
    @patch('cognito.forgot_password.app.boto3.client')
    def test_lambda_handler_email_not_verified(self, mock_boto_client, mock_get_secret):
        # Configuración de los mocks
        mock_get_secret.return_value = {'client_id': 'test_client_id', 'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Simular respuesta de admin_get_user con email no verificado
        mock_cognito_client.admin_get_user.return_value = {
            'UserAttributes': [
                {'Name': 'email_verified', 'Value': 'false'}
            ]
        }

        # Evento simulado con email
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Código de confirmación enviado al correo electrónico", json.loads(response['body'])['message'])

        # Verificar que se actualizó el atributo email_verified
        mock_cognito_client.admin_update_user_attributes.assert_called_once_with(
            UserPoolId='test_user_pool_id',
            Username='user@example.com',
            UserAttributes=[
                {'Name': 'email_verified', 'Value': 'true'}
            ]
        )

        # Verificar que se llamó a forgot_password con los parámetros correctos
        mock_cognito_client.forgot_password.assert_called_once_with(
            ClientId='test_client_id',
            Username='user@example.com'
        )

    @patch('cognito.forgot_password.app.get_secret')
    @patch('cognito.forgot_password.app.boto3.client')
    def test_lambda_handler_cognito_exception(self, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id', 'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para que Cognito lance una excepción
        mock_cognito_client.admin_get_user.side_effect = ClientError(
            error_response={'Error': {'Code': 'UserNotFoundException', 'Message': 'User not found'}},
            operation_name='AdminGetUser'
        )

        # Evento simulado con email
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("User not found", json.loads(response['body'])['error_message'])

    @patch('cognito.forgot_password.app.get_secret')
    @patch('cognito.forgot_password.app.boto3.client')
    def test_lambda_handler_general_exception(self, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id', 'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción general
        mock_cognito_client.admin_get_user.side_effect = Exception('Unexpected error')

        # Evento simulado con email
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("An unexpected error occurred", json.loads(response['body'])['error_message'])

if __name__ == '__main__':
    unittest.main()
