import boto3
from botocore.exceptions import ClientError
import json
from cognito.forgot_password.db_conection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    secrets = get_secret()
    client = boto3.client('cognito-idp', region_name='us-east-1')
    client_id = secrets['client_id']
    user_pool_id = secrets['user_pool_id']
    try:
        # Parsea el body del evento
        body_parameters = json.loads(event["body"])
        email = body_parameters.get('email')

        # Obtener detalles del usuario
        user_details = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=email
        )

        # Verificar si el email está verificado
        email_verified = False
        for attribute in user_details['UserAttributes']:
            if attribute['Name'] == 'email_verified' and attribute['Value'] == 'true':
                email_verified = True
                break

        # Si el email no está verificado, actualizar el atributo
        if not email_verified:
            client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ]
            )

        response = client.forgot_password(
            ClientId=client_id,
            Username=email
        )

        return {
            'statusCode': 200,
            'headers': headers_cors,
            'body': json.dumps({"message": "Código de confirmación enviado al correo electrónico", "response": response})
        }
    except json.JSONDecodeError as jde:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({"error_message": "Invalid JSON format in request body", "details": str(jde)})
        }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({"error_message": str(ve)})
        }
    except ClientError as ce:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({"error_message": ce.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({"error_message": "An unexpected error occurred", "details": str(e)})
        }

