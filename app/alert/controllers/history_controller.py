from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models import SessionLocal, AlertHistory
from app.models.alert_schemas import CommonResponse
from app.utils.logger import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 解决告警请求模型
class ResolveAlertRequest(BaseModel):
    reason: Optional[str] = None

@router.get("/alert/history", response_model=CommonResponse[dict])
def get_alert_history(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="组件分组筛选"),
    level: Optional[str] = Query(None, description="告警等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    rule_name: Optional[str] = Query(None, description="规则名称搜索"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)")
):
    """
    获取告警历史记录
    支持分组查询、分页、多条件筛选
    """
    try:
        query = db.query(AlertHistory)
        
        # 组件分组筛选
        if category:
            query = query.filter(AlertHistory.category == category)
        
        # 告警等级筛选
        if level:
            query = query.filter(AlertHistory.level == level)
        
        # 状态筛选
        if status:
            query = query.filter(AlertHistory.status == status)
        
        # 规则名称搜索
        if rule_name:
            query = query.filter(AlertHistory.rule_name.like(f"%{rule_name}%"))
        
        # 时间范围筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AlertHistory.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(AlertHistory.created_at < end_datetime)
        
        # 总数统计
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * size
        histories = query.order_by(desc(AlertHistory.created_at)).offset(offset).limit(size).all()
        
        # 格式化返回数据
        history_list = []
        for history in histories:
            history_dict = {
                "id": history.id,
                "rule_id": history.rule_id,
                "rule_name": history.rule_name,
                "category": history.category,
                "level": history.level,
                "status": history.status,
                "message": history.message,
                "alert_value": history.alert_value,
                "condition": history.condition,
                "labels": history.labels,
                "notified": history.notified,
                "notified_at": history.notified_at.isoformat() if history.notified_at else None,
                "resolved_at": history.resolved_at.isoformat() if history.resolved_at else None,
                "fired_at": history.created_at.isoformat(),  # 添加fired_at字段
                "created_at": history.created_at.isoformat(),
                "acknowledged": history.acknowledged,  # 添加确认状态字段
                "acknowledged_at": history.acknowledged_at.isoformat() if history.acknowledged_at else None,
                "acknowledged_by": history.acknowledged_by
            }
            history_list.append(history_dict)
        
        return {
            "code": 0,
            "data": {
                "items": history_list,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "msg": "查询成功"
        }
        
    except Exception as e:
        logger.error(f"查询告警历史失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.get("/alert/history/stats", response_model=CommonResponse[dict])
def get_alert_history_stats(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30, description="统计天数")
):
    """
    获取告警历史统计数据
    按组件分组统计最近N天的告警情况
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # 总体统计数据
        total_alerts = db.query(AlertHistory).filter(
            AlertHistory.created_at >= start_date
        ).count()
        
        firing_alerts = db.query(AlertHistory).filter(
            AlertHistory.created_at >= start_date,
            AlertHistory.status == 'triggered'
        ).count()
        
        resolved_alerts = db.query(AlertHistory).filter(
            AlertHistory.created_at >= start_date,
            AlertHistory.status == 'recovered'
        ).count()
        
        # 按分组统计告警数量
        category_stats = db.query(
            AlertHistory.category,
            func.count(AlertHistory.id).label('total_count'),
            func.sum(case((AlertHistory.level == 'critical', 1), else_=0)).label('critical_count'),
            func.sum(case((AlertHistory.level == 'high', 1), else_=0)).label('high_count'),
            func.sum(case((AlertHistory.level == 'medium', 1), else_=0)).label('medium_count'),
            func.sum(case((AlertHistory.level == 'low', 1), else_=0)).label('low_count'),
            func.sum(case((AlertHistory.notified == True, 1), else_=0)).label('notified_count')
        ).filter(
            AlertHistory.created_at >= start_date
        ).group_by(AlertHistory.category).all()
        
        # 按日期统计趋势
        daily_stats = db.query(
            func.date(AlertHistory.created_at).label('date'),
            func.count(AlertHistory.id).label('count')
        ).filter(
            AlertHistory.created_at >= start_date
        ).group_by(func.date(AlertHistory.created_at)).order_by('date').all()
        
        # 格式化统计数据
        category_data = []
        for stat in category_stats:
            category_data.append({
                "category": stat.category,
                "total_count": stat.total_count,
                "critical_count": stat.critical_count or 0,
                "high_count": stat.high_count or 0,
                "medium_count": stat.medium_count or 0,
                "low_count": stat.low_count or 0,
                "notified_count": stat.notified_count or 0
            })
        
        daily_data = []
        for stat in daily_stats:
            daily_data.append({
                "date": stat.date.strftime("%Y-%m-%d"),
                "count": stat.count
            })
        
        return {
            "code": 0,
            "data": {
                "total_alerts": total_alerts,
                "firing_alerts": firing_alerts,
                "resolved_alerts": resolved_alerts,
                "category_stats": category_data,
                "daily_stats": daily_data,
                "period_days": days
            },
            "msg": "查询成功"
        }
        
    except Exception as e:
        logger.error(f"查询告警统计失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.get("/alert/history/categories", response_model=CommonResponse[List[str]])
def get_alert_categories(db: Session = Depends(get_db)):
    """获取所有告警分组列表"""
    try:
        categories = db.query(AlertHistory.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return {
            "code": 0,
            "data": category_list,
            "msg": "查询成功"
        }
    except Exception as e:
        logger.error(f"查询告警分组失败: {e}")
        return {"code": 1, "data": [], "msg": f"查询失败: {str(e)}"}

@router.delete("/alert/history/{history_id}", response_model=CommonResponse[dict])
def delete_alert_history(history_id: int, db: Session = Depends(get_db)):
    """删除告警历史记录"""
    try:
        history = db.query(AlertHistory).filter(AlertHistory.id == history_id).first()
        if not history:
            return {"code": 1, "data": None, "msg": "历史记录不存在"}
        
        db.delete(history)
        db.commit()
        
        return {"code": 0, "data": {"id": history_id}, "msg": "删除成功"}
    except Exception as e:
        logger.error(f"删除告警历史失败: {e}")
        db.rollback()
        return {"code": 1, "data": None, "msg": f"删除失败: {str(e)}"}

@router.post("/alert/history/batch_delete", response_model=CommonResponse[dict])
def batch_delete_alert_history(
    history_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量删除告警历史记录"""
    try:
        deleted_count = db.query(AlertHistory).filter(
            AlertHistory.id.in_(history_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "code": 0,
            "data": {"deleted_count": deleted_count},
            "msg": f"成功删除 {deleted_count} 条记录"
        }
    except Exception as e:
        logger.error(f"批量删除告警历史失败: {e}")
        db.rollback()
        return {"code": 1, "data": None, "msg": f"删除失败: {str(e)}"}

@router.post("/alert/history/{history_id}/acknowledge", response_model=CommonResponse[dict])
def acknowledge_alert(
    history_id: int,
    acknowledged_by: str = Query(..., description="确认人"),
    db: Session = Depends(get_db)
):
    """确认告警，停止继续发送"""
    try:
        # 更新告警历史记录
        history = db.query(AlertHistory).filter(AlertHistory.id == history_id).first()
        if not history:
            return {"code": 1, "data": None, "msg": "告警历史记录不存在"}
        
        history.acknowledged = True
        history.acknowledged_at = datetime.now()
        history.acknowledged_by = acknowledged_by
        
        # 将对应的告警规则状态设置为静默，停止发送
        from app.models import AlertRule
        rule = db.query(AlertRule).filter(AlertRule.id == history.rule_id).first()
        if rule and rule.alert_state == 'alerting':
            rule.alert_state = 'silenced'
            logger.info(f"告警规则 {rule.name} 已被手动确认，状态设为静默")
        
        db.commit()
        
        return {
            "code": 0,
            "data": {
                "history_id": history_id,
                "acknowledged_by": acknowledged_by,
                "acknowledged_at": history.acknowledged_at.isoformat()
            },
            "msg": "告警确认成功，已停止发送"
        }
        
    except Exception as e:
        logger.error(f"确认告警失败: {e}")
        db.rollback()
        return {"code": 1, "data": None, "msg": f"确认失败: {str(e)}"}

@router.post("/alert/rule/{rule_id}/acknowledge", response_model=CommonResponse[dict])
def acknowledge_rule_alert(
    rule_id: int,
    acknowledged_by: str = Query(..., description="确认人"),
    db: Session = Depends(get_db)
):
    """确认规则的所有告警，停止继续发送"""
    try:
        from app.models import AlertRule
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            return {"code": 1, "data": None, "msg": "告警规则不存在"}
        
        # 将规则状态设置为静默
        if rule.alert_state in ['alerting']:
            rule.alert_state = 'silenced'
            
            # 更新最近的告警历史记录为已确认
            recent_history = db.query(AlertHistory).filter(
                AlertHistory.rule_id == rule_id,
                AlertHistory.acknowledged == False
            ).order_by(AlertHistory.created_at.desc()).first()
            
            if recent_history:
                recent_history.acknowledged = True
                recent_history.acknowledged_at = datetime.now()
                recent_history.acknowledged_by = acknowledged_by
            
            db.commit()
            
            logger.info(f"告警规则 {rule.name} 已被手动确认，状态设为静默")
            
            return {
                "code": 0,
                "data": {
                    "rule_id": rule_id,
                    "acknowledged_by": acknowledged_by,
                    "previous_state": 'alerting'
                },
                "msg": "规则告警确认成功，已停止发送"
            }
        else:
            return {"code": 1, "data": None, "msg": f"规则当前状态为 {rule.alert_state}，无需确认"}
        
    except Exception as e:
        logger.error(f"确认规则告警失败: {e}")
        db.rollback()
        return {"code": 1, "data": None, "msg": f"确认失败: {str(e)}"} 

@router.post("/alert/history/{history_id}/resolve", response_model=CommonResponse[dict])
def resolve_alert(
    history_id: int,
    request: ResolveAlertRequest,
    db: Session = Depends(get_db)
):
    """手动解决告警"""
    try:
        # 查找告警历史记录
        history = db.query(AlertHistory).filter(AlertHistory.id == history_id).first()
        if not history:
            return {"code": 1, "data": None, "msg": "告警历史记录不存在"}
        
        # 检查告警状态
        if history.status == 'recovered':
            return {"code": 1, "data": None, "msg": "告警已经解决"}
        
        # 更新告警状态为已解决
        history.status = 'recovered'
        history.resolved_at = datetime.now()
        
        # 如果有解决原因，可以存储到message字段或新增字段
        if request.reason:
            history.message = f"{history.message}\n\n解决原因: {request.reason}"
        
        # 将对应的告警规则状态设置为正常
        from app.models import AlertRule
        rule = db.query(AlertRule).filter(AlertRule.id == history.rule_id).first()
        if rule and rule.alert_state == 'alerting':
            rule.alert_state = 'ok'
            logger.info(f"告警规则 {rule.name} 已被手动解决，状态设为正常")
        
        db.commit()
        
        return {
            "code": 0,
            "data": {
                "history_id": history_id,
                "resolved_at": history.resolved_at.isoformat(),
                "reason": request.reason
            },
            "msg": "告警已解决"
        }
        
    except Exception as e:
        logger.error(f"解决告警失败: {e}")
        db.rollback()
        return {"code": 1, "data": None, "msg": f"解决失败: {str(e)}"} 