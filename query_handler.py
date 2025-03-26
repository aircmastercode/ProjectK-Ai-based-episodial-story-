from langchain_ollama import OllamaLLM

# Initialize the small and main models
small_model = OllamaLLM(model="mistral", base_url="http://localhost:11434", system="use_gpu:true")
main_model = OllamaLLM(model="llama3", base_url="http://localhost:11434", system="use_gpu:true")

def query_models(prompt, is_new_story=True):
    """
    Handles querying of both models while ensuring AI follows the exact story concept
    and does NOT generate multiple episodes at once.
    """

    # Step 1: Process the prompt minimally with small_model (only if needed)
    refined_prompt = small_model.invoke(
        f"Refine this text for clarity while keeping its meaning exactly the same:\n\n{prompt}"
    )

    # Step 2: Define the instruction structure
    if is_new_story:
        main_prompt = (
            f"You are a professional storyteller. Write **only Episode 1** of a multi-episode story.\n"
            f"The story must strictly follow this theme: {refined_prompt}.\n"
            f"**DO NOT** summarize the story or generate multiple episodes.\n"
            f"Your output must be a well-written narrative containing only **one self-contained episode**."
        )
    else:
        main_prompt = (
            f"You are continuing a serialized story.\n"
            f"Write **only the next episode** and ensure strong continuity with past events.\n"
            f"Do not summarize or provide multiple episodes, just return **one new episode only**."
        )

    # Step 3: Generate the story (or episode)
    final_story = main_model.invoke(main_prompt)

    return final_story.strip()