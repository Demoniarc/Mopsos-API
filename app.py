# -*- coding: utf-8 -*-

# 1. Library imports
import uvicorn
from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader, APIKeyQuery
import numpy as np
import pandas as pd
from google.cloud import bigquery
from google.cloud import firestore
from google.oauth2 import service_account
import time
from datetime import datetime, timezone
import os
import json

api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def load_credentials_from_file(json_file_path):
    with open(json_file_path) as json_file:
        credentials_info = json.load(json_file)

    # Créer l'objet Credentials avec les informations de la clé JSON
    credentials = service_account.Credentials.from_service_account_info(credentials_info)

    return credentials

def get_firestore_client(credentials):
    # Passer les credentials à l'initialisation du client Firestore
    db = firestore.Client(credentials=credentials)
    return db


def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    json_file_path = "/etc/secrets/tranquil-lore-396810-a584b05b6b14.json"
    credentials = load_credentials_from_file(json_file_path)
    db = get_firestore_client(credentials)
    collection_ref = db.collection('collection api')

    timestamp_now = int(datetime.now(timezone.utc).timestamp())

    existing_doc_1 = collection_ref.where('api_key', '==', api_key_query).get()
    if existing_doc_1:
        data_1 = existing_doc_1[0].to_dict()
        time_value_1 = data_1.get('expiry_date')

    existing_doc_2 = collection_ref.where('api_key', '==', api_key_header).get()
    if existing_doc_2:
        data_2 = existing_doc_2[0].to_dict()
        time_value_2 = data_2.get('expiry_date')

    if existing_doc_1 and time_value_1>=timestamp_now:
        return api_key_query
    if existing_doc_2 and time_value_2>=timestamp_now:
        return api_key_header
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired or missing API Key",
    )

app = FastAPI()

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'/'}

@app.get('/oceanprotocol')
def get_ocean_protocol_data(api_key: str = Security(get_api_key)):
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.ocean_protocol'
    query = f"SELECT * FROM `{table_id}` ORDER BY date ASC"
    query_job = client.query(query)
    results = query_job.result(page_size=10000)
    rows = [dict(row) for row in results]

    return rows

@app.get('/dimitra')
def get_dimitra_data(api_key: str = Security(get_api_key)):
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.dimitra'
    query = f"SELECT * FROM `{table_id}` ORDER BY date ASC"
    query_job = client.query(query)
    results = query_job.result(page_size=10000)
    rows = [dict(row) for row in results]

    return rows

@app.get('/numerai')
def get_numerai_data(api_key: str = Security(get_api_key)):
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.numerai'
    query = f"SELECT * FROM `{table_id}` ORDER BY date ASC"
    query_job = client.query(query)
    results = query_job.result(page_size=10000)
    rows = [dict(row) for row in results]

    return rows

@app.get('/anyone')
def get_anyone_data(api_key: str = Security(get_api_key)):
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.anyone'
    query = f"SELECT * FROM `{table_id}` ORDER BY date ASC"
    query_job = client.query(query)
    results = query_job.result(page_size=10000)
    rows = [dict(row) for row in results]

    return rows

@app.get('/genomes')
def get_genomes_data(api_key: str = Security(get_api_key)):
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.genomes'
    query = f"SELECT * FROM `{table_id}` ORDER BY date ASC"
    query_job = client.query(query)
    results = query_job.result(page_size=10000)
    rows = [dict(row) for row in results]

    return rows

    
# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload