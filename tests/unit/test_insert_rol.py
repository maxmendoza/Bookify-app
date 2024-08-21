import unittest
from unittest.mock import patch, MagicMock
import json
from roles.insert_rol.app import lambda_handler  # Asegúrate de que la ruta sea correcta
import pymysql

class TestInsertRol(unittest.TestCase):

    @patch('roles.insert_rol.app.get_connection')
    def test_lambda_handler_success(self, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'name_rol': 'Admin',
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Rol creado con éxito', json.loads(response['body']))

        # Verificar que se ejecutó la consulta SQL con los datos correctos
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO roles (name_rol, status) VALUES (%s, %s)",
            ('Admin', True)
        )

        # Verificar que se hizo commit de la transacción
        mock_conn.commit.assert_called_once()

    def test_lambda_handler_invalid_json(self):
        # Evento simulado con JSON inválido
        mock_event = {
            'body': "invalid-json"
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid JSON input', json.loads(response['body'])['error'])

    @patch('roles.insert_rol.app.get_connection')
    def test_lambda_handler_mysql_error(self, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción MySQL
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = pymysql.MySQLError('MySQL Error')

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'name_rol': 'Admin',
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error creating role', json.loads(response['body'])['error'])

    @patch('roles.insert_rol.app.get_connection')
    def test_lambda_handler_general_exception(self, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción general
        mock_conn = MagicMock()
        mock_get_connection.side_effect = Exception('Unexpected error')

        # Evento simulado con los datos necesarios
        mock_event = {
            'body': json.dumps({
                'name_rol': 'Admin',
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Unexpected error', json.loads(response['body'])['error'])

if __name__ == '__main__':
    unittest.main()
