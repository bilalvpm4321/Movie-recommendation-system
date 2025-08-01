import pickle
import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")  # Full width



st.markdown("""
    <style>
    /* Global styles for the app background and text */
    body {
        /* A dark gray or black background similar to the screenshot */
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }

    /* Heading styles */
    h2, h3 {
        color: #ffffff;
        font-weight: 500;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Container for the featured items */
    .featured-container-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
        position: relative;
    }

    /* A flexbox grid to hold the items horizontally */
    .item-grid {
        display: flex;
        gap: 20px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding: 10px 0;
        scrollbar-width: none;  /* Firefox */
    }
    .item-grid::-webkit-scrollbar {
        display: none; /* Chrome, Safari */
    }

    /* Styling for a single item card */
    .item-card {
        flex: 0 0 auto;
        width: 300px; /* Adjust width as needed */
        background-color: #242424;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        text-align: center;
        padding: 20px;
    }
    .item-card:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    }

    /* Styles for the content within the card */
    .item-title {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .item-subtitle {
        font-size: 14px;
        color: #bbbbbb;
        margin-top: 0;
    }

    /* Navigation arrows */
    .arrow-button {
        background: rgba(40, 40, 40, 0.7);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 10;
        color: white;
        border: none;
    }
    .arrow-button svg {
        fill: white;
        width: 20px;
        height: 20px;
    }
    .prev-arrow {
        position: absolute;
        left: 0;
    }
    .next-arrow {
        position: absolute;
        right: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Define your data (replace with your actual data)
# featured_items = [
#     {
#         "title": "Item 1 Title",
#         "subtitle": "A short description of item 1.",
#     },
#     {
#         "title": "Item 2 Title",
#         "subtitle": "A slightly longer description for item 2.",
#     },
#     {
#         "title": "Item 3 Title",
#         "subtitle": "Details about the third item go here.",
#     }
# ]


# A simple function to generate the HTML for a single card
def create_item_card(item):
    return f"""
    <div class="item-card">
        <h4 class="item-title">{item['title']}</h4>
        <p class="item-subtitle">{item['subtitle']}</p>
    </div>
    """


# Generate HTML for all item cards
# featured_items_html = "".join([create_item_card(item) for item in featured_items])

# # Display the content
# st.markdown("<h3>Featured Items</h3>", unsafe_allow_html=True)
# st.markdown("""
#     <div class="featured-container-wrapper">
#         <button class="arrow-button prev-arrow">
#             <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
#         </button>
#         <div class="item-grid">
#             """ + featured_items_html + """
#         </div>
#         <button class="arrow-button next-arrow">
#             <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
#         </button>
#     </div>
#     """, unsafe_allow_html=True)

# st.markdown("<h3>Other Content</h3>", unsafe_allow_html=True)
# st.write("This is a section for other content that uses the same dark theme.")


# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Fetch poster with metadata
def fetch_metadata(movie_title):
    url = f"https://www.omdbapi.com/?t={movie_title}&apikey=36de685d"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True':
            poster = data['Poster'] if data['Poster'] != "N/A" else "https://via.placeholder.com/500x750.png?text=No+Poster"
            rating = data.get('imdbRating', 'N/A')
            year = data.get('Year', 'N/A')
            return poster, rating, year
    except:
        pass
    return "https://via.placeholder.com/500x750.png?text=Error", "N/A", "N/A"

# Recommend logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    results = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].title
        poster, rating, year = fetch_metadata(title)
        results.append((title, poster, rating, year))
    return results

# UI Components
st.markdown('<h1>🎬 Movie Recommender System</h1>', unsafe_allow_html=True)

selected_movie = st.selectbox(
    "🎥 Type or select a movie:",
    movies['title'].values,
    key='dropdown',
    help="Choose a movie to get similar recommendations"
)

# Show Recommendations
if st.button('✨ Show Recommendation'):
    recommendations = recommend(selected_movie)
    cols = st.columns(5)
    for idx, (title, poster, rating, year) in enumerate(recommendations):
        with cols[idx]:
            st.image(poster, use_container_width=True)
            st.markdown(f"<div class='movie-metadata'><strong>{title}</strong><br>⭐ {rating} | 📅 {year}</div>", unsafe_allow_html=True)
