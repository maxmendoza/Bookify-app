import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.login.app import lambda_handler  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoLogin(unittest.TestCase):

    @patch('cognito.login.app.get_secret')
    @patch('cognito.login.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_get_secret):
        # Configuración de los mocks
        mock_get_secret.return_value = {'client_id': 'test_client_id', 'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Simular respuesta de initiate_auth
        mock_cognito_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'IdToken': 'test_id_token',
                'AccessToken': 'test_access_token',
                'RefreshToken': 'test_refresh_token'
            }
        }

        # Simular respuesta de admin_list_groups_for_user
        mock_cognito_client.admin_list_groups_for_user.return_value = {
            'Groups': [
                {'GroupName': 'Admin'}
            ]
        }

        # Evento simulado con email y password
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'password': 'password123'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['id_token'], 'test_id_token')
        self.assertEqual(body['access_token'], 'test_access_token')
        self.assertEqual(body['refresh_token'], 'test_refresh_token')
        self.assertEqual(body['role'], 'Admin')

        # Verificar que se llamó a initiate_auth con los parámetros correctos
        mock_cognito_client.initiate_auth.assert_called_once_with(
            ClientId='test_client_id',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'user@example.com',
                'PASSWORD': 'password123'
            }
        )

        # Verificar que se llamó a admin_list_groups_for_user con los parámetros correctos
        mock_cognito_client.admin_list_groups_for_user.assert_called_once_with(
            Username='user@example.com',
            UserPoolId='test_user_pool_id'
        )

    @patch('cognito.login.app.boto3.client')
    def test_lambda_handler_not_authorized_exception(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción NotAuthorizedException
        mock_cognito_client.initiate_auth.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect username or password'}},
            operation_name='InitiateAuth'
        )

        # Evento simulado con email y password
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'password': 'wrongpassword'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 401)
        self.assertIn("Usuario o contraseña inválidos", json.loads(response['body'])['error_message'])

    @patch('cognito.login.app.boto3.client')
    def test_lambda_handler_user_not_found_exception(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción UserNotFoundException
        mock_cognito_client.initiate_auth.side_effect = ClientError(
            error_response={'Error': {'Code': 'UserNotFoundException', 'Message': 'User does not exist'}},
            operation_name='InitiateAuth'
        )

        # Evento simulado con email y password
        mock_event = {
            'body': json.dumps({
                'email': 'nonexistentuser@example.com',
                'password': 'password123'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        self.assertIn("Usuario no encontrado", json.loads(response['body'])['error_message'])

    @patch('cognito.login.app.boto3.client')
    def test_lambda_handler_general_exception(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción general
        mock_cognito_client.initiate_auth.side_effect = Exception('Unexpected error')

        # Evento simulado con email y password
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'password': 'password123'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Unexpected error", json.loads(response['body'])['error_message'])

if __name__ == '__main__':
    unittest.main()
