# 迁移自alert_module.py
# ... existing code ... 

from fastapi import APIRouter, Request, Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from app.models import SessionLocal
from app.models.alert_schemas import CommonResponse
from app.alert.services.alert_service import parse_and_dispatch_alert
from app.alert.services.engine_service import (
    start_alert_engine, 
    stop_alert_engine, 
    get_alert_engine_status,
    alert_engine_job
)
from app.utils.logger import logger

router = APIRouter()
logger = logging.getLogger("alert_controller")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/alert/webhook")
async def alert_webhook(request: Request):
    data = await request.json()
    logger.info(f"收到Alertmanager告警: {data}")
    result = parse_and_dispatch_alert(data)
    return result 

@router.post("/alert/engine/start", response_model=CommonResponse[dict])
def start_engine():
    """启动告警引擎"""
    try:
        start_alert_engine()
        return {"code": 0, "data": {"status": "started"}, "msg": "告警引擎启动成功"}
    except Exception as e:
        logger.error(f"启动告警引擎失败: {e}")
        return {"code": 1, "data": None, "msg": f"启动失败: {str(e)}"}

@router.post("/alert/engine/stop", response_model=CommonResponse[dict])
def stop_engine():
    """停止告警引擎"""
    try:
        stop_alert_engine()
        return {"code": 0, "data": {"status": "stopped"}, "msg": "告警引擎停止成功"}
    except Exception as e:
        logger.error(f"停止告警引擎失败: {e}")
        return {"code": 1, "data": None, "msg": f"停止失败: {str(e)}"}

@router.get("/alert/engine/status", response_model=CommonResponse[dict])
def get_engine_status():
    """获取告警引擎状态"""
    try:
        status = get_alert_engine_status()
        return {"code": 0, "data": status, "msg": "获取状态成功"}
    except Exception as e:
        logger.error(f"获取告警引擎状态失败: {e}")
        return {"code": 1, "data": None, "msg": f"获取状态失败: {str(e)}"}

@router.post("/alert/engine/test", response_model=CommonResponse[dict])
def test_engine():
    """手动触发一次告警检测（测试用）"""
    try:
        alert_engine_job()
        return {"code": 0, "data": {"status": "executed"}, "msg": "手动执行告警检测成功"}
    except Exception as e:
        logger.error(f"手动执行告警检测失败: {e}")
        return {"code": 1, "data": None, "msg": f"执行失败: {str(e)}"} 