import unittest
from unittest.mock import patch, MagicMock
import json
from book.get_bookById.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetBookById(unittest.TestCase):

    @patch('book.get_bookById.app.get_connection')
    @patch('book.get_bookById.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular un libro encontrado en la base de datos
        mock_cursor.fetchone.return_value = (
            1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '1925',
            'A novel set in the Jazz Age', 'A story of lost love and the American Dream',
            'http://example.com/image.jpg', 'http://example.com/book.pdf', True
        )

        # Evento simulado con un id_book válido
        mock_event = {
            'queryStringParameters': {'id_book': '1'}
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Libro obtenido correctamente')
        self.assertEqual(json.loads(response['body'])['data']['title'], 'The Great Gatsby')

        # Verificar que se llamó a la base de datos con el query correcto
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT id_book, title, author, gener, year, description, synopsis, image_url, pdf_url, status
            FROM books
            WHERE id_book = %s
            """, ('1',)
        )

    @patch('book.get_bookById.app.get_connection')
    @patch('book.get_bookById.app.handle_response')
    def test_lambda_handler_book_not_found(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que no se encontró ningún libro
        mock_cursor.fetchone.return_value = None

        # Evento simulado con un id_book que no existe
        mock_event = {
            'queryStringParameters': {'id_book': '999'}
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], 'Book not found')

    @patch('book.get_bookById.app.get_connection')
    @patch('book.get_bookById.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado
        mock_event = {
            'queryStringParameters': {'id_book': '1'}
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
