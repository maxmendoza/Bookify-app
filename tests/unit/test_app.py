import unittest
from unittest.mock import patch, Mock
import pymysql
from roles.get_roles.db_connection import get_connection, handle_response, get_secret


class TestDatabaseConnection(unittest.TestCase):

    @patch('roles.get_roles.db_connection.get_secret')
    @patch('pymysql.connect')
    def test_get_connection_success(self, mock_connect, mock_get_secret):
        # Simular la respuesta de get_secret
        mock_secret_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_pass',
            'dbname': 'test_db'
        }
        mock_get_secret.return_value = mock_secret_value

        # Simular la conexión exitosa a la base de datos
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        # Llamar a la función get_connection
        connection = get_connection()

        # Verificar que se llamaron las funciones correctamente
        mock_get_secret.assert_called_once()
        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_pass',
            database='test_db'
        )

        # Verificar que la conexión retornada es la esperada
        self.assertEqual(connection, mock_connection)

        # Imprimir los secrets para verificar los valores
        print("Secrets devueltos:", mock_get_secret.return_value)
        # También puedes visualizarlos en el debugger si estás usando uno

    @patch('roles.get_roles.db_connection.get_secret')
    @patch('pymysql.connect')
    def test_get_connection_failure(self, mock_connect, mock_get_secret):
        # Simular la respuesta de get_secret
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_pass',
            'dbname': 'test_db'
        }

        # Simular una excepción al intentar conectar a la base de datos
        mock_connect.side_effect = pymysql.MySQLError('Connection error')

        # Llamar a la función get_connection
        response = get_connection()

        # Verificar que se llamaron las funciones correctamente
        mock_get_secret.assert_called_once()
        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_pass',
            database='test_db'
        )

        # Verificar que la respuesta es la esperada
        expected_response = handle_response(pymysql.MySQLError('Connection error'),
                                            'Failed to connect to database: Connection error', 500)
