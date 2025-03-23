from query_handler import query_models

def generate_story(plot):
    """
    Generates a story by querying multiple models using structured prompts.
    """
    result = query_models(plot)
    return result