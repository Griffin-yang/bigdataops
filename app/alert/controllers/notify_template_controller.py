from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import SessionLocal, AlertNotifyTemplate
from app.models.alert_schemas import AlertNotifyTemplateOut, CommonResponse
from app.alert.services import notify_template_service
import json
from app.utils.logger import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/alert/notify_template", response_model=CommonResponse[List[AlertNotifyTemplateOut]])
def list_templates(type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        tpls = notify_template_service.get_templates(db, type)
        for tpl in tpls:
            if isinstance(tpl.params, str):
                try:
                    tpl.params = json.loads(tpl.params)
                except Exception:
                    tpl.params = {}
        return {"code": 0, "data": [AlertNotifyTemplateOut.model_validate(t) for t in tpls], "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询通知模板异常: {e}")
        return {"code": 1, "data": None, "msg": "查询失败"}

@router.get("/alert/notify_template/{template_id}", response_model=CommonResponse[AlertNotifyTemplateOut])
def get_template(template_id: int, db: Session = Depends(get_db)):
    try:
        tpl = notify_template_service.get_template(db, template_id)
        if not tpl:
            return {"code": 1, "data": None, "msg": "未找到模板"}
        if isinstance(tpl.params, str):
            try:
                tpl.params = json.loads(tpl.params)
            except Exception:
                tpl.params = {}
        return {"code": 0, "data": AlertNotifyTemplateOut.model_validate(tpl), "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询通知模板异常: {e}")
        return {"code": 1, "data": None, "msg": "查询失败"}

@router.post("/alert/notify_template", response_model=CommonResponse[AlertNotifyTemplateOut])
def create_template(data: dict, db: Session = Depends(get_db)):
    try:
        tpl = notify_template_service.create_template(db, data['name'], data['type'], data['params'])
        if isinstance(tpl.params, str):
            try:
                tpl.params = json.loads(tpl.params)
            except Exception:
                tpl.params = {}
        return {"code": 0, "data": AlertNotifyTemplateOut.model_validate(tpl), "msg": "创建成功"}
    except Exception as e:
        logger.error(f"创建通知模板异常: {e}")
        return {"code": 1, "data": None, "msg": "创建失败"}

@router.put("/alert/notify_template/{template_id}", response_model=CommonResponse[AlertNotifyTemplateOut])
def update_template(template_id: int, data: dict, db: Session = Depends(get_db)):
    try:
        tpl = notify_template_service.update_template(db, template_id, data['name'], data['params'])
        if not tpl:
            return {"code": 1, "data": None, "msg": "未找到模板"}
        if isinstance(tpl.params, str):
            try:
                tpl.params = json.loads(tpl.params)
            except Exception:
                tpl.params = {}
        return {"code": 0, "data": AlertNotifyTemplateOut.model_validate(tpl), "msg": "修改成功"}
    except Exception as e:
        logger.error(f"修改通知模板异常: {e}")
        return {"code": 1, "data": None, "msg": "修改失败"}

@router.delete("/alert/notify_template/{template_id}", response_model=CommonResponse[dict])
def delete_template(template_id: int, db: Session = Depends(get_db)):
    try:
        ok = notify_template_service.delete_template(db, template_id)
        if not ok:
            return {"code": 1, "data": None, "msg": "未找到模板"}
        return {"code": 0, "data": {"success": True}, "msg": "删除成功"}
    except Exception as e:
        logger.error(f"删除通知模板异常: {e}")
        return {"code": 1, "data": None, "msg": "删除失败"} 