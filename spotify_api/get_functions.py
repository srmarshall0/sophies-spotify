import json 
import pandas as pd 
import os 
import spotipy

# get environment vars
username = os.environ.get("SP_USERNAME")
client_id = os.environ.get("SP_CLIENT_ID")
client_secret = os.environ.get("SP_CLIENT_SECRET")
redirect_uri = os.environ.get("SP_REDIRECT_URI")

# retrieve API token
def get_token(scope):
    token = spotipy.util.prompt_for_user_token(username=username,
                                               scope=scope,
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri)
    return token

# create spotify object
def get_sp(token):
    import spotipy
    sp = spotipy.Spotify(auth=token)
    return sp

# retrieve listening history as df
def get_listening_history():

    # retrieve token + create spotify object
    token = get_token(scope ="user-read-recently-played")
    sp = get_sp(token=token)

    # fetch data -- format into df 
    recently_played = sp.current_user_recently_played()
    str_recently_played = json.dumps(recently_played)
    dict_recently_played = json.loads(str_recently_played)
    flat_recently_played = pd.json_normalize(dict_recently_played, record_path="items")
    df_recently_played = pd.DataFrame(flat_recently_played)

    # format columns 
    df_recently_played.columns = df_recently_played.columns.str.replace(".", "__")

    # add if condition to remove context column 
    if "context" in df_recently_played.columns:
        df_recently_played = df_recently_played.drop(["context"], axis=1)

    columns_to_convert = ["played_at", 
                          "track__album__album_type",
                          "track__album__artists",
                          "track__album__available_markets",
                          "track__album__external_urls__spotify",
                          "track__album__href",
                          "track__album__id",
                          "track__album__images",
                          "track__album__name",
                          "track__album__release_date",
                          "track__album__release_date_precision",
                          "track__album__type",
                          "track__album__uri",
                          "track__artists",
                          "track__available_markets",
                          "track__external_ids__isrc",
                          "track__external_urls__spotify",
                          "track__href",
                          "track__id",
                          "track__name",
                          "track__preview_url",
                          "track__type",
                          "track__uri",
                          "context__type",
                          "context__href",
                          "context__external_urls__spotify",
                          "context__uri"]

    # coerce column types
    df_recently_played[columns_to_convert] = df_recently_played[columns_to_convert].astype("str")

    # remove incorrectly formatted years 
    df_recently_played = df_recently_played[df_recently_played["track__album__release_date_precision"] != "year"]

    return df_recently_played