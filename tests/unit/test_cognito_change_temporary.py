import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.change_temporary.app import lambda_handler,handle_response
from botocore.exceptions import ClientError

class TestCognitoChangeTemporary(unittest.TestCase):

    @patch('cognito.change_temporary.app.get_secret')
    @patch('cognito.change_temporary.app.get_connection')
    @patch('cognito.change_temporary.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_get_connection, mock_get_secret):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_get_secret.return_value = {'client_id': 'test_client_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Simular respuesta de autenticación exitosa con cambio de contraseña requerido
        mock_cognito_client.initiate_auth.return_value = {
            'ChallengeName': 'NEW_PASSWORD_REQUIRED',
            'Session': 'test_session'
        }

        # Evento simulado con email, temporary_password, y new_password
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'temporary_password': 'TempPass123!',
                'new_password': 'NewPass456!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Contraseña actualizada correctamente')

        # Verificar que se llamó a Cognito con los parámetros correctos
        mock_cognito_client.initiate_auth.assert_called_once_with(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'user@example.com',
                'PASSWORD': 'TempPass123!'
            },
            ClientId='test_client_id'
        )

        mock_cognito_client.respond_to_auth_challenge.assert_called_once_with(
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={
                'NEW_PASSWORD': 'NewPass456!',
                'USERNAME': 'user@example.com'
            },
            ClientId='test_client_id',
            Session='test_session'
        )

        # Verificar que se realizó la actualización en la base de datos
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET password=%s WHERE email=%s",
            (unittest.mock.ANY, 'user@example.com')
        )

        # Verificar que se realizó el commit
        mock_conn.commit.assert_called_once()

    @patch('cognito.change_temporary.app.get_secret')
    def test_lambda_handler_missing_parameters(self, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id'}

        # Evento simulado sin parámetros obligatorios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com'
                # Falta temporary_password y new_password
            })
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error al analizar el cuerpo del evento.', json.loads(response['body'])['message'])

    @patch('cognito.change_temporary.app.get_secret')
    @patch('cognito.change_temporary.app.boto3.client')
    def test_lambda_handler_cognito_exception(self, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'client_id': 'test_client_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para que Cognito lance una excepción
        mock_cognito_client.initiate_auth.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect username or password'}},
            operation_name='InitiateAuth'
        )

        # Evento simulado con parámetros obligatorios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'temporary_password': 'TempPass123!',
                'new_password': 'NewPass456!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error changing temporary password', json.loads(response['body'])['message'])
        self.assertIn('NotAuthorizedException', json.loads(response['body'])['error'])

if __name__ == '__main__':
    unittest.main()
