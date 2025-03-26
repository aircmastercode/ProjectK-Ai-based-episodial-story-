# query_handler.py - Handles LLM Queries and Chunk Processing

from langchain_ollama import OllamaLLM

# Initialize the small and main models
small_model = OllamaLLM(model="mistral", base_url="http://localhost:11434", system="use_gpu:true")
main_model = OllamaLLM(model="llama3", base_url="http://localhost:11434", system="use_gpu:true")

def query_models(prompt):
    """Handles querying of both models and manages chunking efficiently."""
    # Step 1: Use the small model to preprocess the request
    small_summary = small_model.invoke(f"Summarize key points for better chunk processing: {prompt}")
    
    # Step 2: Break content into optimized chunks with overlapping context
    chunks = chunk_text(small_summary, chunk_size=500, overlap=100)
    
    # Step 3: Feed chunks sequentially to the main model
    final_story = ""
    for chunk in chunks:
        response = main_model.invoke(f"Ensure story consistency and coherence: {chunk}")
        final_story += response + "\n"
    
    return final_story.strip()


def chunk_text(text, chunk_size=500, overlap=100):
    """Improved chunking with overlapping context for better coherence."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks
