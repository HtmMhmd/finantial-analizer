import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


load_dotenv(override=True, dotenv_path=".env")

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
openrouter_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

openrouter_headers = {
    "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", ""),
    "X-Title": os.getenv("OPENROUTER_APP_TITLE", "DocAnalizer"),
}


def _filter_headers(headers: dict[str, str]) -> dict[str, str]:
    """Remove empty header values to avoid invalid requests."""

    return {key: value for key, value in headers.items() if value}

def get_llm(llm_type: str = "groq"):

    if llm_type == "groq" and groq_api_key:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            groq_api_key=groq_api_key,
            max_retries=2,
        )

    if llm_type == "openai" and openai_api_key:
        return ChatOpenAI(
            model_name="gpt-4.1-nano",
            temperature=0,
            openai_api_key=openai_api_key,
        )

    if llm_type == "openrouter" and openrouter_api_key:
        headers = _filter_headers(openrouter_headers)
        client_kwargs = {
            "model_name": openrouter_model,
            "temperature": 0,
            "openai_api_key": openrouter_api_key,
            "base_url": openrouter_base_url,
        }
        if headers:
            client_kwargs["default_headers"] = headers
        return ChatOpenAI(**client_kwargs)

    raise ValueError("No valid LLM API key found in environment variables for the requested llm type.")