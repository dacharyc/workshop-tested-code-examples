import unittest
import examples.filter_tutorial as filter_tutorial
import os
import io
from contextlib import redirect_stdout
from dotenv import load_dotenv
from pymongo import MongoClient

class TestTutorialApp(unittest.TestCase):
    CONNECTION_STRING = None
    client = None
    filter_collection = None

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        TestTutorialApp.CONNECTION_STRING = os.getenv("CONNECTION_STRING")

        # fast fail
        if TestTutorialApp.CONNECTION_STRING is None:
            raise Exception("Could not retrieve CONNECTION_STRING - make sure you have created the .env file at the root of the PyMongo directory and the variable is correctly named as CONNECTION_STRING.")
        try:
            TestTutorialApp.client = MongoClient(TestTutorialApp.CONNECTION_STRING)
        except:
            raise Exception("CONNECTION_STRING invalid - make sure your connection string in your .env file matches the one for your MongoDB deployment.")

    def setUp(self):
        TestTutorialApp.client.drop_database('agg_tutorials_db')

    def test_filter_tutorial(self):
        print("----------Test should insert sample data and aggregate successfully----------")

        # results is a list of documents found by the aggregation
        results = []
        with redirect_stdout(io.StringIO()) as stdout:
            results = filter_tutorial.example(TestTutorialApp.CONNECTION_STRING)
        captured_actual_output = stdout.getvalue()
        self.assertEqual(3, len(results), "there should be only 3 documents filtered" )

        output_filepath = "examples/aggregations/filter/filter-tutorial-output.txt"
        file = open(output_filepath)
        output_lines = file.readlines()
        file.close()

        expected_list = []
        for line in output_lines:
            expected_list.append(line.strip())

        with redirect_stdout(io.StringIO()) as stdout:
            for document in expected_list:
                print(document)
        captured_expected_output = stdout.getvalue()

        self.assertEqual(captured_expected_output, captured_actual_output, "expected != actual")

        print("----------Test complete----------")

    @classmethod
    def tearDownClass(cls):
        TestTutorialApp.client.close()