import json
from book.get_books.db_connection import get_secret, get_connection, handle_response

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, _context):
    connection = None
    try:

        connection = get_connection()
        cursor = connection.cursor()

        select_books_query = """
            SELECT id_book, title, author, gener, year, description, synopsis, image_url, pdf_url, status
            FROM books
        """
        cursor.execute(select_books_query)
        books = cursor.fetchall()

        book_list = []
        for book in books:
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
            book_list.append(book_data)

    except Exception as e:
        return handle_response(e, f'Failed to execute query: {str(e)}', 500)
    finally:
        if connection:
            connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps(book_list)
    }
