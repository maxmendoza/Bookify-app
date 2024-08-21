import boto3
from botocore.exceptions import ClientError
from cognito.sign_up.db_conection import get_secret, get_connection, handle_response
import json
import string
import random

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    secrets = get_secret()
    try:
        body = json.loads(event['body'])
    except (TypeError, json.JSONDecodeError) as e:
        return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)

    email = body.get('email')
    password = generate_temporary_password()
    phone_number = body.get('phone_number')
    name = body.get('name')
    lastname = body.get('lastname')
    second_lastname = body.get('second_lastname')

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        # Create user in Cognito
        client.admin_create_user(
            UserPoolId=secrets['user_pool_id'],
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'}
            ],
            TemporaryPassword=password
        )

        # Add user to 'clients' group
        client.admin_add_user_to_group(
            UserPoolId=secrets['user_pool_id'],
            Username=email,
            GroupName='Clients'
        )

        # Insert user into the database
        insert_into_user(email, name, lastname, second_lastname, phone_number, password)

    except ClientError as e:
        return handle_response(e, f'Error during registration: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Usuario registrado correctamente, verifica tu correo'})
    }


def generate_temporary_password(length=12):
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
    characters = string.ascii_letters + string.digits + special_characters

    while True:
        password = ''.join(random.choice(characters) for _ in range(length))

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in special_characters for char in password)

        if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
            return password


def insert_into_user(email, name, lastname, second_lastname, phone_number, password):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            insert_query = """INSERT INTO users (email, name, lastname, second_lastname, phone, password, id_rol, status) VALUES (%s, %s, %s, %s, %s, %s, 2, True)"""
            cursor.execute(insert_query, (email, name, lastname, second_lastname, phone_number, password))
            connection.commit()

    except Exception as e:
        print(f"Error al insertar datos: {e}")
        return handle_response(e, 'Ocurrió un error al registrar el usuario.', 500)

    finally:
        connection.close()
