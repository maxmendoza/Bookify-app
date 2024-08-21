import boto3
from botocore.exceptions import ClientError
import json
from werkzeug.security import generate_password_hash
from cognito.change_temporary.db_conection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    secrets = get_secret()
    client_id = secrets['client_id']
    try:
        body = json.loads(event['body'])
    except (TypeError, json.JSONDecodeError) as e:
        return handle_response(e, 'Error al analizar el cuerpo del evento.', 400)

    email = body.get('email')
    temporary_password = body.get('temporary_password')
    new_password = body.get('new_password')

    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        # Authenticate the user with the temporary password
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': temporary_password
            },
            ClientId=client_id
        )

        # Print or log the response for debugging
        print("Auth Response:", response)

        # Check if AuthenticationResult is in the response
        if 'ChallengeName' in response:
            if response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                # Complete the new password challenge
                session = response['Session']
                client.respond_to_auth_challenge(
                    ChallengeName='NEW_PASSWORD_REQUIRED',
                    ChallengeResponses={
                        'NEW_PASSWORD': new_password,
                        'USERNAME': email
                    },
                    ClientId=client_id,
                    Session=session
                )
            else:
                return handle_response(None, 'Authentication failed or challenge not expected.', 400)
        else:
            # Use the authentication tokens to change the password
            access_token = response['AuthenticationResult']['AccessToken']
            client.change_password(
                PreviousPassword=temporary_password,
                ProposedPassword=new_password,
                AccessToken=access_token
            )

            hashed_password = generate_password_hash(new_password)

            connection = get_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE users SET password=%s WHERE email=%s"
                cursor.execute(sql, (hashed_password, email))
            connection.commit()

    except ClientError as e:
        return handle_response(e, f'Error changing temporary password: {str(e)}', 400)
    except Exception as e:
        return handle_response(e, f'Unexpected error: {str(e)}', 500)

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Contraseña actualizada correctamente'})
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
