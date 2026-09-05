from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .adapter import InferenceClient, LLMRequest, LLMResponse
from .fingerprint import RuntimeConfiguration, canonical_json


API_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_TIMEOUT_SECONDS = 60
MAX_OUTPUT_TOKENS = 64
STRUCTURED_OUTPUT_NAME = "rb_b_action"


class OpenAIResponsesClient(InferenceClient):
    """Minimal, auditable OpenAI Responses API client for Q-LLM-01.

    The client performs one real inference per ``infer`` call. It has no access
    to experiment condition, mutation hooks, expected repairs, or harness state.
    It treats refusal, incomplete generation, missing response identity, and
    protocol-shape violations as hard runtime failures rather than usable data.
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
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not self.model:
            raise ValueError("model must be non-empty")

    def runtime_configuration(self, request: LLMRequest) -> RuntimeConfiguration:
        """Expose the exact immutable runtime settings used to construct a request."""

        return RuntimeConfiguration(
            provider="openai",
            api=API_URL,
            requested_model=self.model,
            timeout_seconds=self.timeout_seconds,
            store=False,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            structured_output_name=STRUCTURED_OUTPUT_NAME,
            structured_output_strict=True,
            structured_output_schema=_structured_schema(request),
            client_revision=os.environ.get("Q_LLM_CLIENT_REVISION", "UNPINNED"),
        )

    def infer(self, request: LLMRequest) -> LLMResponse:
        payload = self._build_payload(request)
        http_request = urllib.request.Request(
            API_URL,
            data=canonical_json(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw_bytes = response.read()
                status = response.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1000]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"OpenAI runtime invocation failed: {type(exc).__name__}: {exc}") from exc

        try:
            body = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("OpenAI runtime returned non-JSON response") from exc

        if not isinstance(body, dict):
            raise RuntimeError("OpenAI runtime returned a non-object response")
        if status != 200:
            raise RuntimeError(f"OpenAI API returned unexpected HTTP status {status}")

        _assert_runtime_evidence(body, requested_model=self.model)
        action = _extract_action(body)
        metadata = {
            "provider": "openai",
            "api": API_URL,
            "requested_model": self.model,
            "returned_model": body["model"],
            "response_id": body["id"],
            "status": body["status"],
            "store": body["store"],
            "usage": body.get("usage"),
        }
        return LLMResponse(raw=body, action=action, metadata=metadata)

    def _build_payload(self, request: LLMRequest) -> dict[str, Any]:
        return {
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
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": STRUCTURED_OUTPUT_NAME,
                    "strict": True,
                    "schema": _structured_schema(request),
                }
            },
        }


def _structured_schema(request: LLMRequest) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [*request.tools, "TERMINATE"],
            }
        },
        "required": ["action"],
        "additionalProperties": False,
    }


def _assert_runtime_evidence(body: dict[str, Any], requested_model: str) -> None:
    response_id = body.get("id")
    returned_model = body.get("model")
    status = body.get("status")
    store = body.get("store")

    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("OpenAI response lacks a non-empty response id")
    if not isinstance(returned_model, str) or not returned_model:
        raise RuntimeError("OpenAI response lacks the actual returned model identity")
    if not isinstance(status, str):
        raise RuntimeError("OpenAI response lacks a generation status")
    if status != "completed":
        reason = body.get("incomplete_details") or body.get("error") or "no additional details"
        raise RuntimeError(f"OpenAI response is not completed: status={status!r}; detail={reason!r}")
    if store is not False:
        raise RuntimeError("OpenAI response does not prove store:false")
    if requested_model != returned_model:
        raise RuntimeError(
            f"OpenAI model identity mismatch: requested={requested_model!r}, returned={returned_model!r}"
        )


def _render_user_input(request: LLMRequest) -> str:
    """Serialize only declared model-visible state in a deterministic form."""

    document = {
        "objective": request.objective,
        "available_actions": list(request.tools),
        "current_observation": request.observation,
        "history": list(request.history),
        "instruction": "Return exactly one JSON object selecting the next available action or TERMINATE.",
    }
    return canonical_json(document)


def _extract_action(body: dict[str, Any]) -> str | None:
    """Extract the structured action; refusal or malformed output is never usable."""

    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            content_type = content.get("type")
            if content_type == "refusal":
                raise RuntimeError("OpenAI model refused the structured-output request")
            if content_type != "output_text":
                continue
            text = content.get("text", "")
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError("structured model response is not valid JSON") from exc
            action = parsed.get("action")
            if not isinstance(action, str):
                raise ValueError("structured model response does not contain a string action")
            return None if action == "TERMINATE" else action

    raise ValueError("OpenAI response contains no structured action output")
