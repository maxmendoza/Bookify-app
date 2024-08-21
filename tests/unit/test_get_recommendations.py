import unittest
from unittest.mock import patch, MagicMock
import json
from recommendations.get_recommendations.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestGetRecommendations(unittest.TestCase):

    @patch('recommendations.get_recommendations.app.get_connection')
    @patch('recommendations.get_recommendations.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular que se encontraron varias recomendaciones en la base de datos
        mock_cursor.fetchall.return_value = [
            (1, 101, 202, 'Highly recommended!'),
            (2, 102, 203, 'A must-read!'),
            (3, 103, 204, 'Very informative.')
        ]

        # Evento simulado (puede estar vacío ya que no se usa en la función)
        mock_event = {}

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recomendaciones obtenidas correctamente')
        self.assertEqual(len(body['data']), 3)  # Verificar que se obtuvieron 3 recomendaciones
        self.assertEqual(body['data'][0]['recommendation_text'], 'Highly recommended!')
        self.assertEqual(body['data'][1]['recommendation_text'], 'A must-read!')
        self.assertEqual(body['data'][2]['recommendation_text'], 'Very informative.')

        # Verificar que se ejecutó la consulta SQL
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT id_recommendation, id_book, id_user, recommendation_text 
            FROM recommendations
            """
        )

    @patch('recommendations.get_recommendations.app.get_connection')
    @patch('recommendations.get_recommendations.app.handle_response')
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
