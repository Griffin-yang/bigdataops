#!/usr/bin/env python3
"""
乐聊告警功能测试脚本
"""

import requests
import json

# 配置
API_BASE_URL = "http://localhost:8000"

def test_create_lechat_template():
    """测试创建乐聊告警模板"""
    print("🧪 测试创建乐聊告警模板...")
    
    # 测试群组模板
    group_template_data = {
        "name": "乐聊群组告警模板",
        "type": "lechat", 
        "params": {
            "mode": "group",
            "url": "http://your-host/api/message/sendTeam",
            "fromId": "lyj-dw",
            "groupId": "group-123456",
            "ext": {"group": "oa"},
            "body_template": {
                "robot": {"type": "robotAnswer"},
                "type": "multi", 
                "msgs": [{
                    "text": "🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}",
                    "type": "text"
                }]
            },
            "pushcontent": "告警提醒"
        }
    }
    
    # 测试个人模板  
    personal_template_data = {
        "name": "乐聊个人告警模板",
        "type": "lechat",
        "params": {
            "mode": "personal",
            "url": "http://your-host/api/message/sendPersonal",
            "fromId": "lyj-dw",
            "userIds": "233655,056518,283669",
            "ext": {"group": "oa"},
            "body_template": {
                "robot": {"type": "robotAnswer"},
                "type": "multi",
                "msgs": [{
                    "text": "🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}",
                    "type": "text"
                }]
            },
            "userMapping": {
                "233655": "br",
                "056518": "056518", 
                "283669": "dq"
            },
            "pushcontent": "告警提醒"
        }
    }
    
    # 先测试群组模板
    print("📱 测试群组模板创建...")
    template_data = group_template_data
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/alert/notify_template",
            json=template_data,
            timeout=10
        )
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 如果群组模板创建成功，继续测试个人模板
        if response.status_code == 200:
            print("\n📱 测试个人模板创建...")
            personal_response = requests.post(
                f"{API_BASE_URL}/api/alert/notify_template",
                json=personal_template_data,
                timeout=10
            )
            print(f"个人模板响应状态码: {personal_response.status_code}")
            print(f"个人模板响应内容: {personal_response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始乐聊告警功能测试")
    test_create_lechat_template()
    print("🎯 测试完成！")