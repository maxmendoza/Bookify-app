import unittest
from unittest.mock import patch, MagicMock
import json
from book.update_book.app import lambda_handler, upload_to_s3, decode_base64  # Asegúrate de que la ruta sea correcta

class TestUpdateBook(unittest.TestCase):

    @patch('book.update_book.app.boto3.client')
    @patch('book.update_book.app.get_connection')
    @patch('book.update_book.app.get_secret')
    @patch('book.update_book.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_secret, mock_get_connection, mock_boto_client):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_get_secret.return_value = {'BUCKET_NAME': 'test-bucket'}
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        # Evento simulado con id_book y algunos campos a actualizar
        mock_event = {
            'body': json.dumps({
                'id_book': 1,
                'title': 'Updated Title',
                'author': 'Updated Author',
                'image': 'data:image/jpeg;base64,test_image_data',
                'pdf': 'data:application/pdf;base64,test_pdf_data'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Book updated successfully")

        # Verificar que se ejecutó la query de actualización con los valores correctos
        mock_cursor.execute.assert_called_once_with(
            "UPDATE books SET title = %s, author = %s, image_url = %s, pdf_url = %s WHERE id_book = %s",
            ('Updated Title', 'Updated Author', 'https://test-bucket.s3.amazonaws.com/images_cover/test_image.jpg',
             'https://test-bucket.s3.amazonaws.com/pdf_book/test_pdf.pdf', 1)
        )

        # Verificar que se realizó el commit
        mock_conn.commit.assert_called_once()

    @patch('book.update_book.app.get_connection')
    @patch('book.update_book.app.handle_response')
    def test_lambda_handler_no_valid_fields(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Evento simulado sin campos válidos para actualizar
        mock_event = {
            'body': json.dumps({
                'id_book': 1
            })
        }

        # Llamar al lambda_handler y capturar la excepción
        with self.assertRaises(ValueError) as context:
            lambda_handler(mock_event, None)

        self.assertEqual(str(context.exception), "No valid fields to update")

    @patch('book.update_book.app.get_connection')
    @patch('book.update_book.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado
        mock_event = {
            'body': json.dumps({
                'id_book': 1,
                'title': 'Updated Title'
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
