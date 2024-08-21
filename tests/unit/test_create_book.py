import unittest
from unittest.mock import patch, MagicMock
import json
from book.create_book.app import lambda_handler, upload_to_s3, decode_base64


class TestCreateBook(unittest.TestCase):

    @patch('book.create_book.app.get_secret')
    @patch('book.create_book.app.get_connection')
    @patch('book.create_book.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_get_connection, mock_get_secret):
        # Mock responses
        mock_get_secret.return_value = {'BUCKET_NAME': 'test-bucket'}
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        mock_s3_client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock input event
        mock_event = {
            'body': json.dumps({
                'title': 'Rafa',
                "author": "Kanye West",
                "gener": "Meca",
                "year": "2002",
                "description": "chapolinesiooooo",
                "synopsis": "blah blah blah",
                "image": 'data:image/jpeg;base64,dGVzdA==',
                'pdf': 'data:application/pdf;base64,dGVzdA==',
                'status': True
            })
        }

        # Call the lambda handler
        response = lambda_handler(mock_event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], "Book created successfully")
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('book.create_book.app.boto3.client')
    def test_upload_to_s3_success(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        mock_s3_client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Call upload_to_s3 function
        s3_url = upload_to_s3('data:image/jpeg;base64,dGVzdA==', mock_s3_client, 'test-bucket', 'images_cover')

        # Assertions
        self.assertTrue(s3_url.startswith('https://test-bucket.s3.amazonaws.com/'))

    def test_decode_base64_success(self):
        # Call decode_base64 function
        binary_data, file_name = decode_base64('data:image/jpeg;base64,dGVzdA==', 'images_cover')

        # Assertions
        self.assertEqual(binary_data, b'test')
        self.assertTrue(file_name.startswith('images_cover/'))
        self.assertTrue(file_name.endswith('.jpg'))


if __name__ == '__main__':
    unittest.main()
