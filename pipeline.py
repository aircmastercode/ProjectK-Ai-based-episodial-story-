import os
import re
from query_handler import query_models

def generate_new_story(brief_text):
    """Generate a new story based on a brief input and save it."""
    
    # Step 1: Generate a strict title **(3-5 words, NO extra text)**
    response = query_models(
        f"Generate ONLY a short and meaningful title (3-5 words) for a story about: {brief_text}. "
        f"Return ONLY the title, with no extra explanation."
    )

    # Step 2: Extract the title correctly **without unnecessary text**
    match = re.search(r"^[\"']?([\w\s-]{3,50})[\"']?$", response.strip(), re.MULTILINE)
    story_title = match.group(1) if match else "Untitled_Story"

    # Step 3: Sanitize title (remove special characters)
    story_title = "".join(c for c in story_title if c.isalnum() or c in (" ", "_", "-")).strip()

    # Step 4: Generate **only Episode 1** (No extra content)
    full_story = query_models(
        f"Write **Episode 1** of a **multi-episode story** titled '{story_title}'. "
        f"The story is about: {brief_text}. "
        f"Ensure strong character development, an immersive setting, and a compelling plot. "
        f"Do NOT summarize the story. **Only return Episode 1 as a narrative.**"
    )

    # Step 5: Save story
    story_path = f"stories/{story_title}.txt"
    os.makedirs("stories", exist_ok=True)  # Ensure folder exists

    with open(story_path, "w") as f:
        f.write(f"Episode 1:\n\n{full_story.strip()}")

    return story_title, full_story.strip()


def generate_new_episode(story_title, character_input=""):
    """Generate a new episode for an existing story, ensuring continuity."""
    
    story_path = f"stories/{story_title}.txt"
    
    # Step 1: Check if story exists
    if not os.path.exists(story_path):
        return "Error: Story file not found."
    
    # Step 2: Read previous content (get last 2000 characters for context)
    with open(story_path, "r") as f:
        previous_content = f.read()

    # Step 3: Determine the correct episode number
    episode_number = get_next_episode_number(previous_content)

    # Step 4: Ensure the model continues the story correctly
    prompt = (
        f"You are continuing the **ongoing** story titled '{story_title}'. "
        f"DO NOT restart the story or summarize it. Instead, write **only the next episode (Episode {episode_number})** "
        f"by continuing from the last scene.\n\n"
        f"---\n"
        f"Here’s what has happened so far (last part of previous episode):\n"
        f"{previous_content[-2000:]}\n\n"
        f"Now, write **Episode {episode_number}** and keep the story consistent."
    )

    if character_input.strip():
        prompt += f"\nAdditionally, introduce and develop the following new characters: {character_input}."

    # Step 5: Generate new episode
    new_episode = query_models(prompt)

    # Step 6: Append new episode to the file
    with open(story_path, "a") as f:
        f.write(f"\n\nEpisode {episode_number}:\n\n{new_episode.strip()}")

    return new_episode.strip()


def get_next_episode_number(content):
    """Determine the next episode number by checking the last episode in the story file."""
    matches = re.findall(r"Episode (\d+)", content)
    if matches:
        last_episode = max(map(int, matches))  # Get the highest episode number
        return last_episode + 1
    return 2  # Default to Episode 2 if no episode number is found