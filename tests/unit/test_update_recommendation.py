import unittest
from unittest.mock import patch, MagicMock
import json
from recommendations.update_recommendation.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestUpdateRecommendation(unittest.TestCase):

    @patch('recommendations.update_recommendation.app.get_connection')
    @patch('recommendations.update_recommendation.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simular que una fila fue afectada

        # Evento simulado con todos los datos requeridos
        mock_event = {
            'body': json.dumps({
                'id_recommendation': 1,
                'id_book': 101,
                'id_user': 202,
                'recommendation_text': 'Updated recommendation!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recomendación actualizada correctamente')

        # Verificar que se ejecutó la consulta SQL con los datos correctos
        mock_cursor.execute.assert_called_once_with(
            """
            UPDATE recommendations
            SET id_book = %s, id_user = %s, recommendation_text = %s
            WHERE id_recommendation = %s
            """, (101, 202, 'Updated recommendation!', 1)
        )

        # Verificar que se hizo commit de la transacción
        mock_conn.commit.assert_called_once()

    def test_lambda_handler_missing_data(self):
        # Evento simulado faltando el campo 'recommendation_text'
        mock_event = {
            'body': json.dumps({
                'id_recommendation': 1,
                'id_book': 101,
                'id_user': 202
                # 'recommendation_text' falta aquí
            })
        }

        # Llamar al lambda_handler y capturar la respuesta
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Faltan datos requeridos')

    @patch('recommendations.update_recommendation.app.get_connection')
    @patch('recommendations.update_recommendation.app.handle_response')
    def test_lambda_handler_recommendation_not_found(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0  # Simular que ninguna fila fue afectada

        # Evento simulado con todos los datos requeridos
        mock_event = {
            'body': json.dumps({
                'id_recommendation': 999,
                'id_book': 101,
                'id_user': 202,
                'recommendation_text': 'Non-existing recommendation'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recomendación no encontrada')

    @patch('recommendations.update_recommendation.app.get_connection')
    @patch('recommendations.update_recommendation.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado con todos los datos requeridos
        mock_event = {
            'body': json.dumps({
                'id_recommendation': 1,
                'id_book': 101,
                'id_user': 202,
                'recommendation_text': 'Updated recommendation!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
