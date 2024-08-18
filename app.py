# -*- coding: utf-8 -*-

# 1. Library imports
import uvicorn
from fastapi import FastAPI
import numpy as np
import pickle
import pandas as pd
import ccxt
from xgboost import XGBRegressor
from google.cloud import bigquery
import os
import json

app = FastAPI()

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'ez'}

@app.get('/oceanprotocol')
def get_name():
    
    credentials_path = '/etc/secrets/tranquil-lore-396810-2d54adfd3963.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigquery.Client()
    table_id = 'tranquil-lore-396810.mopsos_ai.ocean_protocol'
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