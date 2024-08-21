import json
from book.patch_book.db_connection import get_secret, get_connection, handle_response

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'PATCH'
}


def lambda_handler(event, _context):
    conn = None
    cur = None

    try:
        request_body = json.loads(event['body'])
        id_book = request_body['id_book']
        status = request_body['status']

        conn = get_connection()
        cur = conn.cursor()
        conn.autocommit = False

        # Update status query
        update_status_query = "UPDATE books SET status = %s WHERE id_book = %s"
        cur.execute(update_status_query, (status, id_book))

        # Commit transaction
        conn.commit()
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Book status updated successfully"}),
            'headers': headers
        }

    except Exception as e:
        # Rollback transaction
        if conn is not None:
            conn.rollback()
        return handle_response(e, 'Error processing request', 500)

    finally:
        # Close database connection and cursor
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()
