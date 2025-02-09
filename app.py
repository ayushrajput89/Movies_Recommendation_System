import pickle
import streamlit as st
import requests
import time


def fetch_movie_details(movie_id):
    try:
        time.sleep(1)  # Add a delay to avoid hitting API limits
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ee2dc8b1d67713dc6d6e3f8ff9406ed5&language=en-US"
        response = requests.get(url, timeout=10)  # Set a timeout
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()
        poster_url = f"https://image.tmdb.org/t/p/w500/{data.get('poster_path', '')}" if data.get(
            'poster_path') else "https://via.placeholder.com/500x750?text=No+Image"

        return {
            "poster": poster_url,
            "title": data.get('title', 'Unknown'),
            "overview": data.get('overview', 'No description available'),
            "rating": data.get('vote_average', 'N/A'),
            "genre": ", ".join([genre['name'] for genre in data.get('genres', [])])
        }
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return {
            "poster": "https://via.placeholder.com/500x750?text=Error",
            "title": "Error",
            "overview": "Could not fetch movie details.",
            "rating": "N/A",
            "genre": "N/A"
        }


def recommend(movie):
    if movie not in movies['title'].values:
        return []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])

    recommended_movies = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended_movies.append(details)

    return recommended_movies


st.header('Movie Recommender System')

try:
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Ensure 'movie_list.pkl' and 'similarity.pkl' exist in the 'model/' folder.")
    st.stop()

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie", movie_list)

if st.button('Show Recommendation'):
    recommended_movies = recommend(selected_movie)

    if not recommended_movies:
        st.error("No recommendations found. Try another movie.")
    else:
        columns = st.columns(5)
        for col, details in zip(columns, recommended_movies):
            with col:
                st.image(details["poster"])
                st.markdown(f"**{details['title']}**")
                st.text(f"⭐ {details['rating']} | 🎭 {details['genre']}")
                st.caption(details['overview'][:100] + "...")
