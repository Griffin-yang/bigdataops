-- 告警系统优化升级脚本 v2.0
-- 添加增强的抑制规则和确认功能

-- 为告警规则表添加新字段
ALTER TABLE alert_rule ADD COLUMN IF NOT EXISTS duration INTEGER DEFAULT 3600 COMMENT '告警持续时间(秒)，超过时间停止发送';
ALTER TABLE alert_rule ADD COLUMN IF NOT EXISTS max_send_count INTEGER DEFAULT NULL COMMENT '最大发送次数，达到次数后停止发送';
ALTER TABLE alert_rule ADD COLUMN IF NOT EXISTS send_count INTEGER DEFAULT 0 COMMENT '当前已发送次数';
ALTER TABLE alert_rule ADD COLUMN IF NOT EXISTS alert_start_time DATETIME DEFAULT NULL COMMENT '告警开始时间';

-- 为告警历史表添加确认相关字段
ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS acknowledged BOOLEAN DEFAULT FALSE COMMENT '是否已确认';
ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS acknowledged_at DATETIME DEFAULT NULL COMMENT '确认时间';
ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS acknowledged_by VARCHAR(128) DEFAULT NULL COMMENT '确认人';

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_alert_rule_alert_state ON alert_rule(alert_state);
CREATE INDEX IF NOT EXISTS idx_alert_rule_alert_start_time ON alert_rule(alert_start_time);
CREATE INDEX IF NOT EXISTS idx_alert_history_acknowledged ON alert_history(acknowledged);
CREATE INDEX IF NOT EXISTS idx_alert_history_rule_id_acknowledged ON alert_history(rule_id, acknowledged);

-- 更新现有数据的默认值
UPDATE alert_rule SET duration = 3600 WHERE duration IS NULL;
UPDATE alert_rule SET send_count = 0 WHERE send_count IS NULL;
UPDATE alert_history SET acknowledged = FALSE WHERE acknowledged IS NULL;

-- 验证更新结果
SELECT 
    'alert_rule' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN duration IS NOT NULL THEN 1 END) as duration_set,
    COUNT(CASE WHEN send_count IS NOT NULL THEN 1 END) as send_count_set
FROM alert_rule
UNION ALL
SELECT 
    'alert_history' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN acknowledged IS NOT NULL THEN 1 END) as acknowledged_set,
    0 as send_count_set
FROM alert_history;

-- 显示表结构
SHOW CREATE TABLE alert_rule;
SHOW CREATE TABLE alert_history;
