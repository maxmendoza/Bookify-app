import json
from book.get_bookById.db_connection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, _context):
    connection = None
    try:
        id_book = event['queryStringParameters']['id_book']

        connection = get_connection()
        cursor = connection.cursor()

        select_book_query = """
            SELECT id_book, title, author, gener, year, description, synopsis, image_url, pdf_url, status
            FROM books
            WHERE id_book = %s
        """
        cursor.execute(select_book_query, (id_book,))
        book = cursor.fetchone()

        # Verificar si se encontró el libro
        if book:
            book_data = {
                'id_book': book[0],
                'title': book[1],
                'author': book[2],
                'gener': book[3],
                'year': book[4],
                'description': book[5],
                'synopsis': book[6],
                'image_url': book[7],
                'pdf_url': book[8],
                'status': book[9]
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers_cors,
                'body': json.dumps({"message": "Book not found"})
            }

    except Exception as e:
        return handle_response(e, f'Failed to execute query: {str(e)}', 500)
    finally:
        if connection:
            connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({
            'statusCode': 200,
            'message': 'Libro obtenido correctamente',
            'data': book_data
        })
    }
