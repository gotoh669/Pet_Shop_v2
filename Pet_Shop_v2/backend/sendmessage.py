import os
import json
import random


class SMSConfig:
    # 优先从环境变量读取，防止密钥泄露
    ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID") or os.getenv("ALIYUN_SMS_ACCESS_KEY_ID", "")
    ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET") or os.getenv("ALIYUN_SMS_ACCESS_KEY_SECRET", "")

    # 必须与控制台体验测试页面的参数一字不差
    SIGN_NAME = "速通互联验证码"
    TEMPLATE_CODE = "100001"


def send_sms_verify_code_direct(phone: str) -> dict:
    """
    调用阿里云号码认证服务发送验证码
    """
    # 1. 本地生成 6 位随机验证码
    verify_code = str(random.randint(100000, 999999))
    if not SMSConfig.ACCESS_KEY_ID or not SMSConfig.ACCESS_KEY_SECRET:
        return {
            "success": False,
            "message": "缺少阿里云 AccessKey 配置"
        }
    try:
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
        from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
    except ImportError as e:
        return {
            "success": False,
            "message": f"缺少阿里云短信 SDK: {str(e)}"
        }

    # 2. 配置专属网关 (必须是 dypnsapi)
    config = open_api_models.Config(
        access_key_id=SMSConfig.ACCESS_KEY_ID,
        access_key_secret=SMSConfig.ACCESS_KEY_SECRET,
        endpoint="dypnsapi.aliyuncs.com"
    )
    client = DypnsapiClient(config)

    # 3. 组装 100001 模板需要的变量（code: 验证码, min: 有效期分钟数）
    template_param = {
        "code": verify_code,
        "min": "5"
    }

    request = dypnsapi_models.SendSmsVerifyCodeRequest(
        phone_number=phone,
        sign_name=SMSConfig.SIGN_NAME,
        template_code=SMSConfig.TEMPLATE_CODE,
        template_param=json.dumps(template_param)  # 必须序列化为 JSON 字符串
    )

    try:
        # 4. 发起网络请求
        response = client.send_sms_verify_code(request)

        # 阿里云返回 OK 代表网关接收成功
        if response.body.code == "OK":
            return {
                "success": True,
                "message": "发送成功",
                "code": verify_code  # 务必将验证码返回，以便 FastAPI 存入 Redis
            }
        else:
            return {
                "success": False,
                "message": f"云端拒绝: {response.body.message}"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"SDK调用异常: {str(e)}"
        }
