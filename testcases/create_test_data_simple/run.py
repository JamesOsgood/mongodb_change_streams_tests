from ChangeStreamBaseTest import ChangeStreamBaseTest
import random
import math
from datetime import datetime, timedelta
from bson.decimal128 import Decimal128

class PySysTest(ChangeStreamBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		ChangeStreamBaseTest.__init__(self, descriptor, outsubdir, runner)

		self.coll_name = 'input_data'

	# Test entry point
	def execute(self):
		db = self.get_db_connection(dbname=self.db_name)

		DOCUMENTS_TO_CREATE = 100000
		self.generate_documents(db, DOCUMENTS_TO_CREATE)

	def generate_documents(self, db, docs_to_generate):
		collection = db[self.input_data_coll_name]
		collection.drop()

		BUCKET_COUNT = 10
		inserted_count = 0
		doc_index = 0
		current_bucket = []
		while inserted_count < docs_to_generate:
			doc = self.create_doc(doc_index)
			current_bucket, inserted_count = self.store_doc(collection, doc, current_bucket, inserted_count, BUCKET_COUNT)
			doc_index += 1

		if len(current_bucket) > 0:
			collection.insert_many(current_bucket)
			self.log.info(f'Inserted {inserted_count + len(current_bucket)} docs')
			inserted_count += len(current_bucket)

		self.inserted_count = inserted_count

	def store_doc(self, coll, doc, current_bucket, inserted_count, bucket_count):
		current_bucket.append(doc)
		if len(current_bucket) >= bucket_count:
			coll.insert_many(current_bucket)
			self.log.info(f'Inserted {inserted_count + len(current_bucket)} docs')
			return ([], inserted_count + len(current_bucket))
		else:
			return (current_bucket, inserted_count)


	def create_doc(self, inserted_count):
		doc = {}
		doc['_id'] = inserted_count
		doc['ts'] = datetime.now()
		return doc

	def validate(self):
		db = self.get_db_connection()
		coll = db[self.coll_name]
		self.cnt = coll.count_documents({})
		self.assertThat('self.cnt == self.inserted_count')

