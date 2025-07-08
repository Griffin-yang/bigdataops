from sqlalchemy.orm import Session
from app.models.alert_models import AlertHistory
from typing import List, Optional
from datetime import datetime

def get_history(db: Session, rule_id: Optional[int] = None) -> List[AlertHistory]:
    query = db.query(AlertHistory)
    if rule_id is not None:
        query = query.filter(AlertHistory.rule_id == rule_id)
    return query.order_by(AlertHistory.created_at.desc()).all()

def get_history_by_id(db: Session, history_id: int) -> Optional[AlertHistory]:
    return db.query(AlertHistory).filter(AlertHistory.id == history_id).first()

def create_history(db: Session, rule_id: int, status: str, message: str, 
                  notified: bool = False, notified_at: Optional[datetime] = None) -> AlertHistory:
    """创建告警历史记录"""
    history = AlertHistory(
        rule_id=rule_id,
        status=status,
        message=message,
        notified=notified,
        notified_at=notified_at
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

def delete_history(db: Session, history_id: int) -> bool:
    history = db.query(AlertHistory).filter(AlertHistory.id == history_id).first()
    if not history:
        return False
    db.delete(history)
    db.commit()
    return True 