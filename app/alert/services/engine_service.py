from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import SessionLocal, AlertRule, AlertNotifyTemplate, AlertHistory
from app.alert.downstream.email import send_email_msg, render_email_template
from app.alert.downstream.http import send_http_msg, render_http_template
from app.alert.downstream.lechat import send_lechat_msg, render_lechat_template
from app.utils.logger import logger
from app.config import get_settings

# 全局调度器实例
scheduler = None

def _get_scheduler():
    """获取或创建调度器实例"""
    global scheduler
    if scheduler is None:
        # 配置调度器执行器，限制最大线程数
        executors = {
            'default': ThreadPoolExecutor(max_workers=2)
        }
        
        # 调度器配置
        job_defaults = {
            'coalesce': False,  # 不合并任务
            'max_instances': 1  # 最多只能有1个实例在运行
        }
        
        scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
    return scheduler

# Prometheus配置，可以从config.py读取
PROMETHEUS_URL = get_settings().prometheus_url

def alert_engine_job():
    """告警引擎主任务"""
    logger.info("告警引擎开始执行")
    
    db = SessionLocal()
    try:
        # 获取所有启用的规则
        enabled_rules = db.query(AlertRule).filter(AlertRule.enabled == True).all()
        logger.info(f"找到 {len(enabled_rules)} 条启用的告警规则")
        
        for rule in enabled_rules:
            try:
                process_alert_rule(db, rule)
            except Exception as e:
                logger.error(f"处理规则 {rule.id}({rule.name}) 时出错: {e}")
        
    except Exception as e:
        logger.error(f"告警引擎执行异常: {e}")
    finally:
        db.close()
        
    logger.info("告警引擎执行完成")

def process_alert_rule(db: Session, rule: AlertRule):
    """处理单个告警规则"""
    try:
        logger.info(f"开始处理告警规则: {rule.name}")
        logger.info(f"PromQL: {rule.promql}")
        logger.info(f"告警条件: {rule.condition}")
        logger.info(f"当前规则状态: {rule.alert_state}")
        
        # 查询Prometheus
        query_result = query_prometheus(rule.promql)
        if query_result is None:
            logger.warning(f"规则 {rule.name} 查询无结果")
            return
        
        current_value = query_result['value']
        metric_labels = query_result['labels']
        current_time = datetime.now()
        
        logger.info(f"Prometheus查询结果: 值={current_value}, 标签={metric_labels}")
        
        # 检查告警条件
        is_triggered = check_alert_condition(current_value, rule.condition)
        logger.info(f"告警条件检查: 值={current_value}, 条件={rule.condition}, 触发={is_triggered}")
        
        # 确定告警状态
        previous_state = rule.alert_state
        new_state = determine_alert_state(previous_state, is_triggered, rule, current_time)
        logger.info(f"状态转换: {previous_state} -> {new_state}")
        
        # 检查是否需要发送通知
        should_send = should_send_notification(db, rule, previous_state, new_state, current_time, current_value)
        logger.info(f"是否需要发送通知: {should_send}")
        
        # 更新规则状态
        update_rule_state(db, rule, new_state, current_time if new_state == 'alerting' else None)
        
        # 如果需要发送通知
        if should_send:
            logger.info(f"准备发送告警通知: 规则={rule.name}, 值={current_value}")
            send_alert_and_record(db, rule, current_value, current_time, new_state, metric_labels)
        else:
            logger.info(f"不发送通知: 规则={rule.name}, 原因可能是状态未变化或处于静默期")
        
        logger.info(f"规则 {rule.name} 处理完成: 值={current_value}, 状态={new_state}, 发送={should_send}")
        
    except Exception as e:
        logger.error(f"处理告警规则 {rule.name} 失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")

