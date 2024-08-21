import json
import pymysql

try:
    from db_connection import get_secret, get_connection, handle_response
except ImportError:
    from roles.insert_rol.db_connection import get_secret, get_connection, handle_response


def lambda_handler(event, context):
    try:
        rol_data = json.loads(event['body'])
        name_rol = rol_data['name_rol']
        status = rol_data.get('status', True)

        connection = get_connection()
        if 'statusCode' in connection and connection['statusCode'] != 200:
            return connection

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO roles (name_rol, status) VALUES (%s, %s)"
                cursor.execute(sql, (name_rol, status))
                connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error creating role', 'details': str(e)})
            }
        finally:
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Rol creado con éxito')
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON input'})
        }
    except pymysql.err.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database error', 'details': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
