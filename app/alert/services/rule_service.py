from app.models import SessionLocal, AlertRule, AlertNotifyTemplate
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, case
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

# 获取所有规则
def get_rules(db: Session) -> List[AlertRule]:
    """
    查询所有告警规则
    """
    return db.query(AlertRule).all()

# 获取规则列表（支持筛选和分页）
def get_rules_with_filter(db: Session, page: int, size: int, 
                         category: Optional[str] = None,
                         level: Optional[str] = None,
                         enabled: Optional[bool] = None,
                         alert_state: Optional[str] = None,
                         name: Optional[str] = None) -> Dict[str, Any]:
    """
    获取告警规则列表，支持分页和多条件筛选
    """
    query = db.query(AlertRule)
    
    # 组件分组筛选
    if category:
        query = query.filter(AlertRule.category == category)
    
    # 告警等级筛选
    if level:
        query = query.filter(AlertRule.level == level)
    
    # 启用状态筛选
    if enabled is not None:
        query = query.filter(AlertRule.enabled == enabled)
    
    # 告警状态筛选
    if alert_state:
        query = query.filter(AlertRule.alert_state == alert_state)
    
    # 规则名称搜索
    if name:
        query = query.filter(AlertRule.name.like(f"%{name}%"))
    
    # 总数统计
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    rules = query.order_by(desc(AlertRule.created_at)).offset(offset).limit(size).all()
    
    # 格式化返回数据
    rule_list = []
    for rule in rules:
        rule_dict = {
            "id": rule.id,
            "name": rule.name,
            "category": rule.category,
            "promql": rule.promql,
            "condition": rule.condition,
            "level": rule.level,
            "description": rule.description,
            "labels": rule.labels,
            "suppress": rule.suppress,
            "repeat": rule.repeat,
            "enabled": rule.enabled,
            "alert_state": rule.alert_state,
            "last_alert_time": rule.last_alert_time.isoformat() if rule.last_alert_time else None,
            "notify_template_id": rule.notify_template_id,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat()
        }
        rule_list.append(rule_dict)
    
    return {
        "items": rule_list,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

# 获取分组列表
def get_categories(db: Session) -> List[str]:
    """获取所有规则分组列表"""
    categories = db.query(AlertRule.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]

# 获取规则统计
def get_rule_stats(db: Session) -> Dict[str, Any]:
    """获取规则统计信息"""
    # 总体统计
    total_rules = db.query(AlertRule).count()
    enabled_rules = db.query(AlertRule).filter(AlertRule.enabled == True).count()
    alerting_rules = db.query(AlertRule).filter(AlertRule.alert_state == 'alerting').count()
    
    # 按分组统计
    category_stats = db.query(
        AlertRule.category,
        func.count(AlertRule.id).label('total_count'),
        func.sum(case((AlertRule.enabled == True, 1), else_=0)).label('enabled_count'),
        func.sum(case((AlertRule.alert_state == 'alerting', 1), else_=0)).label('alerting_count')
    ).group_by(AlertRule.category).all()
    
    # 按等级统计
    level_stats = db.query(
        AlertRule.level,
        func.count(AlertRule.id).label('count')
    ).group_by(AlertRule.level).all()
    
    # 格式化统计数据
    category_data = []
    for stat in category_stats:
        category_data.append({
            "category": stat.category,
            "total_count": stat.total_count,
            "enabled_count": stat.enabled_count or 0,
            "alerting_count": stat.alerting_count or 0
        })
    
    level_data = []
    for stat in level_stats:
        level_data.append({
            "level": stat.level,
            "count": stat.count
        })
    
    return {
        "total_rules": total_rules,
        "enabled_rules": enabled_rules,
        "alerting_rules": alerting_rules,
        "category_stats": category_data,
        "level_stats": level_data
    }

# 获取单条规则
def get_rule(db: Session, rule_id: int) -> Optional[AlertRule]:
    """
    根据ID查询单条告警规则
    """
    return db.query(AlertRule).filter(AlertRule.id == rule_id).first()

# 创建规则
def create_rule(db: Session, rule: Dict[str, Any]) -> AlertRule:
    """
    创建新的告警规则，若notify_template_id不存在则抛出异常
    """
    notify_template_id = rule.get('notify_template_id')
    if notify_template_id is not None:
        tpl = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == notify_template_id).first()
        if not tpl:
            raise HTTPException(status_code=400, detail="请选择需要发送的下游告警（通知模板不存在）")
    
    db_rule = AlertRule(**rule)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# 更新规则
def update_rule(db: Session, rule_id: int, rule_data: Dict[str, Any]) -> Optional[AlertRule]:
    """
    更新指定ID的告警规则
    """
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        return None
    
    # 验证通知模板
    notify_template_id = rule_data.get('notify_template_id')
    if notify_template_id is not None:
        tpl = db.query(AlertNotifyTemplate).filter(AlertNotifyTemplate.id == notify_template_id).first()
        if not tpl:
            raise HTTPException(status_code=400, detail="通知模板不存在")
    
    for k, v in rule_data.items():
        setattr(db_rule, k, v)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# 删除规则
def delete_rule(db: Session, rule_id: int) -> bool:
    """
    删除指定ID的告警规则
    """
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        return False
    db.delete(db_rule)
    db.commit()
    return True

# 批量更新分组
def batch_update_category(db: Session, rule_ids: List[int], category: str) -> int:
    """
    批量更新规则分组
    """
    updated_count = db.query(AlertRule).filter(
        AlertRule.id.in_(rule_ids)
    ).update(
        {"category": category},
        synchronize_session=False
    )
    db.commit()
    return updated_count 