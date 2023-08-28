from sqlalchemy import create_engine, Column, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from get_functions import get_listening_history
import datetime
import os

# retrieve credentials from env
connection_credentials = os.environ.get("SP_CONNECTION_CREDENTIALS")

# create engine
engine = create_engine(connection_credentials)

print("engine created")
print("building session")

# build session
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# create table model 
class ListeningHistory(Base):
    __tablename__ = "listening_history"
    played_at = Column(DateTime, primary_key=True)

# grab maxtime
query_output__maxtime = session.query(func.max(ListeningHistory.played_at))
query_output__maxtime = str(query_output__maxtime[0])

print("maxtime retrieved")

# format maxtime
form_maxtime = query_output__maxtime[19:-3]
form_maxtime = [int(x) for x in form_maxtime.split(",")]
form_maxtime = datetime.datetime(*form_maxtime)

# create object to filter by 
filter_by = form_maxtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

print("filter_by variable created")
print("retrieving listening history data")

user_recently_played = get_listening_history()

print("data retrieved")
print("filtering data")

only_new_user_recently_played = user_recently_played[user_recently_played["played_at"] > filter_by][:-1]

print("insterting to postgres table")

only_new_user_recently_played.to_sql("listening_history", engine, if_exists="append", index=False)

print("data successfully added")