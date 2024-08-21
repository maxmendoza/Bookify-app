import unittest
from unittest.mock import patch, MagicMock
import json
from user.get_users.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetUsers(unittest.TestCase):

    @patch('user.get_users.app.get_connection')
    @patch('user.get_users.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que se encontraron varios usuarios en la base de datos
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe', 'Smith', 'john.doe@example.com', 'hashedpassword', '+123456789', 2, True),
            (2, 'Jane', 'Roe', 'Johnson', 'jane.roe@example.com', 'hashedpassword', '+987654321', 3, False)
        ]

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Usuarios obtenidos correctamente')
        self.assertEqual(len(body['data']), 2)  # Verificar que se obtuvieron 2 usuarios

    @patch('user.get_users.app.get_connection')
    @patch('user.get_users.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once_with('Database connection failed', 'Error al obtener usuarios: ', 500)
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
