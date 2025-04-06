import openai
import json
import os
from config import OPENAI_API_KEY, SMALL_MODEL, BIG_MODEL, MAX_MEMORY_EPISODES
import logging

logger = logging.getLogger(__name__)

class QueryHandler:
    def __init__(self):
        self.client = openai.Client(api_key=OPENAI_API_KEY)
        self.cache = {}  # Simple in-memory cache
    
    def generate_response(self, prompt, model_type="small", temperature=0.7, max_tokens=None):
        """Generate a response from the appropriate model with configurable parameters."""
        model = SMALL_MODEL if model_type == "small" else BIG_MODEL
        
        # Create cache key
        cache_key = f"{model}:{prompt[:50]}:{temperature}:{max_tokens}"
        
        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for query with model {model}")
            return self.cache[cache_key]
        
        try:
            # Set default max tokens based on model
            if not max_tokens:
                max_tokens = 1500 if model_type == "small" else 3000
            
            # Create system prompt based on the task
            system_prompt = "You are an expert storyteller creating engaging narrative content. Your writing is detailed, creative, and maintains consistent character development and plot coherence."
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Error generating response with {model}: {str(e)}")
            return f"Error: {str(e)}"

def query_models(prompt, model_type="small", use_chunks=False, temperature=0.7):
    """Query the appropriate model based on the task requirements."""
    handler = QueryHandler()
    
    if use_chunks and len(prompt) > 3000:
        logger.info("Using chunking strategy for long prompt")
        return process_large_prompt(prompt, model_type, temperature)
    
    return handler.generate_response(prompt, model_type, temperature)

def process_large_prompt(prompt, model_type="big", temperature=0.7):
    """Process a large prompt by breaking it into chunks."""
    handler = QueryHandler()
    
    # 1. Split the prompt into manageable chunks
    chunks = split_into_chunks(prompt, 2500)  # 2500 characters per chunk
    logger.info(f"Split prompt into {len(chunks)} chunks")
    
    # 2. Process each chunk with the small model for summarization
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        summary_prompt = f"Summarize this portion of text while retaining all key information:\n\n{chunk}"
        summary = handler.generate_response(summary_prompt, "small", temperature=0.5)
        chunk_summaries.append(summary)
        logger.info(f"Processed chunk {i+1}/{len(chunks)}")
    
    # 3. Combine the summaries
    combined_summary = "\n\n".join(chunk_summaries)
    
    # 4. Generate the final response with the preferred model
    final_prompt = f"""
    Use the following summarized context to generate your response:
    
    {combined_summary}
    
    Based on this information, please respond to the original request.
    """
    
    return handler.generate_response(final_prompt, model_type, temperature=temperature)

def split_into_chunks(text, chunk_size):
    """Split text into chunks of roughly equal size at sentence boundaries."""
    chunks = []
    current_chunk = ""
    
    # Split by sentences (simplistic approach)
    sentences = text.replace(".", ".").replace("!", "!").replace("?", "?").split(".")
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        sentence = sentence.strip() + "."
        
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def query_with_memory(prompt, memory_data, model_type="small", temperature=0.7):
    """Generate a response using memory context."""
    handler = QueryHandler()
    
    # Prepare memory context
    memory_context = format_memory_context(memory_data)
    
    # Create the full prompt with memory context
    full_prompt = f"""
    Context:
    {memory_context}
    
    With this context in mind, please respond to:
    {prompt}
    """
    
    logger.info("Querying with memory context")
    return handler.generate_response(full_prompt, model_type, temperature=temperature)

def format_memory_context(memory_data):
    """Format memory data into a coherent context for the model."""
    context_parts = []
    
    # Add basic story information
    if "story_title" in memory_data:
        context_parts.append(f"Story Title: {memory_data['story_title']}")
    
    if "concept" in memory_data:
        context_parts.append(f"Concept: {memory_data['concept']}")
    
    if "genre" in memory_data and "audience" in memory_data:
        context_parts.append(f"Genre: {memory_data['genre']}, Target Audience: {memory_data['audience']}")
    
    # Add character information
    if "characters" in memory_data and memory_data["characters"]:
        character_section = ["Characters:"]
        for name, desc in memory_data["characters"].items():
            character_section.append(f"- {name}: {desc}")
        context_parts.append("\n".join(character_section))
    
    # Add previous episode summaries (limited by MAX_MEMORY_EPISODES)
    if "episode_summaries" in memory_data and memory_data["episode_summaries"]:
        summaries = memory_data["episode_summaries"]
        summaries_split = summaries.split("\n\n")
        
        # Take the most recent MAX_MEMORY_EPISODES
        recent_summaries = summaries_split[-MAX_MEMORY_EPISODES:] if len(summaries_split) > MAX_MEMORY_EPISODES else summaries_split
        
        context_parts.append("Previous Episode Summaries:")
        context_parts.append("\n".join(recent_summaries))
    
    # Add story bible highlights if available
    if "story_bible" in memory_data and memory_data["story_bible"]:
        # Extract just the important parts from the story bible
        bible_prompt = f"""
        Extract the most crucial elements from this story bible that would be necessary
        for maintaining consistency in future episodes. Focus on themes, character arcs,
        and major plot points:
        
        {memory_data["story_bible"][:2000]}  # Limit length for efficiency
        """
        
        bible_summary = query_models(bible_prompt, "small", temperature=0.5)
        context_parts.append("Story Bible Highlights:")
        context_parts.append(bible_summary)
    
    return "\n\n".join(context_parts)