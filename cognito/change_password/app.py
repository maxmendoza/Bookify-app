import boto3
from botocore.exceptions import ClientError
import json
import os

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

client_id = os.getenv('CLIENT_ID')
region_name = 'us-east-1'
ses_sender_email = os.getenv('SES_SENDER_EMAIL')  # Dirección de correo electrónico verificada en SES


def lambda_handler(event, context):
    body = json.loads(event.get('body', {}))
    email = body.get('email')

    if not email:
        return handle_response('Missing email', 'Invalid input', 400)

    client = boto3.client('cognito-idp', region_name=region_name)

    try:
        response = client.forgot_password(
            ClientId=client_id,
            Username=email
        )
    except ClientError as e:
        return handle_response(e, f'Error initiating forgot password: {str(e)}', 400)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Password reset initiated. Check your email for the verification code.'})
    }
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
