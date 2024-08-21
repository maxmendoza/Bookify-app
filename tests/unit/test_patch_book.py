import unittest
from unittest.mock import patch, MagicMock
import json
from book.patch_book.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestPatchBook(unittest.TestCase):

    @patch('book.patch_book.app.get_connection')
    @patch('book.patch_book.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Evento simulado con un id_book válido y nuevo status
        mock_event = {
            'body': json.dumps({
                'id_book': 1,
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Book status updated successfully")

        # Verificar que se ejecutó la query de actualización con los valores correctos
        mock_cursor.execute.assert_called_once_with(
            "UPDATE books SET status = %s WHERE id_book = %s", (True, 1)
        )

        # Verificar que se realizó el commit
        mock_conn.commit.assert_called_once()

    @patch('book.patch_book.app.get_connection')
    @patch('book.patch_book.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado
        mock_event = {
            'body': json.dumps({
                'id_book': 1,
                'status': True
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

        # Verificar que no se realizó el commit debido a la excepción
        mock_get_connection.return_value.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
