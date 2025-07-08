from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import SessionLocal
from app.models.alert_schemas import AlertRuleOut, CommonResponse
from app.alert.services import rule_service
from app.utils.logger import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/alert/rule", response_model=CommonResponse[dict])
def list_rules(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="组件分组筛选"),
    level: Optional[str] = Query(None, description="告警等级筛选"),
    enabled: Optional[bool] = Query(None, description="启用状态筛选"),
    alert_state: Optional[str] = Query(None, description="告警状态筛选"),
    name: Optional[str] = Query(None, description="规则名称搜索")
):
    """
    获取告警规则列表
    支持分页和多条件筛选
    """
    try:
        result = rule_service.get_rules_with_filter(db, page, size, category, level, enabled, alert_state, name)
        return {"code": 0, "data": result, "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询规则异常: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.get("/alert/rule/categories", response_model=CommonResponse[List[str]])
def get_rule_categories(db: Session = Depends(get_db)):
    """获取所有规则分组列表"""
    try:
        categories = rule_service.get_categories(db)
        return {"code": 0, "data": categories, "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询规则分组失败: {e}")
        return {"code": 1, "data": [], "msg": f"查询失败: {str(e)}"}

@router.get("/alert/rule/stats", response_model=CommonResponse[dict])
def get_rule_stats(db: Session = Depends(get_db)):
    """获取规则统计信息"""
    try:
        stats = rule_service.get_rule_stats(db)
        return {"code": 0, "data": stats, "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询规则统计失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.get("/alert/rule/{rule_id}", response_model=CommonResponse[AlertRuleOut])
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    try:
        rule = rule_service.get_rule(db, rule_id)
        if not rule:
            return {"code": 1, "data": None, "msg": "未找到规则"}
        return {"code": 0, "data": AlertRuleOut.model_validate(rule), "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询规则异常: {e}")
        return {"code": 1, "data": None, "msg": "查询失败"}

@router.post("/alert/rule", response_model=CommonResponse[AlertRuleOut])
def create_rule(rule: dict, db: Session = Depends(get_db)):
    try:
        # 设置默认值
        if 'category' not in rule:
            rule['category'] = 'other'
        if 'alert_state' not in rule:
            rule['alert_state'] = 'ok'
        
        db_rule = rule_service.create_rule(db, rule)
        if db_rule:
            logger.info(f"创建规则成功: {db_rule.id}, 分组: {db_rule.category}")
            return {"code": 0, "data": AlertRuleOut.model_validate(db_rule), "msg": "创建成功"}
        else:
            logger.warning("创建规则失败")
            return {"code": 1, "data": None, "msg": "创建失败"}
    except Exception as e:
        logger.error(f"创建规则异常: {e}")
        return {"code": 1, "data": None, "msg": f"创建失败: {str(e)}"}

@router.put("/alert/rule/{rule_id}", response_model=CommonResponse[AlertRuleOut])
def update_rule(rule_id: int, rule: dict, db: Session = Depends(get_db)):
    try:
        db_rule = rule_service.update_rule(db, rule_id, rule)
        if not db_rule:
            return {"code": 1, "data": None, "msg": "未找到规则"}
        logger.info(f"更新规则成功: {db_rule.id}, 分组: {db_rule.category}")
        return {"code": 0, "data": AlertRuleOut.model_validate(db_rule), "msg": "修改成功"}
    except Exception as e:
        logger.error(f"修改规则异常: {e}")
        return {"code": 1, "data": None, "msg": f"修改失败: {str(e)}"}

@router.delete("/alert/rule/{rule_id}", response_model=CommonResponse[dict])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    try:
        ok = rule_service.delete_rule(db, rule_id)
        if not ok:
            return {"code": 1, "data": None, "msg": "未找到规则"}
        return {"code": 0, "data": {"success": True}, "msg": "删除成功"}
    except Exception as e:
        logger.error(f"删除规则异常: {e}")
        return {"code": 1, "data": None, "msg": "删除失败"}

@router.post("/alert/rule/batch_update_category", response_model=CommonResponse[dict])
def batch_update_category(
    rule_ids: List[int],
    category: str,
    db: Session = Depends(get_db)
):
    """批量更新规则分组"""
    try:
        updated_count = rule_service.batch_update_category(db, rule_ids, category)
        return {
            "code": 0,
            "data": {"updated_count": updated_count},
            "msg": f"成功更新 {updated_count} 条规则的分组"
        }
    except Exception as e:
        logger.error(f"批量更新分组失败: {e}")
        return {"code": 1, "data": None, "msg": f"更新失败: {str(e)}"}