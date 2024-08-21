import json
import jwt
import requests
from jwt import PyJWKClient
from user.get_userById.db_connection import get_connection, handle_response, get_secret

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):

    id_user = None
    if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
        id_user = event['queryStringParameters'].get('id_user')
    else:
        try:
            body = json.loads(event['body'])
        except (TypeError, json.JSONDecodeError) as e:
            return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)
        id_user = body.get('id_user')

    if not id_user:
        return handle_response(None, 'Falta el id', 400)

    connection = get_connection()
    query = """
        SELECT id_user, name, lastname, second_lastname, email, password, phone, id_rol, status 
        FROM users 
        WHERE id_user = %s
    """
    user_data = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (id_user,))
            result = cursor.fetchall()

            #Si no hay datos no hay usuario
            if not result:
                return {
                    'statusCode': 404,
                    'headers': headers_cors,
                    'body': json.dumps({
                        'statusCode': 404,
                        'message': 'Usuario no encontrado.'
                    })
                }

            for row in result:
                user = {
                    'id_user': row[0],
                    'name': row[1],
                    'lastname': row[2],
                    'second_lastname': row[3],
                    'email': row[4],
                    'password': row[5],
                    'phone': row[6],
                    'id_rol': row[7],
                    'status': bool(row[8])
                }
                user_data.append(user)

    except Exception as e:
        return handle_response(e, 'Ocurrió un error al obtener la información del usuario.', 500)

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Información del usuario obtenida correctamente.',
            'data': user_data
        })
    }
