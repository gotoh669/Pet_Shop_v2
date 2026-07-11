import json
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import settings
from app.core.exceptions import BadRequestError


class DeepSeekClient:
    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        extra_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not settings.deepseek_api_key:
            raise BadRequestError("DEEPSEEK_API_KEY is required")

        payload: dict[str, Any] = {
            "model": model or settings.deepseek_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if extra_body:
            payload.update(extra_body)

        endpoint = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.deepseek_api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise BadRequestError(f"DeepSeek request failed: {error_body}") from exc
        except URLError as exc:
            raise BadRequestError(f"DeepSeek service unavailable: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise BadRequestError("DeepSeek response is not valid JSON") from exc

    def simple_chat(
        self,
        message: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict[str, Any]:
        response = self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choices = response.get("choices") or []
        content = ""
        if choices:
            content = ((choices[0].get("message") or {}).get("content") or "").strip()
        return {
            "model": response.get("model") or model or settings.deepseek_model,
            "content": content,
            "usage": response.get("usage"),
        }
