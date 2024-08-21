import boto3
from botocore.exceptions import ClientError
import json
try:
    from db_conection import get_secret, get_connection, handle_response
except ImportError:
    from cognito.log_out.db_conection import get_secret, get_connection, handle_response


headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    client = boto3.client('cognito-idp', region_name='us-east-1')

    try:
        body = json.loads(event['body'])
        access_token = body['access_token']

        response = client.global_sign_out(
            AccessToken=access_token
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cerrando sesión'
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error_message': e.response['Error']['Message']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error_message': str(e)
            })
        }