def determine_alert_state(previous_state: str, is_triggered: bool, rule: AlertRule, current_time: datetime) -> str:
    """
    确定新的告警状态
    状态转换规则：
    - ok -> alerting: 触发条件
    - alerting -> ok: 恢复条件
    - alerting -> silenced: 在抑制期内或达到发送限制
    - silenced -> alerting: 超过抑制期且仍触发
    """
    if not is_triggered:
        # 告警恢复，重置计数器
        if previous_state in ['alerting', 'silenced']:
            reset_alert_counters(rule)
        return 'ok'  # 不满足触发条件，状态为正常
    
    # 检查是否是新一天，如果是则重置计数器
    check_and_reset_daily_counters(rule, current_time)
    
    if previous_state == 'ok':
        # 从正常转为告警，设置告警开始时间
        if not rule.alert_start_time:
            rule.alert_start_time = current_time
        return 'alerting'  # 从正常转为告警
    
    if previous_state == 'alerting':
        # 检查持续时间限制
        if rule.duration and rule.alert_start_time:
            if current_time >= rule.alert_start_time + timedelta(seconds=rule.duration):
                return 'silenced'  # 超过持续时间，进入静默
        
        # 检查发送次数限制
        if rule.max_send_count and rule.send_count >= rule.max_send_count:
            return 'silenced'  # 达到最大发送次数，进入静默
        
        # 检查是否需要进入静默期
        if rule.suppress and rule.last_alert_time:
            suppress_duration = parse_time_duration(rule.suppress)
            if suppress_duration and current_time < rule.last_alert_time + suppress_duration:
                return 'silenced'  # 进入静默期
        
        # 检查重复通知间隔
        if rule.repeat and rule.repeat > 0 and rule.last_alert_time:
            repeat_interval = timedelta(seconds=rule.repeat)
            if current_time < rule.last_alert_time + repeat_interval:
                return 'silenced'  # 在重复间隔内，保持静默
        
        return 'alerting'  # 继续告警状态
    
    if previous_state == 'silenced':
        # 检查持续时间限制
        if rule.duration and rule.alert_start_time:
            if current_time >= rule.alert_start_time + timedelta(seconds=rule.duration):
                return 'silenced'  # 仍在持续时间限制内
        
        # 检查发送次数限制
        if rule.max_send_count and rule.send_count >= rule.max_send_count:
            return 'silenced'  # 仍达到最大发送次数
        
        # 检查是否可以退出静默期
        if rule.suppress and rule.last_alert_time:
            suppress_duration = parse_time_duration(rule.suppress)
            if suppress_duration and current_time >= rule.last_alert_time + suppress_duration:
                return 'alerting'  # 退出静默期，重新告警
        
        if rule.repeat and rule.repeat > 0 and rule.last_alert_time:
            repeat_interval = timedelta(seconds=rule.repeat)
            if current_time >= rule.last_alert_time + repeat_interval:
                return 'alerting'  # 超过重复间隔，可以重新告警
        
        return 'silenced'  # 继续静默
    
    return 'alerting'  # 默认返回告警状态

def should_send_notification(db: Session, rule: AlertRule, previous_state: str, 
                           new_state: str, current_time: datetime, current_value: float) -> bool:
    """
    判断是否应该发送通知
    发送条件：
    1. 状态从 ok -> alerting (新告警)
    2. 状态从 silenced -> alerting (重新告警)
    3. 状态从 alerting -> ok (恢复通知，可选)
    """
    # 新触发的告警
    if previous_state in ['ok', 'silenced'] and new_state == 'alerting':
        return True
    
    # 告警恢复通知（可配置是否启用）
    if previous_state in ['alerting', 'silenced'] and new_state == 'ok':
        # 这里可以添加配置项控制是否发送恢复通知
        # return rule.send_recovery_notification if hasattr(rule, 'send_recovery_notification') else False
        return False  # 暂时不发送恢复通知
    
    return False

def send_alert_and_record(db: Session, rule: AlertRule, current_value: float, 
                         current_time: datetime, alert_state: str, metric_labels: dict = None):
    """发送告警并记录历史"""
    logger.info(f"规则 {rule.name} 触发告警，当前值: {current_value}, 状态: {alert_state}")
    
    # 获取通知模板
    if not rule.notify_template_id:
        logger.warning(f"规则 {rule.name} 未配置通知模板")
        return
    
    logger.info(f"查找通知模板 ID: {rule.notify_template_id}")
    template = db.query(AlertNotifyTemplate).filter(
        AlertNotifyTemplate.id == rule.notify_template_id
    ).first()
    
    if not template:
        logger.error(f"规则 {rule.name} 的通知模板 {rule.notify_template_id} 不存在")
        return
    
    logger.info(f"找到通知模板: {template.name}, 类型: {template.type}")
    
    # 合并规则标签和指标标签
    rule_labels = rule.labels or {}
    metric_labels = metric_labels or {}
    
    # 指标标签优先级高于规则标签
    merged_labels = {**rule_labels, **metric_labels}
    
    logger.info(f"规则标签: {rule_labels}")
    logger.info(f"指标标签: {metric_labels}")
    logger.info(f"合并后标签: {merged_labels}")
    
    # 构建告警上下文
    alert_context = {
        'rule_name': rule.name,
        'category': rule.category,
        'level': rule.level,
        'condition': rule.condition,
        'current_value': str(current_value),
        'trigger_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'message': f"[{rule.category.upper()}] {rule.name} 触发告警，当前值 {current_value} {rule.condition}",
        'promql': rule.promql,
        'description': rule.description or '',
        'labels': merged_labels,
        'alert_state': alert_state
    }
    
    # 将指标标签作为单独的变量添加到上下文中，方便模板使用
    for key, value in metric_labels.items():
        alert_context[key] = str(value)
    
    logger.info(f"告警上下文: {alert_context}")
    
    # 发送通知
    logger.info(f"开始发送告警通知...")
    send_result = send_alert_notification(template, alert_context)
    logger.info(f"告警发送结果: {send_result}")
    
    # 记录历史
    logger.info(f"开始记录告警历史...")
    create_alert_history(db, rule, alert_context, send_result, current_value)
    logger.info(f"告警历史记录完成")

