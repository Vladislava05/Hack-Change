import os
from pydantic import BaseSettings
from sqlalchemy import create_engine, Table, Column, Integer, String, LargeBinary, MetaData, insert, select
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import psycopg2

load_dotenv()
user_name = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("PORT")
db_name = os.environ.get("POSTGRES_PROD_DB_NAME")
load_dotenv(".env")


engine = create_engine(f"postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{db_name}") 
metadata = MetaData()

music = Table('music', metadata,
  Column('id', Integer, primary_key=True, autoincrement=True),
  Column('name', String(255)),
  Column('author', String(255)),
  Column('music_file', LargeBinary),
  Column('genre', Integer)
) # создаём таблицу с полями id, name, author, music_file 

metadata.create_all(engine)

import os

directory = '/home/knyazev_artem/recommendation_system/test_content'
Session = sessionmaker(bind=engine)
session = Session()



# Проходимся по директории test_content
for filename in os.listdir(directory):
    # Check if the file is a music file
    if filename.endswith('.wav'):

        words = filename.split('_')
        # Remove the file extension
        words[-1] = words[-1].split('.')[0]

        # Extract the name, author, and genre
        name = words[0]
        author = words[1]
        genre = words[2]
        genre = int(genre)
        print (name, author, genre, filename)
        with open(f'/home/knyazev_artem/recommendation_system/test_content/{filename}', 'rb') as f:
          music_file = f.read()

        # Insert the music file and its genre into the table
        session.execute(insert(music).values(name=name, author=author, music_file=music_file, genre=genre))
        session.commit()

# Commit the changes and close the session
session.close()
