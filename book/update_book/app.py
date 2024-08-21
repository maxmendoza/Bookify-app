import json
from book.update_book.db_connection import get_secret, get_connection, handle_response
import base64
import boto3
import logging
import uuid

headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'PUT'
}


def lambda_handler(event, _context):
    conn = None
    cur = None

    try:
        # Validate request
        request_body = json.loads(event['body'])
        id_book = request_body['id_book']
        title = request_body.get('title')
        author = request_body.get('author')
        gener = request_body.get('gener')
        year = request_body.get('year')
        description = request_body.get('description')
        synopsis = request_body.get('synopsis')
        image_base64 = request_body.get('image')
        pdf_base64 = request_body.get('pdf')
        status = request_body.get('status')

        s3_client = boto3.client('s3')
        bucket_name = get_secret()['BUCKET_NAME']
        image_url = None
        pdf_url = None

        if image_base64:
            image_url = upload_to_s3(image_base64, s3_client, bucket_name, 'images_cover')
            logging.info(f"Image uploaded to S3: {image_url}")

        if pdf_base64:
            pdf_url = upload_to_s3(pdf_base64, s3_client, bucket_name, 'pdf_book')
            logging.info(f"PDF uploaded to S3: {pdf_url}")

        # Database connection
        conn = get_connection()
        cur = conn.cursor()
        conn.autocommit = False

        update_fields = []
        update_values = []

        if title:
            update_fields.append("title = %s")
            update_values.append(title)
        if author:
            update_fields.append("author = %s")
            update_values.append(author)
        if gener:
            update_fields.append("gener = %s")
            update_values.append(gener)
        if year:
            update_fields.append("year = %s")
            update_values.append(year)
        if description:
            update_fields.append("description = %s")
            update_values.append(description)
        if synopsis:
            update_fields.append("synopsis = %s")
            update_values.append(synopsis)
        if image_url:
            update_fields.append("image_url = %s")
            update_values.append(image_url)
        if pdf_url:
            update_fields.append("pdf_url = %s")
            update_values.append(pdf_url)
        if status is not None:
            update_fields.append("status = %s")
            update_values.append(status)

        if not update_fields:
            raise ValueError("No valid fields to update")

        # Add id_book to where clause
        update_values.append(id_book)

        update_query = f"UPDATE books SET {', '.join(update_fields)} WHERE id_book = %s"
        cur.execute(update_query, tuple(update_values))

        # Commit transaction
        conn.commit()
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Book updated successfully"}),
            'headers': headers
        }

    except Exception as e:
        if conn is not None:
            conn.rollback()
        return handle_response(e, 'Error processing request', 500)

    finally:
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