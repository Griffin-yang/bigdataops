from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from app.models.db import Base

class AlertNotifyTemplate(Base):
    __tablename__ = 'alert_notify_template'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    name = Column(String(128), nullable=False, comment='模板名称')
    type = Column(String(32), nullable=False, comment='下游类型(email/http)')
    params = Column(Text, nullable=False, comment='下游参数(JSON)')
    description = Column(Text, default=None, comment='模板描述')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

class AlertRule(Base):
    __tablename__ = 'alert_rule'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    name = Column(String(128), nullable=False, comment='规则名称')
    category = Column(String(64), default='other', comment='组件分组(hdfs/hive/spark/mysql/other)')
    promql = Column(Text, nullable=False, comment='PromQL表达式')
    condition = Column(String(64), nullable=False, comment='触发条件，如 > 80')
    for_duration = Column(Integer, default=60, comment='触发持续时间(秒)，条件需持续满足多长时间才触发告警')
    level = Column(String(32), nullable=False, comment='告警等级，如critical/warning')
    description = Column(Text, default=None, comment='规则描述')
    labels = Column(JSON, default=None, comment='规则标签(JSON格式)')
    suppress = Column(String(128), default=None, comment='抑制条件')
    repeat = Column(Integer, default=0, comment='再通知间隔(秒)')
    duration = Column(Integer, default=3600, comment='告警持续时间(秒)，超过时间停止发送')
    max_send_count = Column(Integer, default=None, comment='最大发送次数，达到次数后停止发送')
    send_count = Column(Integer, default=0, comment='当前已发送次数')
    alert_start_time = Column(DateTime, default=None, comment='告警开始时间')
    enabled = Column(Boolean, default=True, comment='是否启用')
    alert_state = Column(String(32), default='ok', comment='当前告警状态(ok/alerting/silenced)')
    last_alert_time = Column(DateTime, default=None, comment='最后一次告警时间')
    notify_template_id = Column(Integer, ForeignKey('alert_notify_template.id'), nullable=True, comment='通知模板ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

class AlertHistory(Base):
    __tablename__ = 'alert_history'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    rule_id = Column(Integer, ForeignKey('alert_rule.id', ondelete='CASCADE'), nullable=False, comment='规则ID')
    rule_name = Column(String(128), nullable=False, comment='规则名称(冗余存储)')
    category = Column(String(64), nullable=False, comment='组件分组(冗余存储)')
    level = Column(String(32), nullable=False, comment='告警等级(冗余存储)')
    status = Column(String(32), nullable=False, comment='状态(triggered/recovered)')
    message = Column(Text, nullable=False, comment='告警内容')
    alert_value = Column(String(64), default=None, comment='触发时的监控值')
    condition = Column(String(64), default=None, comment='触发条件(冗余存储)')
    labels = Column(JSON, default=None, comment='告警标签(JSON格式)')
    notified = Column(Boolean, default=False, comment='是否已通知')
    notified_at = Column(DateTime, default=None, comment='通知时间')
    resolved_at = Column(DateTime, default=None, comment='恢复时间')
    acknowledged = Column(Boolean, default=False, comment='是否已确认')
    acknowledged_at = Column(DateTime, default=None, comment='确认时间')
    acknowledged_by = Column(String(128), default=None, comment='确认人')
    created_at = Column(DateTime, server_default=func.now(), comment='记录时间') 