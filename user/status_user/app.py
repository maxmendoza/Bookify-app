import json
from user.status_user.db_connetion import get_secret, get_connection, handle_response, authorized

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):

    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Invalid request body.'})
        }

    user_id = body.get('id_user')
    status = body.get('status')

    if user_id is None or status is None:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Faltan parámetros'})
        }

    if not isinstance(status, bool):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Status must be a boolean.'})
        }

    try:
        connection = get_connection()
        user_exists = check_user_exists(user_id, connection)
        if not user_exists:
            return {
                'statusCode': 404,
                'headers': headers_cors,
                'body': json.dumps({'message': 'Usuario no encontrado'})
            }
        response = update_user_status(user_id, status, connection)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }


def check_user_exists(id_user, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE id_user = %s",
                (id_user,)
            )
            result = cursor.fetchone()
            return result[0] > 0
    except Exception as e:
        raise e


def update_user_status(user_id, status, connection):
    try:
        with connection.cursor() as cursor:
            update_query = """
            UPDATE users
            SET status = %s
            WHERE id_user = %s
            """
            cursor.execute(update_query, (status, user_id))
            connection.commit()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'Error al actualizar el status: {str(e)}'})
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Estado cambiado correctamente'})
    }
