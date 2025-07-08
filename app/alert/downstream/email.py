# 迁移自downstream_email.py
# ... existing code ... 

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import json
from typing import Dict, List, Optional
import os

logger = logging.getLogger("downstream_email")

def send_email_msg(params: dict) -> dict:
    """
    发送邮件告警
    params示例：{
        "smtp_host": "smtp.163.com",
        "smtp_port": 465,
        "from": "sender@163.com",
        "to": ["receiver1@qq.com", "receiver2@qq.com"],
        "cc": ["cc@qq.com"],
        "require_auth": true,
        "user": "sender@163.com",
        "password": "smtp_password",
        "starttls": false,
        "ssl": true,
        "subject": "告警通知",
        "content": "告警内容HTML",
        "attachments": ["/path/to/file.png"]  # 可选附件
    }
    """
    try:
        # 必填参数验证
        required_fields = ["smtp_host", "smtp_port", "from", "to", "subject", "content"]
        for field in required_fields:
            if field not in params:
                return {"success": False, "msg": f"缺少必要参数: {field}"}
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['Subject'] = params['subject']
        msg['From'] = params['from']
        msg['To'] = ','.join(params['to']) if isinstance(params['to'], list) else params['to']
        
        if params.get('cc'):
            cc_list = params['cc'] if isinstance(params['cc'], list) else [params['cc']]
            msg['Cc'] = ','.join(cc_list)
        else:
            cc_list = []
        
        # 添加邮件正文
        content_type = 'html' if '<' in params['content'] and '>' in params['content'] else 'plain'
        msg.attach(MIMEText(params['content'], content_type, 'utf-8'))
        
        # 添加附件
        if params.get('attachments'):
            for attachment_path in params['attachments']:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment_path)}'
                        )
                        msg.attach(part)
                else:
                    logger.warning(f"附件不存在: {attachment_path}")
        
        # 连接SMTP服务器
        smtp_port = int(params['smtp_port'])
        if params.get('ssl', False):
            server = smtplib.SMTP_SSL(params['smtp_host'], smtp_port)
        else:
            server = smtplib.SMTP(params['smtp_host'], smtp_port)
            if params.get('starttls', False):
                server.starttls()
        
        # 认证
        if params.get('require_auth', False):
            server.login(params['user'], params['password'])
        
        # 发送邮件
        to_list = params['to'] if isinstance(params['to'], list) else [params['to']]
        all_recipients = to_list + cc_list
        
        server.sendmail(params['from'], all_recipients, msg.as_string())
        server.quit()
        
        logger.info(f"邮件发送成功: {params['subject']} -> {all_recipients}")
        return {"success": True, "msg": "邮件发送成功"}
        
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return {"success": False, "msg": str(e)}

def render_email_template(template_data: dict, alert_context: dict) -> tuple:
    """
    渲染邮件模板
    template_data: 模板配置
    alert_context: 告警上下文数据
    返回: (subject, content)
    """
    try:
        # 默认模板
        default_subject = "【{level}】{rule_name} 告警通知"
        default_content = """
        <h2>告警详情</h2>
        <table border="1" style="border-collapse: collapse;">
            <tr><td><b>规则名称</b></td><td>{rule_name}</td></tr>
            <tr><td><b>告警等级</b></td><td>{level}</td></tr>
            <tr><td><b>触发条件</b></td><td>{condition}</td></tr>
            <tr><td><b>当前值</b></td><td>{current_value}</td></tr>
            <tr><td><b>触发时间</b></td><td>{trigger_time}</td></tr>
            <tr><td><b>告警消息</b></td><td>{message}</td></tr>
        </table>
        """
        
        # 使用自定义模板或默认模板
        subject_template = template_data.get('subject_template', default_subject)
        content_template = template_data.get('content_template', default_content)
        
        # 格式化模板
        subject = subject_template.format(**alert_context)
        content = content_template.format(**alert_context)
        
        return subject, content
        
    except Exception as e:
        logger.error(f"邮件模板渲染失败: {e}")
        # 返回最基础的模板
        return f"告警通知 - {alert_context.get('rule_name', 'Unknown')}", str(alert_context) 