import unittest
from unittest.mock import patch, MagicMock
import json
from user.get_userById.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestUserGetUserById(unittest.TestCase):

    @patch('user.get_userById.app.get_connection')
    @patch('user.get_userById.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que se encontró el usuario en la base de datos
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe', 'Smith', 'john.doe@example.com', 'hashedpassword', '+123456789', 2, True)
        ]

        # Evento simulado con id_user
        mock_event = {
            'queryStringParameters': {
                'id_user': '1'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Información del usuario obtenida correctamente.')
        self.assertEqual(len(body['data']), 1)
        self.assertEqual(body['data'][0]['name'], 'John')
        self.assertEqual(body['data'][0]['email'], 'john.doe@example.com')

        # Verificar que se ejecutó la consulta SQL con el id_user correcto
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT id_user, name, lastname, second_lastname, email, password, phone, id_rol, status 
            FROM users 
            WHERE id_user = %s
            """, ('1',)
        )

    def test_lambda_handler_missing_id_user(self):
        # Evento simulado sin id_user
        mock_event = {
            'body': json.dumps({})
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Falta el id')

    @patch('user.get_userById.app.get_connection')
    @patch('user.get_userById.app.handle_response')
    def test_lambda_handler_user_not_found(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que no se encontró el usuario en la base de datos
        mock_cursor.fetchall.return_value = []

        # Evento simulado con id_user
        mock_event = {
            'queryStringParameters': {
                'id_user': '999'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Usuario no encontrado.')

    @patch('user.get_userById.app.get_connection')
    @patch('user.get_userById.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado con id_user
        mock_event = {
            'queryStringParameters': {
                'id_user': '1'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('Ocurrió un error al obtener la información del usuario.', body['message'])

if __name__ == '__main__':
    unittest.main()
