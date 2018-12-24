# -*- coding: utf-8 -*-
"""
Created on Fri Feb 09 22:13:26 2018

@author: thinky
"""
from google.cloud import storage
from google.cloud import bigquery
import pandas as pd
import h5py
import os.path
import time

class Cloud():

    def __init__(self, dataset = "simulations"):
        self.APIKEY = "Google Playground-fed214dba314.json"
        self.projectID = "innate-solution-180816"
        self.dataset = dataset

    def uploadCSVtoBQ(self, bucket_name, path, destination_name):
        self.create_table(destination_name)
        self.upload_blob(bucket_name, path, destination_name)
        self.load_data_from_gcs(bucket_name, destination_name)

    def upload_blob(self, bucket_name, path, destination_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client.from_service_account_json(
        self.APIKEY)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_name)
        blob.upload_from_filename(path)

        print(('File {} uploaded to {}.'.format(
            path,
            destination_name)))

    def load_data_from_gcs(self, bucket_name, destination_name):
        print('Loading Data from GCS to BQ Table')
        source = 'gs://{}/{}'.format(bucket_name, destination_name)
        bigquery_client = bigquery.Client.from_service_account_json(self.APIKEY)
        dataset_ref = bigquery_client.dataset(self.dataset)
        table_ref = dataset_ref.table(destination_name)
        #Ignore the first row
        job_config = bigquery.LoadJobConfig()
        job_config.skip_leading_rows = 1

        job = bigquery_client.load_table_from_uri(source,
                                                  table_ref,
                                                  job_config=job_config)
        while True:
            job.reload()
            if job.state == 'DONE':
                if job.error_result:
                    raise RuntimeError(job.errors)
                return
            time.sleep(1)
        job.result()  # Waits for job to complete

        print(('Loaded {} rows into {}:{}.'.format(
            job.output_rows, self.dataset, destination_name)))

    def create_table(self, name):
        """Creates a simple table in the given dataset.

        If no project is specified, then the currently active project is used.
        """
        bigquery_client = bigquery.Client.from_service_account_json(self.APIKEY)
        dataset_ref = bigquery_client.dataset(self.dataset)

        table_ref = dataset_ref.table(name)
        table = bigquery.Table(table_ref)

        # Set the table schema
        # table.schema = (
        #    bigquery.SchemaField('ID', 'STRING'),
        #    bigquery.SchemaField('random_field', 'STRING'),
        #    bigquery.SchemaField('As', 'STRING'),
        #    bigquery.SchemaField('Time_ID', 'STRING'),
        #    bigquery.SchemaField('Phis', 'STRING'),
        #    bigquery.SchemaField('mesh_size', 'STRING'),
        #    bigquery.SchemaField('init', 'STRING'),
        #    bigquery.SchemaField('mean', 'STRING')
        # )

        table = bigquery_client.create_table(table)

        print(('Created table {} in dataset {}.'.format(name, self.dataset)))

    def create_table_with_schema(self, name,schema):
        """Creates a simple table in the given dataset.

        If no project is specified, then the currently active project is used.
        """
        bigquery_client = bigquery.Client.from_service_account_json(self.APIKEY)
        dataset_ref = bigquery_client.dataset(self.dataset)

        table_ref = dataset_ref.table(name)
        table = bigquery.Table(table_ref)

        table.schema = tuple([bigquery.SchemaField(i,'STRING') for i in schema])

        table = bigquery_client.create_table(table)

        print(('Created table {} in dataset {}.'.format(name, self.dataset)))

    def download_blob(self, bucket_name, source_name, destination_name):
        """Downloads a blob from the bucket."""
        storage_client = storage.Client.from_service_account_json(
        self.APIKEY)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_name)

        blob.download_to_filename(destination_name)

        print(('Blob {} downloaded to {}.'.format(
            source_name,
            destination_name)))

    def getTRData(self,name):
        return pd.read_gbq("SELECT * FROM [simulations.{}]".format(name), self.projectID, private_key=self.APIKEY)

    def getHDF5Data(self, name, bucket_name = 'quixotic_bucket'):
        if (not os.path.isfile("tempStorage_{}.h".format(name))):
            print("File Downloading...")
            self.download_blob(bucket_name,'dataStore_{}'.format(name),"tempStorage_{}.h".format(name))
        else:
            print("File Exists")
        print("{} Downloaded".format(name))
        f = h5py.File("tempStorage_{}.h".format(name),'r')
        return f
