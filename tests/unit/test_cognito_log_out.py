import unittest
from unittest.mock import patch, MagicMock
import json
from cognito.log_out.app import lambda_handler  # Asegúrate de que la ruta sea correcta
from botocore.exceptions import ClientError

class TestCognitoLogOut(unittest.TestCase):

    @patch('cognito.log_out.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client):
        # Configuración del mock para Cognito
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Evento simulado con un access_token válido
        mock_event = {
            'body': json.dumps({
                'access_token': 'valid_access_token'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Cerrando sesión')

        # Verificar que se llamó a global_sign_out con el access_token correcto
        mock_cognito_client.global_sign_out.assert_called_once_with(
            AccessToken='valid_access_token'
        )

    @patch('cognito.log_out.app.boto3.client')
    def test_lambda_handler_client_error(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción ClientError
        mock_cognito_client.global_sign_out.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'The access token is invalid'}},
            operation_name='GlobalSignOut'
        )

        # Evento simulado con un access_token inválido
        mock_event = {
            'body': json.dumps({
                'access_token': 'invalid_access_token'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('The access token is invalid', json.loads(response['body'])['error_message'])

    @patch('cognito.log_out.app.boto3.client')
    def test_lambda_handler_general_exception(self, mock_boto_client):
        mock_cognito_client = MagicMock()
        mock_boto_client.return_value = mock_cognito_client

        # Configuración del mock para lanzar una excepción general
        mock_cognito_client.global_sign_out.side_effect = Exception('Unexpected error')

        # Evento simulado con un access_token válido
        mock_event = {
            'body': json.dumps({
                'access_token': 'valid_access_token'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Unexpected error', json.loads(response['body'])['error_message'])

if __name__ == '__main__':
    unittest.main()