def update_rule_state(db: Session, rule: AlertRule, new_state: str, alert_time: Optional[datetime]):
    """更新规则状态"""
    try:
        rule.alert_state = new_state
        if alert_time:
            rule.last_alert_time = alert_time
            # 如果发送了告警，增加发送计数
            if new_state == 'alerting':
                rule.send_count = (rule.send_count or 0) + 1
        db.commit()
        logger.debug(f"规则 {rule.name} 状态更新为: {new_state}, 发送次数: {rule.send_count}")
    except Exception as e:
        logger.error(f"更新规则状态失败: {e}")
        db.rollback()

def reset_alert_counters(rule: AlertRule):
    """重置告警计数器"""
    rule.send_count = 0
    rule.alert_start_time = None
    logger.debug(f"规则 {rule.name} 计数器已重置")

def check_and_reset_daily_counters(rule: AlertRule, current_time: datetime):
    """检查并重置每日计数器"""
    if rule.last_alert_time:
        # 如果是新的一天，重置计数器
        last_date = rule.last_alert_time.date()
        current_date = current_time.date()
        if current_date > last_date:
            reset_alert_counters(rule)
            logger.debug(f"规则 {rule.name} 日期切换，计数器已重置")

def parse_time_duration(duration_str: str) -> Optional[timedelta]:
    """
    解析时间间隔字符串
    支持格式: 5m, 1h, 30s, 2d
    """
    if not duration_str:
        return None
    
    duration_str = duration_str.strip().lower()
    try:
        if duration_str.endswith('s'):
            return timedelta(seconds=int(duration_str[:-1]))
        elif duration_str.endswith('m'):
            return timedelta(minutes=int(duration_str[:-1]))
        elif duration_str.endswith('h'):
            return timedelta(hours=int(duration_str[:-1]))
        elif duration_str.endswith('d'):
            return timedelta(days=int(duration_str[:-1]))
        else:
            # 默认当作秒处理
            return timedelta(seconds=int(duration_str))
    except (ValueError, TypeError):
        logger.error(f"无法解析时间间隔: {duration_str}")
        return None

def query_prometheus(promql: str) -> Optional[dict]:
    """查询Prometheus数据，返回包含值和标签的完整结果"""
    try:
        url = f"{PROMETHEUS_URL}/api/v1/query"
        params = {'query': promql}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'success':
            logger.error(f"Prometheus查询失败: {data}")
            return None
        
        result = data['data']['result']
        if not result:
            logger.warning(f"Prometheus查询无结果: {promql}")
            return None
        
        # 返回第一个结果的完整信息
        first_result = result[0]
        return {
            'value': float(first_result['value'][1]),
            'labels': first_result.get('metric', {}),
            'timestamp': first_result['value'][0]
        }
        
    except Exception as e:
        logger.error(f"查询Prometheus异常: {e}")
        return None

def check_alert_condition(value: float, condition: str) -> bool:
    """检查告警条件是否满足"""
    try:
        # 解析条件，如 "> 80", "< 0.5", "== 100", "= 0"
        condition = condition.strip()
        
        if condition.startswith('>='):
            threshold = float(condition[2:].strip())
            return value >= threshold
        elif condition.startswith('<='):
            threshold = float(condition[2:].strip())
            return value <= threshold
        elif condition.startswith('>'):
            threshold = float(condition[1:].strip())
            return value > threshold
        elif condition.startswith('<'):
            threshold = float(condition[1:].strip())
            return value < threshold
        elif condition.startswith('=='):
            threshold = float(condition[2:].strip())
            return value == threshold
        elif condition.startswith('='):
            threshold = float(condition[1:].strip())
            return value == threshold
        elif condition.startswith('!='):
            threshold = float(condition[2:].strip())
            return value != threshold
        else:
            logger.error(f"不支持的条件格式: {condition}")
            return False
            
    except Exception as e:
        logger.error(f"解析条件失败: {condition}, {e}")
        return False

