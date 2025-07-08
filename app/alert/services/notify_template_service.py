from app.models import SessionLocal, AlertNotifyTemplate
from sqlalchemy.orm import Session
from typing import List, Optional
import json

def get_templates(db: Session, type: Optional[str] = None) -> List[AlertNotifyTemplate]:
    query = db.query(AlertNotifyTemplate)
    if type:
        query = query.filter(AlertNotifyTemplate.type == type)
    return query.order_by(AlertNotifyTemplate.created_at.desc()).all()

def get_template(db: Session, template_id: int) -> Optional[AlertNotifyTemplate]:
    return db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == template_id).first()

def create_template(db: Session, name: str, type: str, params: dict) -> AlertNotifyTemplate:
    # 唯一性校验：type+params
    params_json = json.dumps(params, sort_keys=True)
    exists = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.type == type, AlertNotifyTemplate.params == params_json).first()
    if exists:
        return exists
    tpl = AlertNotifyTemplate(name=name, type=type, params=params_json)
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl

def update_template(db: Session, template_id: int, name: str, params: dict) -> Optional[AlertNotifyTemplate]:
    tpl = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == template_id).first()
    if not tpl:
        return None
    tpl.name = name
    tpl.params = json.dumps(params, sort_keys=True)
    db.commit()
    db.refresh(tpl)
    return tpl

def delete_template(db: Session, template_id: int) -> bool:
    tpl = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == template_id).first()
    if not tpl:
        return False
    db.delete(tpl)
    db.commit()
    return True 