import json
from recommendations.insert_recommendation.db_connection import get_secret, get_connection, handle_response

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST'
}


def lambda_handler(event, _context):
    connection = None

    try:
        body = json.loads(event['body'])
        id_book = body.get('id_book')
        id_user = body.get('id_user')
        recommendation_text = body.get('recommendation_text')

        if not id_book or not id_user or not recommendation_text:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"message": "Faltan datos requeridos"})
            }

        connection = get_connection()
        cursor = connection.cursor()

        insert_recomm_query = """
            INSERT INTO recommendations (id_book, id_user, recommendation_text)
            VALUES (%s, %s, %s)
        """

        cursor.execute(insert_recomm_query, (id_book, id_user, recommendation_text))
        connection.commit()

        id_recommendation = cursor.lastrowid

    except Exception as e:
        return handle_response(e, f'Failed to insert recommendation: {str(e)}', 500)
    finally:
        if connection:
            connection.close()

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({
            'statusCode': 201,
            'message': 'Recomendación creada correctamente',
            'id_recommendation': id_recommendation
        })
    }
