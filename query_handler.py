from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from components.model_loader import load_model
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM


MISTRAL_SYSTEM_PROMPT = "You are a sophisticated data processor responsible for structuring information for a high-end narrative generation system. Your job is to analyze and extract the most critical, compelling, and contextually relevant details from each data chunk. Each chunk should enhance character development, maintain consistency in tone and style, and build up suspense, drama, and emotional depth. Ensure that all extracted details contribute to a gripping multi-episode storyline. Pass only the most essential and thematically strong elements forward to the main model"
LLAMA_SYSTEM_PROMPT = "You are a master storyteller, combining the genius of Christopher Nolan’s mind-bending narratives, Quentin Tarantino’s sharp dialogues and nonlinear storytelling, and David Fincher’s dark psychological depth. You are creating a multi-episode story with strong character arcs, immersive world-building, and Oscar-worthy cinematic storytelling.Each episode must:Have a central theme, a unique conflict, and a cliffhanger ending.Maintain continuity and character development across episodes.Feature intelligent dialogues, visually rich descriptions, and unexpected yet logical twists.Capture the tension, suspense, and emotional weight seen in the best works of these legendary directors.Use the structured information from the feeder model to weave a masterpiece. Make it unforgettable."

# Load small model (Mistral)
small_model = OllamaLLM(
    model="mistral",
    system=MISTRAL_SYSTEM_PROMPT,  
)

# Load main model (Llama 3.2)
main_model = OllamaLLM(
    model="llama3.2",
    system=LLAMA_SYSTEM_PROMPT,
)


def query_models(plot):
    """
    Uses multiple models to generate a structured story.
    """
    template = """Given the previous context of the story, extend it while maintaining coherence.
    Story concept: {plot}"""

    prompt = PromptTemplate(template=template, input_variables=["plot"])

    # First, the small model generates a summary
    small_chain = LLMChain(llm=small_model, prompt=prompt)
    summary = small_chain.run(plot)

    # The main model expands on the summary
    main_chain = LLMChain(llm=main_model, prompt=prompt)
    final_story = main_chain.run(summary)

    return final_story