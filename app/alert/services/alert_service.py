# Webhook告警分发服务

from app.alert.downstream.email import send_email_msg
from app.alert.downstream.http import send_http_msg
from app.alert.downstream.lechat import send_lechat_msg
from app.models import SessionLocal, AlertNotifyTemplate
import logging
import json

logger = logging.getLogger("alert_service")

def parse_and_dispatch_alert(data: dict):
    """
    解析外部webhook告警内容，分发到不同下游
    data结构示例：
    {
        "level": "critical",
        "downstream": "email",  # email/http
        "params": { ... },    # 发送下游所需参数
        "notify_template_id": 1  # 可选，优先加载模板参数
    }
    """
    level = data.get("level", "info")
    downstream = data.get("downstream", "email")
    params = data.get("params", {})
    notify_template_id = data.get("notify_template_id")
    
    # 若有模板，加载并合并参数
    if notify_template_id:
        db = SessionLocal()
        try:
            tpl = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == notify_template_id).first()
            if tpl:
                tpl_params = json.loads(tpl.params)
                # 模板参数优先级低于params
                merged = {**tpl_params, **params}
                params = merged
        finally:
            db.close()
    
    logger.info(f"收到外部告警: level={level}, downstream={downstream}")
    
    if downstream == "email":
        return send_email_msg(params)
    elif downstream == "http":
        return send_http_msg(params)
    elif downstream == "lechat":
        return send_lechat_msg(params)
    else:
        logger.warning(f"不支持的下游类型: {downstream}")
        return {"success": False, "msg": f"不支持的下游类型: {downstream}"} 