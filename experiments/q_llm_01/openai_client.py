from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .adapter import InferenceClient, LLMRequest, LLMResponse


API_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_TIMEOUT_SECONDS = 60


class OpenAIResponsesClient(InferenceClient):
    """Minimal, auditable OpenAI Responses API client for Q-LLM-01.

    The client performs one real inference per ``infer`` call. It does not know
    the experiment condition, mutation hook, or harness state. The adapter is
    responsible for enforcing the model-visible information barrier before this
    client is invoked.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("Q_LLM_MODEL", DEFAULT_MODEL)
        self.timeout_seconds = timeout_seconds
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY is required for real LLM inference")

    def infer(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": self.model,
            "store": False,
            "instructions": request.system_instructions,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _render_user_input(request),
                        }
                    ],
                }
            ],
            "max_output_tokens": 64,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "rb_b_action",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": [*request.tools, "TERMINATE"],
                            }
                        },
                        "required": ["action"],
                        "additionalProperties": False,
                    },
                }
            },
        }

        http_request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
                status = response.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1000]}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"OpenAI runtime invocation failed: {type(exc).__name__}: {exc}") from exc

        if status != 200:
            raise RuntimeError(f"OpenAI API returned unexpected HTTP status {status}")

        action = _extract_action(body)
        metadata = {
            "provider": "openai",
            "api": API_URL,
            "model": body.get("model", self.model),
            "response_id": body.get("id"),
            "status": body.get("status"),
            "usage": body.get("usage"),
        }
        return LLMResponse(raw=body, action=action, metadata=metadata)


def _render_user_input(request: LLMRequest) -> str:
    """Serialize only declared model-visible state in a deterministic form."""

    document = {
        "objective": request.objective,
        "available_actions": list(request.tools),
        "current_observation": request.observation,
        "history": list(request.history),
        "instruction": "Return exactly one JSON object selecting the next available action or TERMINATE.",
    }
    return json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _extract_action(body: dict[str, Any]) -> str | None:
    """Extract the structured action without depending on SDK-only helpers."""

    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") != "output_text":
                continue
            text = content.get("text", "")
            parsed = json.loads(text)
            action = parsed.get("action")
            if not isinstance(action, str):
                raise ValueError("structured model response does not contain a string action")
            return None if action == "TERMINATE" else action

    raise ValueError("OpenAI response contains no structured action output")
