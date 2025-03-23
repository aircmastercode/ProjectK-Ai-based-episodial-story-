import streamlit as st
from pipeline import generate_story

st.set_page_config(page_title="AI Storyteller", layout="wide")

st.title("📖 AI Storyteller")

user_input = st.text_area("Enter a brief plot or concept:", height=150)

if st.button("Generate Story"):
    if user_input.strip():
        response = generate_story(user_input)
        st.subheader("Generated Story:")
        st.write(response)
    else:
        st.warning("Please enter a plot or concept before generating.")