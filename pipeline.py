import os
import json
import logging
from datetime import datetime
from query_handler import query_models

# Define directories
STORIES_DIR = "stories"
LOG_FILE = "story_pipeline.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def sanitize_title(title):
    """Sanitize story title for use in file names."""
    title = " ".join(title.split()[:5])  # Limit to 5 words
    return "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()

def save_to_file(file_path, content, mode="w"):
    """Save content to a file safely."""
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            f.writelines(content)
        logging.info(f"Saved content to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save file {file_path}: {e}")
        raise RuntimeError(f"File save error: {e}")

def load_from_file(file_path):
    """Load content from a file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def generate_new_story(brief_text, num_episodes):
    """Generate a new story based on a brief idea with multiple episodes."""
    if not brief_text.strip():
        return "Error: Story idea cannot be empty."

    logging.info(f"Generating story for idea: {brief_text}")

    # Generate a unique story title
    story_title = sanitize_title(
        query_models(f"Generate a catchy story title (3-5 words) about: {brief_text}")
    )

    if not story_title:
        return "Error: Could not generate a valid story title."

    story_path = os.path.join(STORIES_DIR, story_title)
    os.makedirs(story_path, exist_ok=True)

    logging.info(f"Created directory for story: {story_path}")

    all_content = []
    model_summary = []

    for ep in range(1, num_episodes + 1):
        try:
            episode_prompt = f"Write Episode {ep} for the story '{story_title}'. Base it on this plot: {brief_text}"
            episode_content = query_models(episode_prompt, use_chunks=True)

            if not episode_content:
                logging.warning(f"Episode {ep} generation failed.")
                continue

            all_content.append(f"\n\nEpisode {ep}:\n{episode_content}")

            # Summarize the episode for memory tracking
            episode_summary = query_models(f"Summarize key plot points of Episode {ep} for continuity.")
            model_summary.append(f"\nEpisode {ep} Summary:\n{episode_summary}")

        except Exception as e:
            logging.error(f"Error generating Episode {ep}: {e}")

    # Save the user-readable story
    save_to_file(os.path.join(story_path, "story_user.txt"), all_content)
    save_to_file(os.path.join(story_path, "story_model.txt"), model_summary)

    logging.info(f"Story '{story_title}' generated successfully.")
    return story_title

def generate_new_episode(story_title, character_input=""):
    """Generate a new episode for an existing story, considering additional characters."""
    story_path = os.path.join(STORIES_DIR, story_title)
    user_story_path = os.path.join(story_path, "story_user.txt")
    model_story_path = os.path.join(story_path, "story_model.txt")

    if not os.path.exists(user_story_path) or not os.path.exists(model_story_path):
        logging.error(f"Story files missing for: {story_title}")
        return "Error: Story files not found."

    # **Retrieve past 3 episodes** dynamically instead of loading all memory
    past_episodes = load_from_file(user_story_path)
    if past_episodes:
        episode_list = past_episodes.strip().split("\n\n")
        memory_chunk = "\n\n".join(episode_list[-3:])  # Last 3 episodes only
    else:
        memory_chunk = ""

    prompt = f"Continue the story '{story_title}'. Maintain character arcs and coherence.\nMemory:\n{memory_chunk}"
    if character_input.strip():
        prompt += f"\nInclude these new character(s): {character_input}."

    new_episode = query_models(prompt, use_chunks=True)

    if not new_episode:
        logging.error(f"Failed to generate a new episode for '{story_title}'.")
        return "Error: Failed to generate new episode."

    # Save the new episode
    save_to_file(user_story_path, f"\n\n{new_episode}", mode="a")

    # Update model memory
    episode_summary = query_models(f"Summarize key plot points of this new episode for model memory.")
    save_to_file(model_story_path, f"\nNew Episode Summary:\n{episode_summary}", mode="a")

    logging.info(f"New episode added to '{story_title}'.")
    return new_episode.strip()
