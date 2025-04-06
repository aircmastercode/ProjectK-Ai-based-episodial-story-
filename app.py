import streamlit as st
import os
from pipeline import generate_new_story, generate_new_episode, get_story_content

def get_existing_stories():
    """Fetch existing story titles from saved story directories."""
    os.makedirs("stories", exist_ok=True)  # Ensure the stories directory exists
    stories = [d for d in os.listdir("stories") if os.path.isdir(os.path.join("stories", d))]
    return stories

def main():
    st.set_page_config(page_title="AI Episodic Storyteller", layout="wide")
    
    st.title("📚 AI-Powered Episodic Storytelling")
    st.sidebar.image("https://via.placeholder.com/150x80?text=Story+AI", width=150)
    
    # App sections in sidebar
    app_mode = st.sidebar.radio(
        "Choose Mode:",
        ["Create Story", "Continue Story", "Read Story"]
    )
    
    if app_mode == "Create Story":
        create_story_ui()
    elif app_mode == "Continue Story":
        continue_story_ui()
    elif app_mode == "Read Story":
        read_story_ui()

def create_story_ui():
    st.header("📝 Create a New Story")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Story Parameters")
        brief_text = st.text_area(
            "Enter your story concept:",
            height=150,
            placeholder="e.g., A detective with the ability to see 5 minutes into the future tries to solve a case where this power becomes unreliable..."
        )
        
        genre = st.selectbox("Select genre:", 
            ["Science Fiction", "Fantasy", "Mystery", "Romance", "Thriller", "Comedy", "Drama", "Adventure"]
        )
        
        target_audience = st.selectbox("Target audience:", 
            ["Children", "Young Adult", "Adult", "All Ages"]
        )
    
    with col2:
        st.subheader("Episode Settings")
        num_episodes = st.slider("Initial episodes:", 1, 5, 2)
        episode_length = st.select_slider(
            "Episode length:",
            options=["Short", "Medium", "Long"],
            value="Medium"
        )
        
        # Advanced settings (collapsible)
        with st.expander("Advanced Settings"):
            model_quality = st.select_slider(
                "Model quality:",
                options=["Standard", "Premium"],
                value="Standard",
                help="Premium uses a more advanced model but may take longer"
            )
            
            creativity = st.slider(
                "Creativity level:",
                0.0, 1.0, 0.7,
                help="Higher values mean more creative but possibly less coherent stories"
            )
    
    if st.button("🪄 Generate Story", use_container_width=True):
        if brief_text.strip():
            with st.spinner("Creating your story... this may take a minute"):
                try:
                    title = generate_new_story(
                        brief_text, 
                        num_episodes,
                        genre=genre,
                        audience=target_audience,
                        length=episode_length,
                        model_quality="big" if model_quality == "Premium" else "small",
                        temperature=creativity
                    )
                    
                    if title:
                        st.success(f"✅ Story '{title}' created with {num_episodes} episodes!")
                        st.session_state.current_story = title
                        st.balloons()
                        
                        # Show button to view the story
                        if st.button("Read Your Story Now"):
                            st.switch_page("Read Story")
                    else:
                        st.error("⚠️ Story generation failed. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a story concept to continue.")

def continue_story_ui():
    st.header("📖 Continue an Existing Story")
    
    story_titles = get_existing_stories()
    
    if not story_titles:
        st.warning("No existing stories found. Create a new story first.")
        return
    
    selected_story = st.selectbox("Select a story to continue:", story_titles)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        character_input = st.text_area(
            "New characters to introduce (optional):",
            placeholder="e.g., Marina, a hacker with a mysterious past who knows more than she lets on..."
        )
        
        plot_direction = st.text_area(
            "Plot direction (optional):",
            placeholder="e.g., Introduce a twist where the main character discovers a betrayal..."
        )
    
    with col2:
        model_quality = st.select_slider(
            "Model quality:",
            options=["Standard", "Premium"],
            value="Premium"
        )
        
        with st.expander("Advanced Settings"):
            maintain_tone = st.checkbox("Maintain existing tone", value=True)
            creativity = st.slider("Creativity level:", 0.0, 1.0, 0.7)
    
    if st.button("🚀 Generate Next Episode", use_container_width=True):
        with st.spinner("Crafting the next chapter of your story..."):
            try:
                new_episode = generate_new_episode(
                    selected_story, 
                    character_input,
                    plot_direction=plot_direction,
                    model_quality="big" if model_quality == "Premium" else "small",
                    maintain_tone=maintain_tone,
                    temperature=creativity
                )
                
                if new_episode:
                    st.success("✅ New episode added successfully!")
                    
                    with st.expander("📜 Preview New Episode", expanded=True):
                        st.markdown(new_episode)
                    
                    if st.button("Read Full Story"):
                        st.session_state.current_story = selected_story
                        st.switch_page("Read Story")
                else:
                    st.error("⚠️ Episode generation failed. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def read_story_ui():
    st.header("📚 Read Your Stories")
    
    story_titles = get_existing_stories()
    
    if not story_titles:
        st.warning("No stories found. Create a new story first.")
        return
    
    # If coming from another page with a selected story
    current_story = st.session_state.get("current_story", story_titles[0])
    selected_story = st.selectbox("Select a story to read:", story_titles, index=story_titles.index(current_story) if current_story in story_titles else 0)
    
    story_content = get_story_content(selected_story)
    if story_content:
        # Parse episodes
        episodes = story_content.split("\n\nEpisode ")
        title_section = episodes[0]
        actual_episodes = ["Episode " + ep for ep in episodes[1:]]
        
        # Display title
        st.subheader(selected_story.replace("_", " ").title())
        
        # Episode selection
        if len(actual_episodes) > 1:
            episode_options = ["All Episodes"] + [f"Episode {i+1}" for i in range(len(actual_episodes))]
            selected_episode = st.selectbox("Choose episode:", episode_options)
        else:
            selected_episode = "All Episodes"
        
        # Display episodes
        if selected_episode == "All Episodes":
            for i, episode in enumerate(actual_episodes):
                with st.expander(f"Episode {i+1}", expanded=i==0):
                    st.markdown(episode)
        else:
            episode_index = int(selected_episode.split(" ")[1]) - 1
            st.markdown(actual_episodes[episode_index])
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Continue This Story"):
                st.session_state.current_story = selected_story
                st.switch_page("Continue Story")
        with col2:
            if st.button("📊 Story Analytics"):
                # Basic analytics could be added here
                st.info("Story analytics feature coming soon!")
    else:
        st.error("Could not load story content.")

if __name__ == "__main__":
    main()