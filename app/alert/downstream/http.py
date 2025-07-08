import requests
import logging
import json
from typing import Dict, Any

logger = logging.getLogger("downstream_http")

def send_http_msg(params: dict) -> dict:
    """
    发送HTTP告警
    params示例：{
        'url': 'http://example.com/alert',
        'method': 'POST',
        'headers': {'Authorization': 'Bearer xxx', 'Content-Type': 'application/json'},
        'body': '{"msg": "告警内容"}',
        'timeout': 10,
        'verify_ssl': true
    }
    """
    try:
        # 必填参数验证
        if 'url' not in params:
            return {"success": False, "msg": "缺少必要参数: url"}
        
        url = params['url']
        method = params.get('method', 'POST').upper()
        headers = params.get('headers', {})
        body = params.get('body', '')
        timeout = params.get('timeout', 10)
        verify_ssl = params.get('verify_ssl', True)
        
        # 如果body是dict，转为JSON字符串
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False)
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        
        logger.info(f"发送HTTP告警: {method} {url}")
        
        # 发送请求
        resp = requests.request(
            method=method,
            url=url,
            data=body.encode('utf-8') if isinstance(body, str) else body,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        
        logger.info(f"HTTP告警响应: {resp.status_code} - {resp.text[:200]}")
        
        return {
            "success": resp.ok,
            "status_code": resp.status_code,
            "response": resp.text,
            "msg": "HTTP告警发送成功" if resp.ok else f"HTTP请求失败: {resp.status_code}"
        }
        
    except Exception as e:
        logger.error(f"HTTP告警发送失败: {e}")
        return {"success": False, "msg": str(e)}

def render_http_template(template_data: dict, alert_context: dict) -> dict:
    """
    渲染HTTP告警模板
    template_data: 模板配置
    alert_context: 告警上下文数据
    返回: 渲染后的参数
    """
    try:
        # 默认HTTP告警模板
        default_body = {
            "alert_type": "prometheus",
            "rule_name": "{rule_name}",
            "level": "{level}",
            "condition": "{condition}",
            "current_value": "{current_value}",
            "trigger_time": "{trigger_time}",
            "message": "{message}"
        }
        
        # 复制模板数据
        rendered_params = template_data.copy()
        
        # 渲染body
        if 'body_template' in template_data:
            body_template = template_data['body_template']
        else:
            body_template = default_body
        
        # 如果body_template是字符串，直接格式化
        if isinstance(body_template, str):
            rendered_body = body_template.format(**alert_context)
        else:
            # 如果是dict，递归格式化每个值
            rendered_body = {}
            for key, value in body_template.items():
                if isinstance(value, str):
                    rendered_body[key] = value.format(**alert_context)
                else:
                    rendered_body[key] = value
        
        rendered_params['body'] = rendered_body
        
        # 渲染headers中的模板变量
        if 'headers' in rendered_params:
            for key, value in rendered_params['headers'].items():
                if isinstance(value, str) and '{' in value:
                    rendered_params['headers'][key] = value.format(**alert_context)
        
        return rendered_params
        
    except Exception as e:
        logger.error(f"HTTP模板渲染失败: {e}")
        return template_data 