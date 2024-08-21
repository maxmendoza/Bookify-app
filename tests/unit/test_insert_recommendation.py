import unittest
from unittest.mock import patch, MagicMock
import json
from recommendations.insert_recommendation.app import lambda_handler  # Asegúrate de que la ruta sea correcta

class TestInsertRecommendation(unittest.TestCase):

    @patch('recommendations.insert_recommendation.app.get_connection')
    @patch('recommendations.insert_recommendation.app.handle_response')
    def test_lambda_handler_success(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simular el ID generado después de la inserción
        mock_cursor.lastrowid = 1

        # Evento simulado con todos los datos requeridos
        mock_event = {
            'body': json.dumps({
                'id_book': 101,
                'id_user': 202,
                'recommendation_text': 'Great book!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Recomendación creada correctamente')
        self.assertEqual(body['id_recommendation'], 1)

        # Verificar que se ejecutó la consulta SQL con los datos correctos
        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO recommendations (id_book, id_user, recommendation_text)
            VALUES (%s, %s, %s)
            """, (101, 202, 'Great book!')
        )

        # Verificar que se hizo commit de la transacción
        mock_conn.commit.assert_called_once()

    def test_lambda_handler_missing_data(self):
        # Evento simulado faltando el campo 'recommendation_text'
        mock_event = {
            'body': json.dumps({
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

    @patch('recommendations.insert_recommendation.app.get_connection')
    @patch('recommendations.insert_recommendation.app.handle_response')
    def test_lambda_handler_exception(self, mock_handle_response, mock_get_connection):
        # Configuración de los mocks para lanzar una excepción
        mock_get_connection.side_effect = Exception('Database connection failed')

        # Evento simulado con todos los datos requeridos
        mock_event = {
            'body': json.dumps({
                'id_book': 101,
                'id_user': 202,
                'recommendation_text': 'Great book!'
            })
        }

        # Llamar al lambda_handler
        response = lambda_handler(mock_event, None)

        # Verificaciones
        mock_handle_response.assert_called_once()
        self.assertEqual(response['statusCode'], 500)

if __name__ == '__main__':
    unittest.main()
