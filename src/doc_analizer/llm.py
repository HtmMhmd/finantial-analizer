import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


load_dotenv(override=True, dotenv_path=".env")

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_llm(llm_type: str = "groq"):

    if llm_type == "groq" and groq_api_key:
        llm = ChatGroq(
            model="groq-alpha-llama3-70b-chat",
            temperature=0,
            groq_api_key=groq_api_key,
    )

    elif llm_type == "openai" and openai_api_key:
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0,
            openai_api_key=openai_api_key,
    )
    else:
        raise ValueError("No valid LLM API key found in environment variables.")
    return llm