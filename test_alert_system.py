#!/usr/bin/env python3
"""
BigDataOps 告警系统测试脚本
包含完整的功能测试用例
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_api(method: str, url: str, data: Dict = None) -> Dict[str, Any]:
    """通用API测试函数"""
    try:
        if method.upper() == 'GET':
            response = requests.get(f"{BASE_URL}{url}")
        elif method.upper() == 'POST':
            response = requests.post(f"{BASE_URL}{url}", json=data)
        elif method.upper() == 'PUT':
            response = requests.put(f"{BASE_URL}{url}", json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(f"{BASE_URL}{url}")
        else:
            return {"error": f"不支持的HTTP方法: {method}"}
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }
    except Exception as e:
        return {"error": str(e)}

def test_health():
    """测试健康检查"""
    print("=== 1. 健康检查测试 ===")
    result = test_api("GET", "/health")
    print(f"健康检查结果: {result}")
    return result.get("status_code") == 200

def test_email_template():
    """测试创建邮件模板"""
    print("\n=== 2. 邮件模板测试 ===")
    
    # 创建邮件模板
    email_template = {
        "name": "测试邮件告警模板",
        "type": "email",
        "params": {
            "smtp_host": "smtp.163.com",
            "smtp_port": 465,
            "from": "test@163.com",
            "to": ["admin@company.com"],
            "require_auth": True,
            "user": "test@163.com",
            "password": "test_password",
            "ssl": True,
            "subject_template": "【{level}】{rule_name} 告警通知",
            "content_template": "<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p><p>条件: {condition}</p><p>时间: {trigger_time}</p>"
        }
    }
    
    result = test_api("POST", "/alert/notify_template", email_template)
    print(f"创建邮件模板结果: {result}")
    
    if result.get("status_code") == 200 and result.get("data", {}).get("code") == 0:
        template_id = result["data"]["data"]["id"]
        print(f"邮件模板创建成功，ID: {template_id}")
        return template_id
    return None

def test_http_template():
    """测试创建HTTP模板"""
    print("\n=== 3. HTTP模板测试 ===")
    
    # 创建HTTP模板
    http_template = {
        "name": "测试HTTP告警模板",
        "type": "http",
        "params": {
            "url": "http://httpbin.org/post",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            },
            "body_template": {
                "alert_type": "prometheus",
                "rule_name": "{rule_name}",
                "level": "{level}",
                "condition": "{condition}",
                "current_value": "{current_value}",
                "trigger_time": "{trigger_time}",
                "message": "{message}"
            },
            "timeout": 10,
            "verify_ssl": True
        }
    }
    
    result = test_api("POST", "/alert/notify_template", http_template)
    print(f"创建HTTP模板结果: {result}")
    
    if result.get("status_code") == 200 and result.get("data", {}).get("code") == 0:
        template_id = result["data"]["data"]["id"]
        print(f"HTTP模板创建成功，ID: {template_id}")
        return template_id
    return None

def test_alert_rule(template_id: int):
    """测试创建告警规则"""
    print(f"\n=== 4. 告警规则测试 (模板ID: {template_id}) ===")
    
    # 创建告警规则
    alert_rule = {
        "name": "CPU使用率告警",
        "promql": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
        "condition": "> 80",
        "level": "critical",
        "suppress": None,
        "repeat": 300,  # 5分钟内不重复发送
        "enabled": True,
        "notify_template_id": template_id
    }
    
    result = test_api("POST", "/alert/rule", alert_rule)
    print(f"创建告警规则结果: {result}")
    
    if result.get("status_code") == 200 and result.get("data", {}).get("code") == 0:
        rule_id = result["data"]["data"]["id"]
        print(f"告警规则创建成功，ID: {rule_id}")
        return rule_id
    return None

def test_engine_operations():
    """测试告警引擎操作"""
    print("\n=== 5. 告警引擎测试 ===")
    
    # 获取引擎状态
    print("获取引擎状态...")
    result = test_api("GET", "/alert/engine/status")
    print(f"引擎状态: {result}")
    
    # 手动触发一次告警检测
    print("\n手动触发告警检测...")
    result = test_api("POST", "/alert/engine/test")
    print(f"手动触发结果: {result}")
    
    # 再次获取状态
    time.sleep(2)
    print("\n再次获取引擎状态...")
    result = test_api("GET", "/alert/engine/status")
    print(f"引擎状态: {result}")

def test_query_apis():
    """测试查询接口"""
    print("\n=== 6. 查询接口测试 ===")
    
    # 查询所有模板
    print("查询所有通知模板...")
    result = test_api("GET", "/alert/notify_template")
    print(f"通知模板列表: {result}")
    
    # 查询所有规则
    print("\n查询所有告警规则...")
    result = test_api("GET", "/alert/rule")
    print(f"告警规则列表: {result}")
    
    # 查询告警历史
    print("\n查询告警历史...")
    result = test_api("GET", "/alert/history")
    print(f"告警历史列表: {result}")

def main():
    """主测试流程"""
    print("BigDataOps 告警系统完整测试")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health():
        print("❌ 服务不可用，请先启动服务")
        return
    
    # 2. 创建邮件模板
    email_template_id = test_email_template()
    
    # 3. 创建HTTP模板
    http_template_id = test_http_template()
    
    # 4. 创建告警规则（使用邮件模板）
    rule_id = None
    if email_template_id:
        rule_id = test_alert_rule(email_template_id)
    
    # 5. 测试告警引擎
    test_engine_operations()
    
    # 6. 测试查询接口
    test_query_apis()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print(f"邮件模板ID: {email_template_id}")
    print(f"HTTP模板ID: {http_template_id}")
    print(f"告警规则ID: {rule_id}")
    
    if rule_id:
        print("\n📝 后续测试建议:")
        print("1. 配置真实的Prometheus地址")
        print("2. 配置真实的邮箱SMTP信息")
        print("3. 创建会真正触发的PromQL表达式")
        print("4. 观察告警历史记录的生成")

if __name__ == "__main__":
    main() 