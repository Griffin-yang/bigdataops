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

def get_param_label(param: str) -> str:
    """获取参数的中文标签"""
    label_map = {
        'rule_name': '规则名称',
        'level': '告警等级',
        'category': '组件分组',
        'condition': '触发条件',
        'current_value': '当前值',
        'trigger_time': '触发时间',
        'promql': 'PromQL查询',
        'description': '规则描述',
        'name': '主机名称',
        'port': '端口号',
        'instance': '实例地址',
        'job': '服务名称',
        'service': '服务类型',
        'group': '分组',
        'role': '角色'
    }
    return label_map.get(param, param)

def get_level_display(level: str) -> str:
    """将告警等级转换为中文显示"""
    level_map = {
        'critical': '严重',
        'high': '高',
        'medium': '中',
        'low': '低',
        'info': '信息',
        'warning': '警告',
        'error': '错误'
    }
    return level_map.get(level.lower(), level)

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
    渲染邮件模板 - 统一美观的HTML模板
    template_data: 模板配置，包含email_params字段指定要显示的参数
    alert_context: 告警上下文数据
    返回: (subject, content)
    """
    try:
        logger.info(f"开始渲染邮件模板")
        logger.info(f"模板数据: {template_data}")
        logger.info(f"告警上下文: {alert_context}")
        
        # 获取要显示的参数列表
        email_params = template_data.get('email_params', [])
        if not email_params:
            # 默认显示基础参数
            email_params = ['rule_name', 'level', 'current_value', 'name', 'port']
        
        # 默认主题模板
        default_subject = "【{level_display}】{rule_name} 告警通知"
        
        # 统一美观的HTML模板
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>告警通知</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    border-radius: 16px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.3;
                }}
                .header h1 {{ 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 700;
                    position: relative;
                    z-index: 1;
                }}
                .header .subtitle {{
                    margin-top: 8px;
                    opacity: 0.9;
                    font-size: 16px;
                    position: relative;
                    z-index: 1;
                }}
                .content {{ 
                    padding: 30px; 
                }}
                .alert-summary {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 25px;
                    border-left: 4px solid #ff6b6b;
                }}
                .alert-summary h2 {{
                    margin: 0 0 15px 0;
                    color: #2d3748;
                    font-size: 20px;
                    font-weight: 600;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }}
                .summary-item {{
                    background: white;
                    padding: 12px;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }}
                .summary-label {{
                    font-size: 12px;
                    color: #718096;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 4px;
                }}
                .summary-value {{
                    font-size: 14px;
                    color: #2d3748;
                    font-weight: 600;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .status-critical {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; }}
                .status-high {{ background: linear-gradient(135deg, #fd7e14, #e55a00); color: white; }}
                .status-medium {{ background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }}
                .status-low {{ background: linear-gradient(135deg, #28a745, #1e7e34); color: white; }}
                .status-ok {{ background: linear-gradient(135deg, #28a745, #1e7e34); color: white; }}
                .status-error {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; }}
                .details-section {{
                    margin-bottom: 25px;
                }}
                .details-section h3 {{
                    color: #2d3748;
                    font-size: 18px;
                    font-weight: 600;
                    margin: 0 0 15px 0;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .details-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                }}
                .detail-item {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }}
                .detail-label {{
                    font-size: 12px;
                    color: #718096;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 6px;
                }}
                .detail-value {{
                    font-size: 14px;
                    color: #2d3748;
                    font-weight: 500;
                    word-break: break-word;
                }}
                .footer {{ 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 20px 30px; 
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                }}
                .footer p {{
                    margin: 5px 0;
                    color: #718096;
                    font-size: 13px;
                }}
                .footer .system-name {{
                    font-weight: 600;
                    color: #667eea;
                }}
                @media (max-width: 600px) {{
                    .container {{ margin: 10px; }}
                    .content {{ padding: 20px; }}
                    .header {{ padding: 20px; }}
                    .header h1 {{ font-size: 24px; }}
                    .summary-grid {{ grid-template-columns: 1fr; }}
                    .details-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 告警通知</h1>
                    <div class="subtitle">BigDataOps 监控系统</div>
                </div>
                
                <div class="content">
                    <div class="alert-summary">
                        <h2>📋 告警概览</h2>
                        <div class="summary-grid">
                            {summary_items}
                        </div>
                    </div>
                    
                    <div class="details-section">
                        <h3>📊 告警详情</h3>
                        <div class="details-grid">
                            {detail_items}
                        </div>
                    </div>
                    
                    {labels_section}
                    
                    <div class="details-section">
                        <h3>🔍 故障排查建议</h3>
                        <div class="detail-item">
                            <ul style="margin: 0; padding-left: 20px; color: #2d3748;">
                                <li>检查服务进程是否正常运行</li>
                                <li>检查端口是否被占用或被防火墙阻止</li>
                                <li>检查网络连接是否正常</li>
                                <li>查看服务日志获取详细错误信息</li>
                                <li>检查系统资源使用情况</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>此邮件由 <span class="system-name">BigDataOps</span> 告警系统自动发送</p>
                    <p>发送时间：{trigger_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 使用自定义主题模板或默认模板
        subject_template = template_data.get('subject_template', default_subject)
        
        logger.info(f"主题模板: {subject_template}")
        logger.info(f"要显示的参数: {email_params}")
        
        # 生成概览项
        summary_items = ""
        summary_params = ['rule_name', 'level', 'trigger_time']
        for param in summary_params:
            if param in email_params and param in alert_context:
                value = alert_context[param]
                if param == 'level':
                    # 将告警等级转换为中文显示
                    level_display = get_level_display(value)
                    value = f'<span class="status-badge status-{value.lower()}">{level_display}</span>'
                summary_items += f"""
                <div class="summary-item">
                    <div class="summary-label">{get_param_label(param)}</div>
                    <div class="summary-value">{value}</div>
                </div>
                """
        
        # 生成详情项
        detail_items = ""
        detail_params = ['category', 'condition', 'current_value', 'promql', 'description', 'level']
        for param in detail_params:
            if param in email_params and param in alert_context:
                value = alert_context[param]
                if param == 'current_value':
                    value = f'<span class="status-badge status-error">{value}</span>'
                elif param == 'promql':
                    value = f'<code style="background: #f1f3f4; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{value}</code>'
                elif param == 'level':
                    # 将告警等级转换为中文显示
                    level_display = get_level_display(value)
                    value = f'<span class="status-badge status-{value.lower()}">{level_display}</span>'
                detail_items += f"""
                <div class="detail-item">
                    <div class="detail-label">{get_param_label(param)}</div>
                    <div class="detail-value">{value}</div>
                </div>
                """
        
        # 生成标签项
        labels_section = ""
        label_params = ['name', 'port', 'instance', 'job', 'service', 'group', 'role']
        label_items = ""
        has_labels = False
        
        # 从email_params中筛选标签参数
        for param in label_params:
            if param in email_params and param in alert_context:
                has_labels = True
                value = alert_context[param]
                label_items += f"""
                <div class="detail-item">
                    <div class="detail-label">{get_param_label(param)}</div>
                    <div class="detail-value">{value}</div>
                </div>
                """
        
        # 从labels中获取其他标签
        if 'labels' in alert_context and alert_context['labels']:
            for key, value in alert_context['labels'].items():
                # 跳过内部标签和已显示的标签
                if not key.startswith('__') and key not in label_params:
                    has_labels = True
                    label_items += f"""
                    <div class="detail-item">
                        <div class="detail-label">{key}</div>
                        <div class="detail-value">{value}</div>
                    </div>
                    """
        
        if has_labels:
            labels_section = f"""
            <div class="details-section">
                <h3>🏷️ 指标标签</h3>
                <div class="details-grid">
                    {label_items}
                </div>
            </div>
            """
        
        # 格式化模板
        subject = subject_template.format(**alert_context)
        # 移除故障排查建议
        content = html_template.format(
            summary_items=summary_items,
            detail_items=detail_items,
            labels_section=labels_section,
            trigger_time=alert_context.get('trigger_time', '')
        )
        # 去除“故障排查建议”相关内容
        import re
        content = re.sub(r'<div class="details-section">\s*<h3>[^<]*故障排查建议[^<]*</h3>[\s\S]*?</div>', '', content)
        
        # 处理邮件主题中的中文告警等级
        if 'level' in alert_context:
            level_display = get_level_display(alert_context['level'])
            subject = subject.replace('{level_display}', level_display)
        
        logger.info(f"渲染后的主题: {subject}")
        logger.info(f"渲染后的内容: {content}")
        return subject, content
        
    except Exception as e:
        logger.error(f"邮件模板渲染失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        # 返回一个基础的HTML模板而不是原始字典
        fallback_subject = f"告警通知 - {alert_context.get('rule_name', 'Unknown')}"
        fallback_content = f"""
        <html>
        <body>
            <h2>告警通知</h2>
            <p><strong>规则名称：</strong>{alert_context.get('rule_name', 'Unknown')}</p>
            <p><strong>告警等级：</strong>{alert_context.get('level', 'Unknown')}</p>
            <p><strong>当前值：</strong>{alert_context.get('current_value', 'Unknown')}</p>
            <p><strong>触发时间：</strong>{alert_context.get('trigger_time', 'Unknown')}</p>
            <p><strong>触发条件：</strong>{alert_context.get('condition', 'Unknown')}</p>
            <hr>
            <p><small>模板渲染失败，显示基础信息。详细错误请查看日志。</small></p>
        </body>
        </html>
        """
        return fallback_subject, fallback_content 