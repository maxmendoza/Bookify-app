import unittest
from unittest.mock import patch, MagicMock
import json
from user.status_user.app import lambda_handler, check_user_exists, update_user_status  # Asegúrate de que la ruta sea correcta

class TestStatusUser(unittest.TestCase):

    @patch('user.status_user.app.get_connection')
    @patch('user.status_user.app.check_user_exists')
    @patch('user.status_user.app.update_user_status')
    def test_lambda_handler_success(self, mock_update_user_status, mock_check_user_exists, mock_get_connection):
        # Configuración de los mocks
        mock_get_connection.return_value = MagicMock()
        mock_check_user_exists.return_value = True
        mock_update_user_status.return_value = {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({'message': 'Estado cambiado correctamente'})
        }

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'id_user': 1,
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Estado cambiado correctamente', json.loads(response['body'])['message'])

    def test_lambda_handler_invalid_json(self):
        # Evento simulado con JSON inválido
        mock_event = {
            'body': "invalid-json"
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid request body.', json.loads(response['body'])['message'])

    def test_lambda_handler_missing_parameters(self):
        # Evento simulado sin los parámetros necesarios
        mock_event = {
            'body': json.dumps({
                'id_user': 1
                # 'status' falta aquí
            })
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Faltan parámetros', json.loads(response['body'])['message'])

    def test_lambda_handler_invalid_status_type(self):
        # Evento simulado con un status no booleano
        mock_event = {
            'body': json.dumps({
                'id_user': 1,
                'status': "not-a-boolean"
            })
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Status must be a boolean.', json.loads(response['body'])['message'])

    @patch('user.status_user.app.get_connection')
    @patch('user.status_user.app.check_user_exists')
    def test_lambda_handler_user_not_found(self, mock_check_user_exists, mock_get_connection):
        # Configuración de los mocks
        mock_get_connection.return_value = MagicMock()
        mock_check_user_exists.return_value = False

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'id_user': 999,
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Usuario no encontrado', json.loads(response['body'])['message'])

    @patch('user.status_user.app.get_connection')
    @patch('user.status_user.app.check_user_exists')
    @patch('user.status_user.app.update_user_status')
    def test_lambda_handler_update_error(self, mock_update_user_status, mock_check_user_exists, mock_get_connection):
        # Configuración de los mocks
        mock_get_connection.return_value = MagicMock()
        mock_check_user_exists.return_value = True
        mock_update_user_status.return_value = {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Error al actualizar el status'})
        }

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'id_user': 1,
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error al actualizar el status', json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
