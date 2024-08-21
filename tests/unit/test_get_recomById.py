import unittest
from unittest.mock import patch, MagicMock
import json
from recommendations.get_recomById.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetRecomById(unittest.TestCase):

    @patch('recommendations.get_recomById.app.get_connection')
    @patch('recommendations.get_recomById.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que se encontró la recomendación en la base de datos
        mock_cursor.fetchone.return_value = (
            1, 101, 202, 'Highly recommended!'
        )

        # Evento simulado con id_recommendation
        mock_event = {
            'queryStringParameters': {
                'id_recommendation': '1'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recomendación obtenida correctamente')
        self.assertEqual(body['data']['id_recommendation'], 1)
        self.assertEqual(body['data']['id_book'], 101)
        self.assertEqual(body['data']['id_user'], 202)
        self.assertEqual(body['data']['recommendation_text'], 'Highly recommended!')

        # Verificar que se llamó a la consulta SQL con el id_recommendation correcto
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT id_recommendation, id_book, id_user, recommendation_text
            FROM recommendations
            WHERE id_recommendation = %s
            """, ('1',)
        )

    def test_lambda_handler_missing_id_recommendation(self):
        # Evento simulado sin id_recommendation
        mock_event = {
            'queryStringParameters': {}
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'id_recommendation es requerido')

    @patch('recommendations.get_recomById.app.get_connection')
    @patch('recommendations.get_recomById.app.handle_response')
    def test_lambda_handler_recommendation_not_found(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que no se encontró la recomendación en la base de datos
        mock_cursor.fetchone.return_value = None

        # Evento simulado con id_recommendation
        mock_event = {
            'queryStringParameters': {
                'id_recommendation': '999'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recommendation not found')

    @patch('recommendations.get_recomById.app.get_connection')
    @patch('recommendations.get_recomById.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado con id_recommendation
        mock_event = {
            'queryStringParameters': {
                'id_recommendation': '1'
            }
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
