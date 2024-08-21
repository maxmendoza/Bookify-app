import json
import re
from db_connection import get_secret, get_connection, handle_response, authorized

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Invalid request body.'})
        }

    id_user = body.get('id_user')
    name = body.get('name')
    lastname = body.get('lastname')
    second_lastname = body.get('second_lastname')
    email = body.get('email')
    phone = body.get('phone')
    id_rol = body.get('id_rol')
    password = body.get('password')

    if not id_user or not name or not lastname or not email or not phone:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Faltan parametros'})
        }

    if not re.match(email_regex, email):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Correo con formato inválido'})
        }

    try:
        connection = get_connection()
        user_exists = check_user_exists(id_user, connection)
        if not user_exists:
            return {
                'statusCode': 404,
                'headers': headers_cors,
                'body': json.dumps({'message': 'Usuario no encontrado'})
            }
        response = update_user(id_user, name, lastname, second_lastname, email, phone, id_rol, password, connection)
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


def update_user(id_user, name, lastname, second_lastname, email, phone, id_rol, password, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET name = %s, lastname = %s, second_lastname = %s, email = %s, phone = %s, id_rol = %s WHERE id_user = %s",
                (name, lastname, second_lastname, email, phone, id_rol, id_user)
            )

            if password:
                cursor.execute(
                    "UPDATE users SET password = %s WHERE id_user = %s",
                    (password, id_user)
                )

            connection.commit()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'Error al actualizar usuario: {str(e)}'})
        }
    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Usuario actualizado correctamente'})
    }
