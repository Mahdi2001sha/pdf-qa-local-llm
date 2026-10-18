"""Talks to the local Ollama server. Swap this file to use a different LLM provider."""
import requests

from config import EMBED_MODEL, LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT_SECONDS, OLLAMA_URL


class LLMError(Exception):
    """Raised when the LLM server is unreachable or returns an error."""


def _post(path: str, payload: dict, timeout: int) -> dict:
    try:
        response = requests.post(f"{OLLAMA_URL}{path}", json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError as exc:
        raise LLMError("Cannot reach Ollama. Make sure it is running.") from exc
    except requests.HTTPError as exc:
        # Ollama explains what is wrong in the response body - show it.
        try:
            detail = exc.response.json().get("error", "")
        except ValueError:
            detail = exc.response.text[:300]
        raise LLMError(f"Ollama error {exc.response.status_code}: {detail or exc}") from exc
    except requests.RequestException as exc:
        raise LLMError(f"Ollama error: {exc}") from exc


def get_status() -> dict:
    """Report whether Ollama is up and which of our models are installed."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        response.raise_for_status()
        installed = {m["name"] for m in response.json().get("models", [])}
    except requests.RequestException:
        return {"ollama": False, "llm_model": LLM_MODEL, "llm_ready": False,
                "embed_model": EMBED_MODEL, "embed_ready": False}

    def has(name: str) -> bool:
        return name in installed or f"{name}:latest" in installed

    return {"ollama": True, "llm_model": LLM_MODEL, "llm_ready": has(LLM_MODEL),
            "embed_model": EMBED_MODEL, "embed_ready": has(EMBED_MODEL)}


def embed(texts: list[str]) -> list[list[float]]:
    data = _post("/api/embed", {"model": EMBED_MODEL, "input": texts}, timeout=120)
    return data["embeddings"]


def chat(messages: list[dict]) -> str:
    data = _post(
        "/api/chat",
        {"model": LLM_MODEL, "messages": messages, "stream": False,
         "options": {"temperature": LLM_TEMPERATURE}},
        timeout=LLM_TIMEOUT_SECONDS,
    )
    return data["message"]["content"].strip()
