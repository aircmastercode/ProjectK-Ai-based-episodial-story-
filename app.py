# app.py - Streamlit App with New Features

import streamlit as st
from pipeline import generate_new_story, generate_new_episode
import os

def get_existing_stories():
    """Fetch existing story titles from saved .txt files"""
    os.makedirs("stories", exist_ok=True)  # Ensure the stories directory exists
    return [f.replace('.txt', '') for f in os.listdir("stories") if f.endswith(".txt")]

st.title("AI-Powered Episodic Storytelling")

# New Story Generation
st.subheader("Generate a New Story")
brief_text = st.text_area("Enter a brief idea for your new story:")
if st.button("Create Story"):
    if brief_text.strip():
        title, content = generate_new_story(brief_text)
        with open(f"stories/{title}.txt", "w") as f:
            f.write(content)
        st.success(f"Story '{title}' created! You can now add episodes.")
        st.subheader(f"📖 Generated Title: {title}")  # Display title
    else:
        st.error("Please enter a brief idea to generate a story.")

# New Episode Generation
st.subheader("Generate a New Episode")
story_titles = get_existing_stories()
if story_titles:
    selected_story = st.selectbox("Select a story to continue:", story_titles)
    character_input = st.text_area("Describe any new characters for this episode (optional):")
    if st.button("Generate Episode"):
        new_episode = generate_new_episode(selected_story, character_input)
        with open(f"stories/{selected_story}.txt", "a") as f:
            f.write(f"\n\n{new_episode}")
        st.success("New episode added successfully!")
else:
    st.warning("No stories found. Create a new story first.")

