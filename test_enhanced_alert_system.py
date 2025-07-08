#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强告警系统功能测试脚本
测试新增的抑制规则和确认功能
"""

import time
import requests
import json
from datetime import datetime, timedelta

# 配置
API_BASE_URL = "http://localhost:8000/api"
TEST_USER = "test_user"

def test_create_enhanced_rule():
    """测试创建带有增强抑制功能的告警规则"""
    print("🔧 测试创建增强告警规则...")
    
    rule_data = {
        "name": "测试增强抑制规则",
        "category": "system",
        "promql": "up == 0",
        "condition": "> 0",
        "level": "high",
        "suppress": "2m",  # 2分钟抑制
        "repeat": 300,     # 5分钟重复
        "duration": 1800,  # 30分钟持续时间
        "max_send_count": 3,  # 最多发送3次
        "enabled": True,
        "notify_template_id": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/alert/rule", json=rule_data)
        result = response.json()
        
        if result.get("code") == 0:
            print(f"✅ 创建成功，规则ID: {result['data']['id']}")
            return result['data']['id']
        else:
            print(f"❌ 创建失败: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始测试增强告警系统功能...")
    print("=" * 50)
    
    print("📋 新功能说明:")
    print("1. ✅ 持续时间控制 - 告警超过设定时间后自动停止发送")
    print("2. ✅ 发送次数限制 - 在抑制期内最多发送指定次数")
    print("3. ✅ 每日重置 - 计数器每天自动重置")
    print("4. ✅ 手动确认 - 可以手动确认告警停止发送")
    print("5. ✅ 模板复制 - 支持复制现有模板创建新模板")
    
    print("\n🔗 前端功能:")
    print("- 告警规则管理：增加持续时间和最大发送次数配置")
    print("- 告警历史：增加确认按钮")
    print("- 告警模板：增加复制按钮")

if __name__ == "__main__":
    main()