def send_alert_notification(template: AlertNotifyTemplate, alert_context: dict) -> dict:
    """发送告警通知"""
    try:
        logger.info(f"开始发送 {template.type} 类型告警通知")
        logger.info(f"模板参数: {template.params}")
        
        template_params = json.loads(template.params) if isinstance(template.params, str) else template.params
        logger.info(f"解析后的模板参数: {template_params}")
        
        if template.type == 'email':
            logger.info("处理邮件告警通知")
            # 渲染邮件模板
            subject, content = render_email_template(template_params, alert_context)
            logger.info(f"邮件主题: {subject}")
            logger.info(f"邮件内容: {content}")
            
            # 准备邮件参数
            email_params = template_params.copy()
            email_params['subject'] = subject
            email_params['content'] = content
            
            logger.info(f"邮件发送参数: {email_params}")
            result = send_email_msg(email_params)
            logger.info(f"邮件发送结果: {result}")
            return result
            
        elif template.type == 'http':
            logger.info("处理HTTP告警通知")
            # 渲染HTTP模板
            http_params = render_http_template(template_params, alert_context)
            logger.info(f"HTTP发送参数: {http_params}")
            result = send_http_msg(http_params)
            logger.info(f"HTTP发送结果: {result}")
            return result
            
        elif template.type == 'lechat':
            logger.info("处理乐聊告警通知")
            # 渲染乐聊模板
            lechat_params = render_lechat_template(template_params, alert_context)
            logger.info(f"乐聊发送参数: {lechat_params}")
            result = send_lechat_msg(lechat_params)
            logger.info(f"乐聊发送结果: {result}")
            return result
            
        else:
            logger.error(f"不支持的通知类型: {template.type}")
            return {"success": False, "msg": f"不支持的通知类型: {template.type}"}
            
    except Exception as e:
        logger.error(f"发送告警通知失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return {"success": False, "msg": str(e)}

def create_alert_history(db: Session, rule: AlertRule, alert_context: dict, 
                        send_result: dict, current_value: float):
    """创建告警历史记录"""
    try:
        history = AlertHistory(
            rule_id=rule.id,
            rule_name=rule.name,
            category=rule.category,
            level=rule.level,
            status='triggered',
            message=alert_context['message'],
            alert_value=str(current_value),
            condition=rule.condition,
            labels=rule.labels,
            notified=send_result.get('success', False),
            notified_at=datetime.now() if send_result.get('success', False) else None
        )
        
        db.add(history)
        db.commit()
        
        logger.info(f"告警历史记录已创建: rule_id={rule.id}, category={rule.category}, notified={history.notified}")
        
    except Exception as e:
        logger.error(f"创建告警历史失败: {e}")
        db.rollback()

def start_alert_engine():
    """启动告警引擎"""
    try:
        scheduler = _get_scheduler()
        
        # 检查调度器是否已经在运行
        if scheduler.running:
            logger.info("告警引擎已在运行中")
            return
        
        # 添加定时任务
        scheduler.add_job(
            alert_engine_job, 
            "interval", 
            seconds=30, 
            id="alert_engine_job",  # 使用更明确的ID
            replace_existing=True
        )
        
        # 启动调度器
        if not scheduler.running:
            scheduler.start()
            logger.info("告警引擎定时任务已启动，间隔30秒")
        
    except Exception as e:
        logger.error(f"启动告警引擎失败: {e}")
        # 如果启动失败，尝试清理
        try:
            scheduler = _get_scheduler()
            if scheduler and scheduler.running:
                scheduler.shutdown(wait=False)
        except:
            pass

def stop_alert_engine():
    """停止告警引擎"""
    global scheduler
    try:
        if scheduler is None:
            logger.info("告警引擎调度器未初始化")
            return
            
        if scheduler.running:
            # 先移除所有任务，防止新任务被调度
            try:
                scheduler.remove_all_jobs()
                logger.info("已移除所有调度任务")
            except Exception as e:
                logger.warning(f"移除任务时出错: {e}")
            
            # 优雅关闭：等待当前正在执行的任务完成，但不再接受新任务
            scheduler.shutdown(wait=True)
            logger.info("告警引擎已停止")
        else:
            logger.info("告警引擎未在运行")
        
        # 重置全局调度器实例
        scheduler = None
        
    except Exception as e:
        logger.error(f"停止告警引擎失败: {e}")
        # 如果优雅关闭失败，强制关闭
        try:
            if scheduler and hasattr(scheduler, 'shutdown'):
                scheduler.shutdown(wait=False)
                logger.warning("告警引擎已强制停止")
            scheduler = None
        except Exception as force_e:
            logger.error(f"强制停止告警引擎也失败: {force_e}")
            scheduler = None

def get_alert_engine_status() -> dict:
    """获取告警引擎状态"""
    global scheduler
    try:
        if scheduler is None:
            return {
                "running": False,
                "jobs": [],
                "message": "调度器未初始化"
            }
            
        return {
            "running": scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in scheduler.get_jobs()
            ]
        }
    except Exception as e:
        logger.error(f"获取告警引擎状态失败: {e}")
        return {
            "running": False,
            "jobs": [],
            "error": str(e)
        } 