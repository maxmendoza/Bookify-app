import unittest
from unittest.mock import patch, MagicMock
import json
from roles.get_roles.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetRoles(unittest.TestCase):

    @patch('roles.get_roles.app.get_connection')
    @patch('roles.get_roles.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que se encontraron varios roles en la base de datos
        mock_cursor.fetchall.return_value = [
            (1, 'Admin', True),
            (2, 'User', True),
            (3, 'Guest', False)
        ]

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Roles obtenidos correctamente')
        self.assertEqual(len(body['data']), 3)  # Verificar que se obtuvieron 3 roles
        self.assertEqual(body['data'][0]['name_rol'], 'Admin')
        self.assertEqual(body['data'][1]['name_rol'], 'User')
        self.assertEqual(body['data'][2]['name_rol'], 'Guest')

        # Verificar que se ejecutó la consulta SQL
        mock_cursor.execute.assert_called_once_with("SELECT id_rol, name_rol, status FROM roles")

    @patch('roles.get_roles.app.get_connection')
    @patch('roles.get_roles.app.handle_response')
    def test_lambda_handler_db_connection_failure(self, mock_handle_response, mock_get_connection):
        # Configuración del mock para simular fallo en la conexión
        mock_get_connection.return_value = {
            'statusCode': 500,
            'body': json.dumps({'message': 'Database connection failed'})
        }

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('Database connection failed', body['message'])

    @patch('roles.get_roles.app.get_connection')
    @patch('roles.get_roles.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception('Query failed')

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('Error al obtener roles', body['message'])

if __name__ == '__main__':
    unittest.main()
