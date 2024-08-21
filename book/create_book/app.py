import json
import boto3
import logging
import uuid
from book.create_book.db_connection import get_secret, get_connection, handle_response
import base64

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST'
}


def lambda_handler(event, _context):
    conn = None
    cur = None

    try:
        # Validate request
        request_body = json.loads(event['body'])
        title = request_body['title']
        author = request_body['author']
        gener = request_body['gener']
        year = request_body['year']
        description = request_body['description']
        synopsis = request_body['synopsis']
        image_base64 = request_body['image']
        pdf_base64 = request_body['pdf']
        status = request_body.get('status', True)  # Default to True if not provided

        # Upload files to S3
        s3_client = boto3.client('s3')
        bucket_name = get_secret()['BUCKET_NAME']

        # Upload image
        image_url = upload_to_s3(image_base64, s3_client, bucket_name, 'images_cover')
        logging.info(f"Image uploaded to S3: {image_url}")

        # Upload PDF
        pdf_url = upload_to_s3(pdf_base64, s3_client, bucket_name, 'pdf_book')
        logging.info(f"PDF uploaded to S3: {pdf_url}")

        # Database connection
        conn = get_connection()
        cur = conn.cursor()
        conn.autocommit = False

        # Insert book record
        insert_book_query = """
            INSERT INTO books (title, author, gener, year, description, synopsis, image_url, pdf_url, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_book_query, (title, author, gener, year, description, synopsis, image_url, pdf_url, status))

        # Commit transaction
        conn.commit()
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Book created successfully"}),
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


def upload_to_s3(base64_data, s3_client, bucket_name, folder):
    binary_data, file_name = decode_base64(base64_data, folder)
    response = s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=binary_data,
                                    ContentType='application/octet-stream')
    logging.debug(f"File uploaded to S3: {response}")
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    return s3_url


def decode_base64(base64_data, folder):
    base64_str = base64_data.split(',')[1]
    file_extension = 'jpg' if 'image' in base64_data else 'pdf'
    file_name = f"{folder}/{uuid.uuid4()}.{file_extension}"
    binary_data = base64.b64decode(base64_str)
    return binary_data, file_name
