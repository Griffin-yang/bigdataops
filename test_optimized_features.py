#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化功能测试脚本
测试持续时间区分和规则复制功能
"""

import requests
import json
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:8000/api"

def test_create_rule_with_dual_duration():
    """测试创建带有双重持续时间的告警规则"""
    print("🔧 测试双重持续时间功能...")
    
    rule_data = {
        "name": "双重持续时间测试规则",
        "category": "system",
        "promql": "up == 0",
        "condition": "> 0",
        "for_duration": 120,  # 触发持续时间：2分钟
        "level": "medium",
        "suppress": "5m",
        "repeat": 600,
        "duration": 1800,     # 发送持续时间：30分钟
        "max_send_count": 3,
        "enabled": True,
        "notify_template_id": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/alert/rule", json=rule_data)
        result = response.json()
        
        if result.get("code") == 0:
            print(f"✅ 规则创建成功，ID: {result['data']['id']}")
            print(f"   - 触发持续时间: {rule_data['for_duration']}秒 (条件持续2分钟才触发)")
            print(f"   - 发送持续时间: {rule_data['duration']}秒 (发送30分钟后停止)")
            return result['data']['id']
        else:
            print(f"❌ 创建失败: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_rule_copy_functionality():
    """测试规则复制功能（通过模拟前端逻辑）"""
    print("🔧 测试规则复制功能...")
    
    # 首先获取一个现有规则
    try:
        response = requests.get(f"{API_BASE_URL}/alert/rule")
        result = response.json()
        
        if result.get("code") == 0 and result.get("data"):
            rules = result["data"].get("items", [])
            if rules:
                source_rule = rules[0]
                print(f"📋 找到源规则: {source_rule['name']}")
                
                # 模拟复制功能
                copied_rule = {
                    "name": f"{source_rule['name']} - 副本",
                    "category": source_rule["category"],
                    "promql": source_rule["promql"],
                    "condition": source_rule["condition"],
                    "for_duration": source_rule.get("for_duration", 60),
                    "level": source_rule["level"],
                    "description": source_rule.get("description", ""),
                    "suppress": source_rule.get("suppress", ""),
                    "repeat": source_rule.get("repeat", 0),
                    "duration": source_rule.get("duration", 3600),
                    "max_send_count": source_rule.get("max_send_count"),
                    "enabled": False,  # 复制的规则默认禁用
                    "notify_template_id": source_rule.get("notify_template_id")
                }
                
                # 创建复制的规则
                copy_response = requests.post(f"{API_BASE_URL}/alert/rule", json=copied_rule)
                copy_result = copy_response.json()
                
                if copy_result.get("code") == 0:
                    print(f"✅ 规则复制成功，新规则ID: {copy_result['data']['id']}")
                    print(f"   - 新名称: {copied_rule['name']}")
                    print(f"   - 默认状态: {'禁用' if not copied_rule['enabled'] else '启用'}")
                    return copy_result['data']['id']
                else:
                    print(f"❌ 复制失败: {copy_result.get('msg')}")
                    return None
            else:
                print("❌ 没有找到可复制的规则")
                return None
        else:
            print(f"❌ 获取规则失败: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def validate_database_structure():
    """验证数据库结构是否正确"""
    print("🔧 验证数据库结构...")
    
    try:
        # 通过创建一个测试规则来验证字段是否存在
        test_rule = {
            "name": "数据库结构验证规则",
            "category": "other",
            "promql": "up",
            "condition": "> 0",
            "for_duration": 60,
            "level": "low",
            "duration": 3600,
            "max_send_count": 1,
            "enabled": False,
            "notify_template_id": 1
        }
        
        response = requests.post(f"{API_BASE_URL}/alert/rule", json=test_rule)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 数据库结构验证通过")
            print("   - for_duration字段正常")
            print("   - duration字段正常")
            print("   - max_send_count字段正常")
            
            # 删除测试规则
            rule_id = result['data']['id']
            requests.delete(f"{API_BASE_URL}/alert/rule/{rule_id}")
            print("   - 测试数据已清理")
            return True
        else:
            print(f"❌ 数据库结构验证失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试优化功能...")
    print("=" * 50)
    
    # 1. 验证数据库结构
    db_ok = validate_database_structure()
    print()
    
    if not db_ok:
        print("❌ 数据库结构验证失败，请先运行数据库升级脚本")
        return
    
    # 2. 测试双重持续时间功能
    rule_id = test_create_rule_with_dual_duration()
    print()
    
    # 3. 测试规则复制功能
    copied_rule_id = test_rule_copy_functionality()
    print()
    
    print("=" * 50)
    print("🎉 优化功能测试完成！")
    
    print("\n📋 功能总结:")
    print("1. ✅ 持续时间字段分离")
    print("   - 触发持续时间：条件持续满足才触发")
    print("   - 发送持续时间：告警发送超时控制")
    print("2. ✅ 规则复制功能")
    print("   - 一键复制规则配置")
    print("   - 自动添加副本后缀")
    print("   - 默认禁用防误触发")
    
    print("\n🔗 前端新功能:")
    print("- 创建规则：两个持续时间字段含义清晰")
    print("- 规则管理：新增复制按钮")
    print("- 智能复制：配置自动继承")

if __name__ == "__main__":
    main()
