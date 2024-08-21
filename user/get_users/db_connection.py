import boto3
from botocore.exceptions import ClientError
import pymysql
import json
import base64

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def get_secret():
    secret_name = "prod/inte/bookify"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


def get_connection():
    try:
        secrets = get_secret()
        connection = pymysql.connect(
            host=secrets['host'],
            user=secrets['username'],
            password=secrets['password'],
            database=secrets['dbname']
        )
    except Exception as e:
        return handle_response(e, f'Failed to connect to database: {str(e)}', 500)
    return connection


def get_jwt_claims(token):
    try:
        # 1. Divide el token en sus partes (header, payload, firma)
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT token")

        # 2. Decodifica el payload (segunda parte) desde Base64
        payload_encoded = parts[1]
        missing_padding = len(payload_encoded) % 4
        if missing_padding:
            payload_encoded += '=' * (4 - missing_padding)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)
        claims = json.loads(payload_decoded)

        return claims

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error decoding token: {e}")
        return None


def authorized(event, authorized_groups):
    token = event['headers']['Authorization']
    clean_token = token.replace("Bearer ", "")
    claims = get_jwt_claims(clean_token)
    if claims is None:
        return False
    if 'cognito:groups' not in claims:
        return False
    for group in authorized_groups:
        if group in claims['cognito:groups']:
            return True
    return False


def handle_response(error, message, status_code):
    return {
        'statusCode': status_code,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': status_code,
            'message': message,
            'error': str(error)
        })
    }
