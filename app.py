import streamlit as st
import os
from pipeline import generate_new_story, generate_new_episode

def get_existing_stories():
    """Fetch existing story titles from saved story directories."""
    os.makedirs("stories", exist_ok=True)  # Ensure the stories directory exists
    stories = [d for d in os.listdir("stories") if os.path.isdir(os.path.join("stories", d))]

    if not stories:
        print("⚠️ No existing stories found!")
        return None

    return stories

st.title("📚 AI-Powered Episodic Storytelling")

# New Story Generation
st.subheader("📝 Generate a New Story")
brief_text = st.text_area("Enter a brief idea for your new story:")
num_episodes = st.radio("Select the number of episodes to generate initially:", [1, 2, 3, 4, 5])

if st.button("Create Story"):
    if brief_text.strip():
        try:
            title = generate_new_story(brief_text, num_episodes)
            if title:
                st.success(f"✅ Story '{title}' created with {num_episodes} episodes! You can now continue it.")
                st.subheader(f"📖 Generated Title: {title}")
            else:
                st.error("⚠️ No story title returned. Check query_models output.")
        except Exception as e:
            st.error(f"❌ Error generating story: {str(e)}")
            print(f"❌ Error: {e}")
    else:
        st.error("⚠️ Please enter a brief idea to generate a story.")

# New Episode Generation
st.subheader("📖 Generate a New Episode")
story_titles = get_existing_stories()

col1, col2 = st.columns([2, 1])
with col1:
    character_input = st.text_area("Describe any new characters for this episode (optional):")

with col2:
    if story_titles:
        selected_story = st.selectbox("Select a story to continue:", story_titles)

if st.button("Generate Next Episode"):
    try:
        new_episode = generate_new_episode(selected_story, character_input)
        if new_episode:
            st.success("✅ New episode added successfully!")
            st.subheader("📜 Generated Episode:")
            st.write(new_episode)
        else:
            st.error("⚠️ No episode generated. Check query_models output.")
    except Exception as e:
        st.error(f"❌ Error generating episode: {str(e)}")
        print(f"❌ Error: {e}")
else:
    st.warning("⚠️ No stories found. Create a new story first.")