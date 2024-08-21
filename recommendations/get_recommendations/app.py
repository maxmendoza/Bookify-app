import json
from recommendations.get_recommendations.db_connection import get_secret, get_connection, handle_response

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET'
}


def lambda_handler(event, _context):
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        select_recom = """
            SELECT id_recommendation, id_book, id_user, recommendation_text 
            FROM recommendations
        """

        cursor.execute(select_recom)
        recomms = cursor.fetchall()

        recomm_list = [
            {
                'id_recommendation': recomm[0],
                'id_book': recomm[1],
                'id_user': recomm[2],
                'recommendation_text': recomm[3]  # Corregir el índice aquí
            }
            for recomm in recomms
        ]

    except Exception as e:
        return handle_response(e, f'Failed to execute query: {str(e)}', 500)
    finally:
        if connection:
            connection.close()

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Recomendaciones obtenidas correctamente',
            'data': recomm_list  # Retornar la lista completa aquí
        })
    }
