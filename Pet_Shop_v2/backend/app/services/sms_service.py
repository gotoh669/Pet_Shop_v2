import base64
import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib import parse, request
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
            return self._send_via_aliyun(phone, code)
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

    def _send_via_aliyun(self, phone: str, code: str) -> SmsSendResult:
        required = {
            "ALIYUN_SMS_ACCESS_KEY_ID": settings.aliyun_sms_access_key_id,
            "ALIYUN_SMS_ACCESS_KEY_SECRET": settings.aliyun_sms_access_key_secret,
            "ALIYUN_SMS_SIGN_NAME": settings.aliyun_sms_sign_name,
            "ALIYUN_SMS_TEMPLATE_CODE": settings.aliyun_sms_template_code,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise BadRequestError(f"Missing Aliyun SMS config: {', '.join(missing)}")

        params: dict[str, Any] = {
            "AccessKeyId": settings.aliyun_sms_access_key_id,
            "Action": "SendSms",
            "Format": "JSON",
            "PhoneNumbers": phone,
            "RegionId": settings.aliyun_sms_region_id,
            "SignName": settings.aliyun_sms_sign_name,
            "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": str(uuid.uuid4()),
            "SignatureVersion": "1.0",
            "TemplateCode": settings.aliyun_sms_template_code,
            "TemplateParam": json.dumps({"code": code}, separators=(",", ":")),
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Version": "2017-05-25",
        }
        signature = self._aliyun_signature(params, settings.aliyun_sms_access_key_secret)
        params["Signature"] = signature
        url = f"{settings.aliyun_sms_endpoint}?{parse.urlencode(params)}"

        try:
            with request.urlopen(url, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise BadRequestError(f"Aliyun SMS request failed: {body}") from exc
        except URLError as exc:
            raise BadRequestError(f"Aliyun SMS service unavailable: {exc.reason}") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BadRequestError(f"Aliyun SMS returned invalid JSON: {body}") from exc

        if data.get("Code") != "OK":
            message = data.get("Message") or body
            raise BadRequestError(f"Aliyun SMS failed: {message}")

        return SmsSendResult(provider="aliyun", sent=True, message=data.get("Message", "OK"))

    @staticmethod
    def _percent_encode(value: Any) -> str:
        return parse.quote(str(value), safe="-_.~")

    def _aliyun_signature(self, params: dict[str, Any], access_key_secret: str) -> str:
        canonicalized_query = "&".join(
            f"{self._percent_encode(key)}={self._percent_encode(params[key])}"
            for key in sorted(params)
        )
        string_to_sign = f"GET&%2F&{self._percent_encode(canonicalized_query)}"
        digest = hmac.new(
            f"{access_key_secret}&".encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")
