import os
import re
from query_handler import query_models

def generate_new_story(brief_text):
    """Generate a new story based on a brief input and save it."""

    # Step 1: Request a STRICT title without extra AI-generated explanations
    response = query_models(
        f"Generate ONLY a short and meaningful story title (3-5 words) for: {brief_text}. "
        f"Return ONLY the title, no extra text, no explanations."
    )

    # Step 2: Extract the title correctly without extra text
    match = re.search(r"^[\"']?([\w\s-]{3,50})[\"']?$", response.strip(), re.MULTILINE)
    story_title = match.group(1) if match else "Untitled_Story"

    # Step 3: Clean title (remove unwanted characters)
    story_title = "".join(c for c in story_title if c.isalnum() or c in (" ", "_", "-")).strip()

    # Step 4: Generate ONLY Episode 1, ensuring it follows the given theme
    full_story = query_models(
        f"Write **Episode 1** of a multi-episode story. "
        f"The story is titled '{story_title}', and it must follow this exact theme: {brief_text}. "
        f"Ensure strong character development, immersive setting, and compelling plot. "
        f"Do NOT summarize or explain. **Return ONLY Episode 1 in a narrative format.**"
    )

    # Step 5: Save the story
    story_path = f"stories/{story_title}.txt"
    os.makedirs("stories", exist_ok=True)  # Ensure folder exists

    with open(story_path, "w") as f:
        f.write(full_story.strip())

    return story_title, full_story.strip()


def generate_new_episode(story_title, character_input=""):
    """Generate a new episode for an existing story, keeping continuity."""

    story_path = f"stories/{story_title}.txt"

    # Step 1: Check if story exists
    if not os.path.exists(story_path):
        return "Error: Story file not found."

    # Step 2: Read previous content (only the last 2000 characters for context)
    with open(story_path, "r") as f:
        previous_content = f.read()

    # Step 3: Generate Episode 2+ while maintaining coherence
    prompt = (
        f"Write the **next episode** of the story titled '{story_title}'. "
        f"Maintain existing character arcs, introduce new elements, and ensure coherence. "
        f"Here’s what has happened so far:\n\n{previous_content[-2000:]}\n\n"
        f"Now, write **only** the next episode in a natural story format."
    )

    if character_input.strip():
        prompt += f"\n\nAlso, introduce the following new character(s): {character_input}."

    # Step 4: Generate new episode
    new_episode = query_models(prompt)

    # Step 5: Append new episode to the file
    with open(story_path, "a") as f:
        f.write("\n\n" + new_episode.strip())

    return new_episode.strip()