import os
from typing import Type

import requests
from crewai.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from doc_analizer import llm


class PushoverNotificationInput(BaseModel):
    """Input schema for the Pushover notifier tool."""

    title: str = Field(..., description="Short title for the Pushover notification.")
    message: str = Field(..., description="Plain text content to format into HTML.")


class PushoverNotifier(BaseTool):
    """Formats content via an LLM and delivers it to Pushover."""

    name: str = "pushover_notifier"
    description: str = (
        "Formats notification content into HTML using an LLM before sending the payload through"
        " the Pushover API."
    )
    args_schema: Type[BaseModel] = PushoverNotificationInput

    def __init__(self, formatter_llm: str | None = None) -> None:
        super().__init__()
        self._user = os.getenv("PUSHOVER_USER")
        self._token = os.getenv("PUSHOVER_TOKEN")
        self._api_url = os.getenv("PUSHOVER_URL", "https://api.pushover.net/1/messages.json")
        formatter_choice = formatter_llm or os.getenv("PUSHOVER_FORMATTER_LLM", "openai")
        self._formatter_llm = llm.get_llm(formatter_choice)

    def _format_message(self, title: str, message: str) -> str:
        """Use the configured LLM to convert plain text into HTML."""

        system_prompt = (
            "You are an assistant that transforms plain summaries into concise HTML snippets."
            " Use semantic tags such as <p>, <ul>, <li>, and <strong>, avoid <html> or <body> wrappers,"
        )

        human_prompt = (
            f"Title: {title}\n\n"
            "Format the following notification for stakeholders into HTML.\n\n"
            f"Content:\n{message}"
        )
        response = self._formatter_llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        if hasattr(response, "content"):
            return str(response.content).strip()
        return str(response).strip()

    def _run(self, title: str, message: str) -> str:
        formatted_message = self._format_message(title, message)
        print(formatted_message)
        payload = {
            "token": self._token,
            "user": self._user,
            "title": title,
            "message": formatted_message,
            "html": 1,
            "priority": 0,
        }
        response = requests.post(self._api_url, data=payload, timeout=30)
        response.raise_for_status()

        return f"Pushover notification sent successfully (status={response.status_code})."

