import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.confirm_password.app import lambda_handler, update_password_in_db, handle_response  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoConfirmPassword(unittest.TestCase):

    @patch('cognito.confirm_password.app.get_secret')
    @patch('cognito.confirm_password.app.update_password_in_db')
    @patch('cognito.confirm_password.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_update_password_in_db, mock_get_secret):
        # Configuración de los mocks
        mock_get_secret.return_value = {'client_id': 'test_client_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Evento simulado con email, confirmation_code, y new_password
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'confirmation_code': '123456',
                'new_password': 'NewPass456!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Contraseña restablecida correctamente')

        # Verificar que se llamó a Cognito con los parámetros correctos
        mock_cognito_client.confirm_forgot_password.assert_called_once_with(
            ClientId='test_client_id',
            Username='user@example.com',
            ConfirmationCode='123456',
            Password='NewPass456!'
        )

        # Verificar que se actualizó la contraseña en la base de datos
        mock_update_password_in_db.assert_called_once_with(
            'user@example.com',
            unittest.mock.ANY  # El hash de la contraseña no se puede verificar directamente
        )

    def test_lambda_handler_missing_parameters(self):
        # Evento simulado sin parámetros obligatorios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                # Falta confirmation_code y new_password
            })
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid input', json.loads(response['body'])['message'])

    @patch('cognito.confirm_password.app.get_secret')
    @patch('cognito.confirm_password.app.boto3.client')
    def test_lambda_handler_cognito_exception(self, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para que Cognito lance una excepción
        mock_cognito_client.confirm_forgot_password.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect confirmation code'}},
            operation_name='ConfirmForgotPassword'
        )

        # Evento simulado con parámetros obligatorios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'confirmation_code': '123456',
                'new_password': 'NewPass456!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error confirming forgot password', json.loads(response['body'])['message'])
        self.assertIn('NotAuthorizedException', json.loads(response['body'])['error'])

    @patch('cognito.confirm_password.app.get_secret')
    @patch('cognito.confirm_password.app.boto3.client')
    @patch('cognito.confirm_password.app.update_password_in_db')
    def test_lambda_handler_db_exception(self, mock_update_password_in_db, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción en la actualización de la base de datos
        mock_update_password_in_db.side_effect = RuntimeError('Failed to update password in the database')

        # Evento simulado con parámetros obligatorios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'confirmation_code': '123456',
                'new_password': 'NewPass456!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Failed to update password in the database', json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
