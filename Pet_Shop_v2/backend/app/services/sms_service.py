import json
from dataclasses import dataclass
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import settings
from app.core.exceptions import BadRequestError


@dataclass(frozen=True)
class SmsSendResult:
    provider: str
    sent: bool
    message: str = "sent"


class SmsSender:
    def send_login_code(self, phone: str, code: str, expire_minutes: int) -> SmsSendResult:
        provider = settings.sms_provider.lower().strip()
        if provider == "mock":
            return SmsSendResult(provider="mock", sent=True, message="mock sent")
        if provider == "http":
            return self._send_via_http(phone, code, expire_minutes)
        if provider == "aliyun":
            return self._send_via_aliyun(phone, code, expire_minutes)
        raise BadRequestError(f"Unsupported SMS provider: {settings.sms_provider}")

    def _send_via_http(self, phone: str, code: str, expire_minutes: int) -> SmsSendResult:
        if not settings.sms_http_url:
            raise BadRequestError("SMS_HTTP_URL is required when SMS_PROVIDER=http")

        payload = json.dumps(
            {
                "phone": phone,
                "code": code,
                "expire_minutes": expire_minutes,
                "purpose": "login",
            },
            ensure_ascii=False,
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if settings.sms_http_token:
            headers["Authorization"] = f"Bearer {settings.sms_http_token}"

        req = request.Request(
            settings.sms_http_url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                if resp.status < 200 or resp.status >= 300:
                    raise BadRequestError(f"SMS HTTP provider failed: {body}")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise BadRequestError(f"SMS HTTP provider failed: {body}") from exc
        except URLError as exc:
            raise BadRequestError(f"SMS HTTP provider unavailable: {exc.reason}") from exc

        return SmsSendResult(provider="http", sent=True)

    def _send_via_aliyun(self, phone: str, code: str, expire_minutes: int) -> SmsSendResult:
        required = {
            "ALIYUN_SMS_ACCESS_KEY_ID": settings.aliyun_sms_access_key_id,
            "ALIYUN_SMS_ACCESS_KEY_SECRET": settings.aliyun_sms_access_key_secret,
            "ALIYUN_SMS_SIGN_NAME": settings.aliyun_sms_sign_name,
            "ALIYUN_SMS_TEMPLATE_CODE": settings.aliyun_sms_template_code,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise BadRequestError(f"Missing Aliyun SMS config: {', '.join(missing)}")

        try:
            from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
            from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
            from alibabacloud_tea_openapi import models as open_api_models
        except ImportError as exc:
            raise BadRequestError(
                "Aliyun SMS SDK is not installed. Run: pip install -r requirements.txt"
            ) from exc

        endpoint = settings.aliyun_sms_endpoint.replace("https://", "").replace("http://", "").strip("/")
        config = open_api_models.Config(
            access_key_id=settings.aliyun_sms_access_key_id,
            access_key_secret=settings.aliyun_sms_access_key_secret,
            endpoint=endpoint,
        )
        client = DypnsapiClient(config)
        sms_request = dypnsapi_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=settings.aliyun_sms_sign_name,
            template_code=settings.aliyun_sms_template_code,
            template_param=json.dumps(
                {"code": code, "min": str(expire_minutes)},
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        )

        try:
            response = client.send_sms_verify_code(sms_request)
        except Exception as exc:
            raise BadRequestError(f"Aliyun SMS request failed: {exc}") from exc

        response_body = getattr(response, "body", None)
        response_code = getattr(response_body, "code", "")
        if response_code != "OK":
            message = getattr(response_body, "message", "") or response_code or "unknown error"
            raise BadRequestError(f"Aliyun SMS failed: {message}")

        return SmsSendResult(provider="aliyun", sent=True, message="OK")
