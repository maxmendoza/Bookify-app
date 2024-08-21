import json
import boto3
from recommendations.get_recomById.db_connection import get_secret, get_connection, handle_response

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET'
}


def lambda_handler(event, _context):
    connection = None
    try:
        # Validar que id_recommendation esté presente
        if 'id_recommendation' not in event['queryStringParameters']:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"message": "id_recommendation es requerido"})
            }

        id_recommendation = event['queryStringParameters']['id_recommendation']
        connection = get_connection()
        cursor = connection.cursor()

        select_recomm_query = """
            SELECT id_recommendation, id_book, id_user, recommendation_text
            FROM recommendations
            WHERE id_recommendation = %s
        """

        cursor.execute(select_recomm_query, (id_recommendation,))
        recomm = cursor.fetchone()

        if recomm:
            recomm_data = {
                'id_recommendation': recomm[0],
                'id_book': recomm[1],
                'id_user': recomm[2],
                'recommendation_text': recomm[3]
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"message": "Recommendation not found"})
            }

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
            'message': 'Recomendación obtenida correctamente',
            'data': recomm_data
        })
    }
