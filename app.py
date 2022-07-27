
import pickle
import streamlit as st
import psycopg2 as ps
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

#database credentials
host_name = 'database-1.ccck6w0etvpm.us-east-1.rds.amazonaws.com'
dbname = ''
port = '5432'
username = 'postgres'
password = 'nikhilghase'
conn = None

def connect_to_db(host_name, dbname, port, username, password):
    try:
        conn = ps.connect(host=host_name, database=dbname, user=username, password=password, port=port)

    except ps.OperationalError as e:
        raise e
    else:
        print('Connected!')
        return conn

#establish a connection to db
def getdata():
    conn = connect_to_db(host_name, dbname, port, username, password)
    curr = conn.cursor()
    curr.execute("SELECT * FROM songs ")
    records = curr.fetchall()
    song_library = pd.DataFrame(records, columns=['artist', 'album', 'track_name', 'popularity', 'img_url',
       'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
       'instrumentalness', 'liveness', 'valence', 'tempo', 'text_data'])
    return song_library


song_library= getdata()

#song_library = pd.read_csv('C:/Users/nikhil/preprocessed.csv')

# Create CountVectorizer object to transform text into vector

song_vectorizer = CountVectorizer()

# Fit the vectorizer on "genres" field of song_library DataFrame
song_vectorizer.fit(song_library['text_data'])


def song_recommender(song_name):
    try:
        num_cols = ['popularity', 'danceability', 'energy', 'key', 'loudness',
                    'mode', 'speechiness', 'instrumentalness', 'liveness', 'valence', 'tempo']

        text_vec1 = song_vectorizer.transform(
            song_library[song_library['track_name'] == str(song_name)]['text_data']).toarray()

        num_vec1 = song_library[song_library['track_name'] == str(song_name)][num_cols].to_numpy()
        sim_scores = []
        for index, row in song_library.iterrows():
            name = row['track_name']
            text_vec2 = song_vectorizer.transform(
                song_library[song_library['track_name'] == name]['text_data']).toarray()
            num_vec2 = song_library[song_library['track_name'] == name][num_cols].to_numpy()
            text_sim = cosine_similarity(text_vec1, text_vec2)[0][0]

            # Calculate cosine similarity using numerical vectors
            num_sim = cosine_similarity(num_vec1, num_vec2)[0][0]
            sim = (text_sim + num_sim) / 2
            sim_scores.append(sim)
        song_library['similarity'] = sim_scores

        # Sort DataFrame based on "similarity" column
        song_library.sort_values(by=['similarity', 'popularity'], ascending=[False, False], inplace=True)
        recommended_songs = song_library[['track_name']][1:11].values.flatten()
        image =  song_library[["img_url"]][1:11].values.flatten()
        return recommended_songs,image
    except:
        print('{} not found in songs library.'.format(song_name))


st.header('Song Recommender System')
songs = pickle.load(open('song_names.pkl','rb'))

selected_movie = st.selectbox(
    "Type or select a song from the dropdown",
    songs


)
if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = song_recommender(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])
