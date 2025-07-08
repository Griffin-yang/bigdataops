-- 告警系统升级SQL脚本
-- 添加分组功能、防重发机制、详细历史记录

-- 1. 升级AlertRule表
ALTER TABLE alert_rule 
ADD COLUMN category VARCHAR(64) DEFAULT 'other' COMMENT '组件分组(hdfs/hive/spark/mysql/other)' AFTER name,
ADD COLUMN description TEXT DEFAULT NULL COMMENT '规则描述' AFTER level,
ADD COLUMN labels JSON DEFAULT NULL COMMENT '规则标签(JSON格式)' AFTER description,
ADD COLUMN alert_state VARCHAR(32) DEFAULT 'ok' COMMENT '当前告警状态(ok/alerting/silenced)' AFTER enabled,
ADD COLUMN last_alert_time DATETIME DEFAULT NULL COMMENT '最后一次告警时间' AFTER alert_state;

-- 2. 升级AlertNotifyTemplate表
ALTER TABLE alert_notify_template 
ADD COLUMN description TEXT DEFAULT NULL COMMENT '模板描述' AFTER params;

-- 3. 升级AlertHistory表
ALTER TABLE alert_history 
ADD COLUMN rule_name VARCHAR(128) NOT NULL COMMENT '规则名称(冗余存储)' AFTER rule_id,
ADD COLUMN category VARCHAR(64) NOT NULL DEFAULT 'other' COMMENT '组件分组(冗余存储)' AFTER rule_name,
ADD COLUMN level VARCHAR(32) NOT NULL DEFAULT 'medium' COMMENT '告警等级(冗余存储)' AFTER category,
ADD COLUMN alert_value VARCHAR(64) DEFAULT NULL COMMENT '触发时的监控值' AFTER message,
ADD COLUMN condition VARCHAR(64) DEFAULT NULL COMMENT '触发条件(冗余存储)' AFTER alert_value,
ADD COLUMN labels JSON DEFAULT NULL COMMENT '告警标签(JSON格式)' AFTER condition,
ADD COLUMN resolved_at DATETIME DEFAULT NULL COMMENT '恢复时间' AFTER notified_at;

-- 4. 创建索引优化查询性能
CREATE INDEX idx_alert_rule_category ON alert_rule(category);
CREATE INDEX idx_alert_rule_alert_state ON alert_rule(alert_state);
CREATE INDEX idx_alert_rule_last_alert_time ON alert_rule(last_alert_time);

CREATE INDEX idx_alert_history_category ON alert_history(category);
CREATE INDEX idx_alert_history_level ON alert_history(level);
CREATE INDEX idx_alert_history_created_at ON alert_history(created_at);
CREATE INDEX idx_alert_history_rule_category ON alert_history(rule_id, category);

-- 5. 预设组件分组数据（可选）
UPDATE alert_rule SET category = 'hdfs' WHERE name LIKE '%hdfs%' OR name LIKE '%HDFS%';
UPDATE alert_rule SET category = 'hive' WHERE name LIKE '%hive%' OR name LIKE '%Hive%';
UPDATE alert_rule SET category = 'spark' WHERE name LIKE '%spark%' OR name LIKE '%Spark%';
UPDATE alert_rule SET category = 'mysql' WHERE name LIKE '%mysql%' OR name LIKE '%MySQL%';
UPDATE alert_rule SET category = 'kubernetes' WHERE name LIKE '%k8s%' OR name LIKE '%kubernetes%';
UPDATE alert_rule SET category = 'system' WHERE name LIKE '%cpu%' OR name LIKE '%memory%' OR name LIKE '%disk%';

-- 6. 同步历史数据中的冗余字段
UPDATE alert_history ah 
INNER JOIN alert_rule ar ON ah.rule_id = ar.id 
SET ah.rule_name = ar.name, 
    ah.category = ar.category, 
    ah.level = ar.level
WHERE ah.rule_name IS NULL OR ah.rule_name = '';

COMMIT; 