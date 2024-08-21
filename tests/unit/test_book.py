import unittest
import json
from book.create_book.app import lambda_handler

mock_create = {
    'body': json.dumps({
        'title': 'Rafa',
        "author": "Kanye West",
        "gener": "Meca",
        "year": "2002",
        "description": "chapolinesiooooo",
        "synopsis": "blah blah blah",
        "status": "1",
        "image": '',
        'pdf': ''
    })
}

mock_update = {

}

mock_status = {

}

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here
