import json
from recommendations.update_recommendation.db_connection import get_secret, get_connection, handle_response

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'PUT'
}


def lambda_handler(event, _context):
    connection = None

    try:
        body = json.loads(event['body'])
        id_recommendation = body.get('id_recommendation')
        id_book = body.get('id_book')
        id_user = body.get('id_user')
        recommendation_text = body.get('recommendation_text')

        if not id_recommendation or not id_book or not id_user or not recommendation_text:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"message": "Faltan datos requeridos"})
            }

        connection = get_connection()
        cursor = connection.cursor()

        update_recomm_query = """
            UPDATE recommendations
            SET id_book = %s, id_user = %s, recommendation_text = %s
            WHERE id_recommendation = %s
        """

        cursor.execute(update_recomm_query, (id_book, id_user, recommendation_text, id_recommendation))
        connection.commit()

        if cursor.rowcount == 0:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"message": "Recomendación no encontrada"})
            }

    except Exception as e:
        return handle_response(e, f'Failed to update recommendation: {str(e)}', 500)
    finally:
        if connection:
            connection.close()

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Recomendación actualizada correctamente'
        })
    }
