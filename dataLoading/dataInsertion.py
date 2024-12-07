# @Author : Seamus Jackson 
# dataInsertion

# Simple data insertion script for couchDB. 
# Built to insert car data from kaggle into an emtpy db. 

# Data Source:
# https://www.kaggle.com/datasets/arslaan5/explore-car-performance-fuel-efficiency-dataLinks to an external site.

# couch driver and pandas for parsing CSV file
import couchdb
import pandas as pd

import os 
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv('db_url')
DB_NAME = os.getenv('db')

try:
    # connect to couch db (this is my endpoint deployed on azure)
    couch = couchdb.Server(DB_URI)
except Error as e:
    print('something went wrong connecting to the DB', e)

try:
    # user auth for insertion
    couch.resource.credentials = ('admin', 'saluspecial')
except Error as e:
    print('issue with DB credentials', e)

# Access or create if not there
try:
    db_name = DB_NAME
    if db_name in couch: # former
        db = couch[db_name]
    else: # latter 
        db = couch.create(db_name)
except Error as e:
    print('error finding AND attempting to create DB', e)

try:
    data_for_insertion = "car_data.csv"
    car_df = pd.read_csv(data_for_insertion)

    # clean out NAN values, couchdb doesnt support them. Throws errors
    car_df.fillna("", inplace=True)

    # parse, turn rows into JSON for couch
    for _, row in car_df.iterrows():
        doc = row.to_dict() # make it a dictionary
        db.save(doc) # update the db with the new document 

    print("Insertion complete.")
except Error as e:
    print('issue loading data and inserting into db', e)
