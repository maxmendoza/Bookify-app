import json
from user.get_users.db_connection import get_secret, get_connection, handle_response, authorized

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):

    connection = get_connection()
    users = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id_user, name, lastname, second_lastname, email, password, phone, id_rol, status FROM users")
            result = cursor.fetchall()

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
                    'status': row[8]
                }
                users.append(user)

    except Exception as e:
        return handle_response(str(e), 'Error al obtener usuarios: ', 500)

    finally:
        connection.close()

    return {
        "statusCode": 200,
        'headers': headers_cors,
        "body": json.dumps({
            'statusCode': 200,
            'message': 'Usuarios obtenidos correctamente',
            'data': users
        }),
    }

