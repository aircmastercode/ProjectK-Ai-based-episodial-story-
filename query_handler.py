import openai
import os
from config import OPENAI_API_KEY, SMALL_MODEL, BIG_MODEL

class QueryHandler:
    def __init__(self):
        self.client = openai.Client(api_key=OPENAI_API_KEY)

    def generate_response(self, prompt, model_type="small"):
        model = SMALL_MODEL if model_type == "small" else BIG_MODEL

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are an AI storytelling assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

def query_models(prompt, model_type="small", use_chunks=False):
    handler = QueryHandler()
    
    if model_type == "big" and use_chunks:
        # Step 1: Use the small model to summarize data in chunks
        chunked_summary = handler.generate_response(
            f"Summarize the following information for the larger model:\n\n{prompt}",
            model_type="small"
        )

        # Step 2: Pass the summarized chunks to the big model
        final_response = handler.generate_response(
            f"Use this summarized context to continue the story:\n\n{chunked_summary}",
            model_type="big"
        )
        return final_response

    return handler.generate_response(prompt, model_type)
