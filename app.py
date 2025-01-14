# -*- coding: utf-8 -*-

# 1. Library imports
import uvicorn
from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader, APIKeyQuery
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import time
from datetime import datetime, timezone
from supabase import create_client, Client
import os
import json

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

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

# Montez le dossier static pour les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.svg")

# Redirect /favicon.ico to the SVG file
@app.get("/favicon.ico", include_in_schema=False)
async def redirect_favicon():
    return RedirectResponse(url="/static/favicon.svg")

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'/'}

@app.get('/project_id')
def get_project_id(api_key: str = Security(get_api_key)):

    supabase: Client = create_client(url, key)
    response = supabase.table('data') \
        .select('id') \
        .execute()
    
    unique_ids = sorted({item['id'] for item in response.data})

    return unique_ids

@app.get('/data')
def get_data(api_key: str = Security(get_api_key), project_id: str = None, start_date: str = None, end_date: str = None):
    supabase: Client = create_client(url, key)
    query = supabase.table('data').select('*').eq('id', project_id)

    if start_date:
        query = query.gte('date', start_date)
    
    if end_date:
        query = query.lte('date', end_date)

    response = query.order('date', desc=False).execute()

    return response.data
    
# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload
