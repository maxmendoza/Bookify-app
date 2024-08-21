import unittest
from unittest.mock import patch, MagicMock
import json
from book.get_books.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetBooks(unittest.TestCase):

    @patch('book.get_books.app.get_connection')
    @patch('book.get_books.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular libros encontrados en la base de datos
        mock_cursor.fetchall.return_value = [
            (1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '1925',
             'A novel set in the Jazz Age', 'A story of lost love and the American Dream',
             'http://example.com/image.jpg', 'http://example.com/book.pdf', True),
            (2, '1984', 'George Orwell', 'Dystopian', '1949',
             'A novel about a totalitarian regime', 'Big Brother is watching you',
             'http://example.com/1984_image.jpg', 'http://example.com/1984_book.pdf', True)
        ]

        # Evento simulado (puede estar vacío porque no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 2)  # Asegura que se obtienen dos libros
        self.assertEqual(body[0]['title'], 'The Great Gatsby')  # Verifica el título del primer libro

    @patch('book.get_books.app.get_connection')
    @patch('book.get_books.app.handle_response')
    def test_lambda_handler_no_books_found(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que no se encontraron libros
        mock_cursor.fetchall.return_value = []

        # Evento simulado
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 0)  # Asegura que la lista de libros esté vacía

    @patch('book.get_books.app.get_connection')
    @patch('book.get_books.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
