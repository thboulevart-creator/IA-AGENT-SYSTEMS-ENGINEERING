from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


API_URL = "https://api.openai.com/v1/responses"
MODEL = os.environ.get("Q_LLM_MODEL", "gpt-5.6-luna")


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("BLOCKED: OPENAI_API_KEY is not available to the runtime.")
        return 2

    payload = {
        "model": MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Return exactly the word READY.",
                    }
                ],
            }
        ],
        "max_output_tokens": 16,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
            status = response.status
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"FAIL: OpenAI API returned HTTP {exc.code}: {detail[:1000]}")
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"FAIL: runtime invocation error: {type(exc).__name__}: {exc}")
        return 1

    response_model = body.get("model")
    response_id = body.get("id")
    if status != 200 or not response_model or not response_id:
        print("FAIL: API response lacks required runtime evidence.")
        print(json.dumps({"status": status, "model": response_model, "id": response_id}))
        return 1

    # Do not print the raw model response: the smoke test proves connectivity,
    # authentication, and model identity without creating unnecessary output data.
    print(
        json.dumps(
            {
                "status": status,
                "api": API_URL,
                "requested_model": MODEL,
                "returned_model": response_model,
                "response_id": response_id,
                "authenticated_real_inference": True,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
