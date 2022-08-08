import json
import requests
import re
import pandas as pd
import os

pd.set_option('display.max_columns', None)


def create_oscar_df():
    df = pd.DataFrame(columns=('year', 'category', 'movie', 'result', 'rating'))
    return df


def get_oscar_movies(year, wa_key):
    # Get request (API)
    yearstr = " " + str(year)
    url = "http://api.wolframalpha.com/v2/query?appid=" + wa_key + "&input=academy awards nominees" + yearstr + "&includepodid=Result&output=json"
    payload = {}
    headers = {}
    nominees_from_api = get_request(url, headers, payload)
    return nominees_from_api


def get_request(url, headers, payload):
    response = requests.request("GET", url, headers=headers, data=payload)
    payload = response.text
    # Load method - Read Json decode to python
    nominees_from_api = json.loads(payload)
    return nominees_from_api


def populate_oscar_df(first_year, last_year, df, wa_key):
    last_year_for_range = last_year + 1
    for year in range(first_year, last_year_for_range):
        nominees = get_oscar_movies(year, wa_key)
        # Extract full data
        movie_text = nominees['queryresult']['pods'][0]['subpods'][0]['img']['title']
        # Extract best movie
        movie_list = movie_text.replace("nominees", "").split("\n")
        winner = re.search("(?:winner \|)(.+)(?:(\(produced.+))", movie_list[0])
        winner = winner.group(1)
        # Add year and best movie to DF
        df = df.append({'year': year, 'category': 'Best Picture', 'movie': winner, 'result': 'winner'},
                       ignore_index=True)
        # Extract nominees & add to the DF
        row_index = df.index[df['year'] == year].tolist()
        for i in range(1, len(movie_list)):
            nominee = re.search("(?:\|)(.+)(?:(\(produced.+))", movie_list[i])
            nominee = nominee.group(1)
            df = df.append({'year': year, 'category': 'Best Picture', 'movie': nominee, 'result': 'nominee'},
                           ignore_index=True)
    return df


def get_movie_id(title, imdbkey):
    # Get request (API)
    url = "https://imdb-api.com/en/API/Search/" + imdbkey + "/" + title
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    # Response (payload(text), headers, status)
    payload = response.text
    # Load method - Read Json decode to python
    full_data = json.loads(payload)
    return full_data['results'][0]['id']


def get_movie_rating(id, imdbkey):
    # Get request (API)
    url = "https://imdb-api.com/en/API/Ratings/" + imdbkey + "/" + id
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    # Response (payload(text), headers, status)
    payload = response.text
    # Load method - Read Json decode to python
    full_data = json.loads(payload)
    return full_data['imDb']


def oscar_movie_ratings(first_year, last_year, wa_key, imdbkey):
    df = create_oscar_df()
    df_oscar = populate_oscar_df(first_year, last_year, df, wa_key)
    for i in range(len(df_oscar)):
        try:
            title = df_oscar['movie'].iloc[i]
            id = get_movie_id(title, imdbkey)
            rating = get_movie_rating(id, imdbkey)
            df_oscar.at[i, 'rating'] = rating
        except:
            df_oscar.at[i, 'rating'] = "No rating"
    return print(df_oscar)


wa_key = os.getenv('WA_KEY')
imdbkey = os.getenv('IMDB_KEY')
oscar_list_first_year = 1998
oscar_list_last_year = 1998
oscar_movie_ratings(oscar_list_first_year, oscar_list_last_year, wa_key, imdbkey)
