import requests
import logging
import json
from typing import Dict, Any

logger = logging.getLogger("downstream_lechat")

def send_lechat_msg(params: dict) -> dict:
    """
    发送乐聊告警
    params示例：{
        'url': 'http://<host>/api/message/sendTeam',
        'fromId': 'lyj-dw',
        'groupId': 'group-123456',
        'ext': '{"group":"oa"}',
        'body': '{"robot":{"type":"robotAnswer"},"type":"multi","msgs":[{"text":"告警内容","type":"text"}]}',
        'pushcontent': '任务提醒',  # 可选
        'payload': '{}',  # 可选，iOS专用
        'option': '{"push":true}'  # 可选
    }
    """
    try:
        # 获取发送模式
        mode = params.get('mode', 'group')
        
        # 基础必填参数验证
        required_fields = ["url", "fromId", "ext", "body"]
        for field in required_fields:
            if field not in params:
                return {"success": False, "msg": f"缺少必要参数: {field}"}
        
        # 根据模式验证特定参数
        if mode == 'group':
            if 'groupId' not in params:
                return {"success": False, "msg": "群组模式缺少必要参数: groupId"}
        elif mode == 'personal':
            if 'userIds' not in params:
                return {"success": False, "msg": "个人模式缺少必要参数: userIds"}
        
        if mode == 'group':
            # 群组模式：单次发送到群组
            return _send_group_message(params)
        else:
            # 个人模式：批量发送给个人
            return _send_personal_messages(params)
        
    except Exception as e:
        logger.error(f"乐聊告警发送失败: {e}")
        return {"success": False, "msg": str(e)}

def render_lechat_template(template_data: dict, alert_context: dict) -> dict:
    """
    渲染乐聊告警模板
    template_data: 模板配置
    alert_context: 告警上下文数据
    返回: 渲染后的参数
    """
    try:
        # 默认乐聊告警消息体
        default_body = {
            "robot": {"type": "robotAnswer"},
            "type": "multi",
            "msgs": [
                {
                    "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n时间: {trigger_time}",
                    "type": "text"
                }
            ]
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
            rendered_body = format_dict_values(body_template, alert_context)
        
        # 确保body是JSON字符串
        if isinstance(rendered_body, dict):
            rendered_params['body'] = json.dumps(rendered_body, ensure_ascii=False)
        else:
            rendered_params['body'] = rendered_body
        
        # 渲染ext字段
        if 'ext_template' in template_data:
            ext_template = template_data['ext_template']
            if isinstance(ext_template, str):
                rendered_params['ext'] = ext_template.format(**alert_context)
            else:
                rendered_ext = format_dict_values(ext_template, alert_context)
                rendered_params['ext'] = json.dumps(rendered_ext, ensure_ascii=False)
        
        # 渲染其他字段
        for field in ['fromId', 'groupId', 'pushcontent']:
            if field in rendered_params and isinstance(rendered_params[field], str):
                if '{' in rendered_params[field]:
                    rendered_params[field] = rendered_params[field].format(**alert_context)
        
        return rendered_params
        
    except Exception as e:
        logger.error(f"乐聊模板渲染失败: {e}")
        return template_data

def _send_group_message(params: dict) -> dict:
    """发送群组消息"""
    try:
        # 构建群组消息请求数据
        data = {
            'type': '100',  # 固定为100，表示文本消息
            'fromId': params['fromId'],
            'groupId': params['groupId'],
            'ext': params['ext'],
            'body': params['body']
        }
        
        # 添加可选参数
        for optional_field in ['pushcontent', 'payload', 'option']:
            if optional_field in params:
                data[optional_field] = params[optional_field]
        
        logger.info(f"发送乐聊群组告警: POST {params['url']}")
        logger.debug(f"请求数据: {data}")
        
        # 发送请求
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post(
            url=params['url'],
            data=data,
            headers=headers,
            timeout=params.get('timeout', 10)
        )
        
        logger.info(f"乐聊群组告警响应: {resp.status_code} - {resp.text[:200]}")
        
        return {
            "success": resp.ok,
            "status_code": resp.status_code,
            "response": resp.text,
            "msg": "乐聊群组告警发送成功" if resp.ok else f"乐聊群组请求失败: {resp.status_code}"
        }
        
    except Exception as e:
        logger.error(f"乐聊群组告警发送失败: {e}")
        return {"success": False, "msg": str(e)}

def _send_personal_messages(params: dict) -> dict:
    """发送个人消息（批量）"""
    try:
        user_ids = params['userIds'].split(',')
        user_mapping = params.get('userMapping', {})
        results = []
        success_count = 0
        
        logger.info(f"开始批量发送个人告警，目标用户: {len(user_ids)} 个")
        
        for user_id in user_ids:
            user_id = user_id.strip()
            if not user_id or user_id == "000001":  # 跳过空值和特殊工号
                continue
                
            # 应用用户映射
            mapped_user_id = user_mapping.get(user_id, user_id)
            
            # 构建个人消息请求数据
            data = {
                'type': '100',  # 固定为100，表示文本消息
                'fromId': params['fromId'],
                'toUser': mapped_user_id,  # 个人模式使用toUser而不是groupId
                'ext': params['ext'],
                'body': params['body']
            }
            
            # 添加可选参数
            for optional_field in ['pushcontent', 'payload', 'option']:
                if optional_field in params:
                    data[optional_field] = params[optional_field]
            
            try:
                # 发送个人消息
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                resp = requests.post(
                    url=params['url'],
                    data=data,
                    headers=headers,
                    timeout=params.get('timeout', 10)
                )
                
                result = {
                    "user_id": user_id,
                    "mapped_user_id": mapped_user_id,
                    "success": resp.ok,
                    "status_code": resp.status_code,
                    "response": resp.text[:100]  # 限制响应长度
                }
                
                if resp.ok:
                    success_count += 1
                    logger.info(f"乐聊个人告警发送成功: {user_id} -> {mapped_user_id}")
                else:
                    logger.warning(f"乐聊个人告警发送失败: {user_id} -> {mapped_user_id}, {resp.status_code}")
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"发送给用户 {user_id} -> {mapped_user_id} 失败: {e}")
                results.append({
                    "user_id": user_id,
                    "mapped_user_id": mapped_user_id,
                    "success": False,
                    "error": str(e)
                })
        
        total_count = len(results)
        overall_success = success_count > 0
        
        logger.info(f"乐聊个人告警批量发送完成: 成功 {success_count}/{total_count}")
        
        return {
            "success": overall_success,
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": total_count - success_count,
            "results": results,
            "msg": f"乐聊个人告警发送完成: 成功 {success_count}/{total_count}"
        }
        
    except Exception as e:
        logger.error(f"乐聊个人告警批量发送失败: {e}")
        return {"success": False, "msg": str(e)}

def format_dict_values(data: dict, context: dict) -> dict:
    """递归格式化字典中的字符串值"""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = value.format(**context)
        elif isinstance(value, dict):
            result[key] = format_dict_values(value, context)
        elif isinstance(value, list):
            result[key] = [
                item.format(**context) if isinstance(item, str) else
                format_dict_values(item, context) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result