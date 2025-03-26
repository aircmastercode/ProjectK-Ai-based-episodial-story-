# pipeline.py - Story Processing Logic

from query_handler import query_models
import os

def generate_new_story(brief_text):
    """Generate a new story based on a brief input and save it."""
    story_title = query_models(f"Generate a short and catchy title (3-5 words) for a story about: {brief_text}")
    story_title = " ".join(story_title.split()[:5])  # Ensures max 5 words
    story_title = "".join(c for c in story_title if c.isalnum() or c in (" ", "_", "-"))  # Removes special characters
    
    full_story = query_models(f"Write the first episode of a multi-episode story titled '{story_title}'. Ensure strong character arcs and an engaging narrative.")
    return story_title.strip(), full_story.strip()


def generate_new_episode(story_title, character_input=""):
    """Generate a new episode for an existing story, incorporating new characters if provided."""
    story_path = f"stories/{story_title}.txt"
    
    if not os.path.exists(story_path):
        return "Error: Story file not found."
    
    with open(story_path, "r") as f:
        previous_content = f.read()
    
    prompt = f"Continue the story '{story_title}'. Maintain existing character arcs, introduce new elements, and ensure coherence. Here’s what has happened so far: {previous_content[-2000:]}."
    
    if character_input.strip():
        prompt += f" Also, include the following new character(s) in this episode: {character_input}."
    
    new_episode = query_models(prompt)
    return new_episode.strip()
