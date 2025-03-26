
from langchain_ollama import OllamaLLM

# Initialize the small and main models
small_model = OllamaLLM(model="mistral", base_url="http://localhost:11434", system="use_gpu:true")
main_model = OllamaLLM(model="llama3", base_url="http://localhost:11434", system="use_gpu:true")

def query_models(prompt):
    """Handles querying of both models and manages chunking efficiently while maintaining the original story intent."""

    # Step 1: Use the small model to refine the prompt **without changing its meaning**
    small_summary = small_model.invoke(
        f"Improve the clarity of this story idea without altering its meaning: {prompt}"
    )

    # Step 2: Break content into optimized chunks with overlapping context
    chunks = chunk_text(small_summary, chunk_size=500, overlap=100)

    # Step 3: Feed chunks sequentially to the main model
    final_story = ""
    for chunk in chunks:
        main_prompt = (
            f"You are a highly skilled storyteller. You must strictly follow the given story concept "
            f"and not deviate from it.\n\n"
            f"### Story Concept: {prompt}\n\n"
            f"Now, write an engaging and coherent next part of the story with strong character development, "
            f"engaging dialogue, and vivid descriptions:\n\n"
            f"{chunk}"
        )

        response = main_model.invoke(main_prompt)
        final_story += response + "\n"

    return final_story.strip()


def chunk_text(text, chunk_size=500, overlap=100):
    """Improved chunking with overlapping context for better coherence."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks