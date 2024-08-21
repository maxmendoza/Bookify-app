import boto3
from botocore.exceptions import ClientError
import json
from cognito.login.db_conection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    secrets = get_secret()
    client_id = secrets['client_id']
    user_pool_id = secrets['user_pool_id']
    region = 'us-east-1'
    client = boto3.client('cognito-idp', region_name=region)

    try:
        # Obtener parámetros del cuerpo de la solicitud
        body_parameters = json.loads(event["body"])
        email = body_parameters.get('email')
        password = body_parameters.get('password')

        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Obtén los grupos del usuario
        user_groups = client.admin_list_groups_for_user(
            Username=email,
            UserPoolId=user_pool_id  # Reemplaza con tu User Pool ID
        )

        # Determina el rol basado en el grupo
        role = None
        if user_groups['Groups']:
            role = user_groups['Groups'][0]['GroupName']  # Asumiendo un usuario pertenece a un solo grupo

        return {
            'statusCode': 200,
            'headers': headers_cors,  # Incluye los encabezados CORS
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': role
            })
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            # Invalid username or password
            return {
                'statusCode': 401,
                'headers': headers_cors,
                'body': json.dumps({"error_message": "Usuario o contraseña inválidos"})
            }
        elif error_code == 'UserNotFoundException':
            # User does not exist
            return {
                'statusCode': 404,
                'headers': headers_cors,
                'body': json.dumps({"error_message": "Usuario no encontrado"})
            }
        else:
            return {
                'statusCode': 400,
                'headers': headers_cors,
                'body': json.dumps({"error_message": e.response['Error']['Message']})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({"error_message": str(e)})
        }

