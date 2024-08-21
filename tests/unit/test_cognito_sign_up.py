import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.sign_up.app import lambda_handler, generate_temporary_password, insert_into_user  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoSignUp(unittest.TestCase):

    @patch('cognito.sign_up.app.get_secret')
    @patch('cognito.sign_up.app.insert_into_user')
    @patch('cognito.sign_up.app.boto3.client')
    @patch('cognito.sign_up.app.generate_temporary_password')
    def test_lambda_handler_success(self, mock_generate_password, mock_boto_client, mock_insert_user, mock_get_secret):
        # Configuración de los mocks
        mock_get_secret.return_value = {'user_pool_id': 'test_user_pool_id'}
        mock_generate_password.return_value = 'TempPass123!'
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Evento simulado con los parámetros necesarios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'phone_number': '+1234567890',
                'name': 'John',
                'lastname': 'Doe',
                'second_lastname': 'Smith'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Usuario registrado correctamente, verifica tu correo', json.loads(response['body'])['message'])

        # Verificar que se creó el usuario en Cognito
        mock_cognito_client.admin_create_user.assert_called_once_with(
            UserPoolId='test_user_pool_id',
            Username='user@example.com',
            UserAttributes=[
                {'Name': 'email', 'Value': 'user@example.com'},
                {'Name': 'email_verified', 'Value': 'false'}
            ],
            TemporaryPassword='TempPass123!'
        )

        # Verificar que se agregó el usuario al grupo 'Clients'
        mock_cognito_client.admin_add_user_to_group.assert_called_once_with(
            UserPoolId='test_user_pool_id',
            Username='user@example.com',
            GroupName='Clients'
        )

        # Verificar que se insertó el usuario en la base de datos
        mock_insert_user.assert_called_once_with(
            'user@example.com',
            'John',
            'Doe',
            'Smith',
            '+1234567890',
            'TempPass123!'
        )

    def test_lambda_handler_invalid_json(self):
        # Evento simulado con JSON inválido
        mock_event = {
            'body': "invalid-json"
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error al analizar el cuerpo del evento.', json.loads(response['body'])['message'])

    @patch('cognito.sign_up.app.get_secret')
    @patch('cognito.sign_up.app.boto3.client')
    def test_lambda_handler_client_error(self, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción ClientError
        mock_cognito_client.admin_create_user.side_effect = ClientError(
            error_response={'Error': {'Code': 'UsernameExistsException', 'Message': 'Username already exists'}},
            operation_name='AdminCreateUser'
        )

        # Evento simulado con los parámetros necesarios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'phone_number': '+1234567890',
                'name': 'John',
                'lastname': 'Doe',
                'second_lastname': 'Smith'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error during registration', json.loads(response['body'])['message'])

    @patch('cognito.sign_up.app.get_secret')
    @patch('cognito.sign_up.app.boto3.client')
    @patch('cognito.sign_up.app.insert_into_user')
    def test_lambda_handler_db_error(self, mock_insert_user, mock_boto_client, mock_get_secret):
        mock_get_secret.return_value = {'user_pool_id': 'test_user_pool_id'}
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción al insertar en la base de datos
        mock_insert_user.side_effect = Exception('Database insertion failed')

        # Evento simulado con los parámetros necesarios
        mock_event = {
            'body': json.dumps({
                'email': 'user@example.com',
                'phone_number': '+1234567890',
                'name': 'John',
                'lastname': 'Doe',
                'second_lastname': 'Smith'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Ocurrió un error al registrar el usuario.', json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
