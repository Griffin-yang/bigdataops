-- ======================================================
-- 大数据运维管理平台 - 数据库建表语句 v2.0
-- 包含增强告警抑制规则和确认功能
-- ======================================================

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS `alert_history`;
DROP TABLE IF EXISTS `alert_rule`;
DROP TABLE IF EXISTS `alert_notify_template`;

-- ======================================================
-- 告警通知模板表（必须先创建，因为被alert_rule引用）
-- ======================================================
CREATE TABLE `alert_notify_template` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `name` VARCHAR(128) NOT NULL COMMENT '模板名称',
  `type` VARCHAR(32) NOT NULL COMMENT '模板类型(email/http/lechat)',
  `params` TEXT NOT NULL COMMENT '模板参数配置(JSON格式)',
  `description` TEXT DEFAULT NULL COMMENT '模板描述',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_type` (`type`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警通知模板表';

-- ======================================================
-- 告警规则表（增强版）
-- ======================================================
CREATE TABLE `alert_rule` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `name` VARCHAR(128) NOT NULL COMMENT '规则名称',
  `category` VARCHAR(64) DEFAULT 'other' COMMENT '组件分组(hdfs/hive/spark/mysql/kafka/zookeeper/yarn/hbase/elasticsearch/prometheus/grafana/other)',
  `promql` TEXT NOT NULL COMMENT 'PromQL查询表达式',
  `condition` VARCHAR(64) NOT NULL COMMENT '触发条件(如: > 80, < 0.5)',
  `for_duration` INT DEFAULT 60 COMMENT '触发持续时间(秒)，条件需持续满足多长时间才触发告警',
  `level` VARCHAR(32) NOT NULL DEFAULT 'medium' COMMENT '告警等级(low/medium/high/critical)',
  `description` TEXT DEFAULT NULL COMMENT '规则描述',
  `labels` JSON DEFAULT NULL COMMENT '规则标签(JSON格式，用于分组和过滤)',
  
  -- 抑制控制字段
  `suppress` VARCHAR(128) DEFAULT NULL COMMENT '抑制条件(如: 5m, 1h)',
  `repeat` INT DEFAULT 0 COMMENT '再通知间隔(秒，0表示不重复)',
  `duration` INT DEFAULT 3600 COMMENT '告警持续时间(秒)，超过时间停止发送，默认1小时',
  `max_send_count` INT DEFAULT NULL COMMENT '最大发送次数，达到次数后停止发送',
  
  -- 状态跟踪字段
  `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用(0=禁用, 1=启用)',
  `alert_state` VARCHAR(32) DEFAULT 'ok' COMMENT '当前告警状态(ok/alerting/silenced)',
  `last_alert_time` DATETIME DEFAULT NULL COMMENT '最后一次告警时间',
  `send_count` INT DEFAULT 0 COMMENT '当前已发送次数',
  `alert_start_time` DATETIME DEFAULT NULL COMMENT '告警开始时间',
  
  -- 关联字段
  `notify_template_id` INT DEFAULT NULL COMMENT '通知模板ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (`notify_template_id`) REFERENCES `alert_notify_template`(`id`) ON DELETE SET NULL,
  
  -- 索引
  INDEX `idx_category` (`category`),
  INDEX `idx_level` (`level`),
  INDEX `idx_enabled` (`enabled`),
  INDEX `idx_alert_state` (`alert_state`),
  INDEX `idx_last_alert_time` (`last_alert_time`),
  INDEX `idx_alert_start_time` (`alert_start_time`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_category_level` (`category`, `level`),
  INDEX `idx_enabled_state` (`enabled`, `alert_state`),
  INDEX `idx_send_count` (`send_count`),
  INDEX `idx_duration` (`duration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则表(增强版)';

-- ======================================================
-- 告警历史表（增强版）
-- ======================================================
CREATE TABLE `alert_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `rule_id` INT NOT NULL COMMENT '关联的规则ID',
  `rule_name` VARCHAR(128) NOT NULL COMMENT '规则名称(冗余存储，便于查询)',
  `category` VARCHAR(64) NOT NULL DEFAULT 'other' COMMENT '组件分组(冗余存储)',
  `level` VARCHAR(32) NOT NULL DEFAULT 'medium' COMMENT '告警等级(冗余存储)',
  `status` VARCHAR(32) NOT NULL COMMENT '告警状态(firing/resolved)',
  `message` TEXT NOT NULL COMMENT '告警消息内容',
  `alert_value` VARCHAR(64) DEFAULT NULL COMMENT '触发时的监控值',
  `condition` VARCHAR(64) DEFAULT NULL COMMENT '触发条件(冗余存储)',
  `labels` JSON DEFAULT NULL COMMENT '告警标签(JSON格式)',
  
  -- 通知状态字段
  `notified` TINYINT(1) DEFAULT 0 COMMENT '是否已通知(0=未通知, 1=已通知)',
  `notified_at` DATETIME DEFAULT NULL COMMENT '通知时间',
  
  -- 确认功能字段
  `acknowledged` TINYINT(1) DEFAULT 0 COMMENT '是否已确认(0=未确认, 1=已确认)',
  `acknowledged_at` DATETIME DEFAULT NULL COMMENT '确认时间',
  `acknowledged_by` VARCHAR(128) DEFAULT NULL COMMENT '确认人',
  
  -- 时间字段
  `resolved_at` DATETIME DEFAULT NULL COMMENT '解决时间',
  `fired_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '告警触发时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
  
  -- 外键约束
  FOREIGN KEY (`rule_id`) REFERENCES `alert_rule`(`id`) ON DELETE CASCADE,
  
  -- 索引
  INDEX `idx_rule_id` (`rule_id`),
  INDEX `idx_category` (`category`),
  INDEX `idx_level` (`level`),
  INDEX `idx_status` (`status`),
  INDEX `idx_fired_at` (`fired_at`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_resolved_at` (`resolved_at`),
  INDEX `idx_notified` (`notified`),
  INDEX `idx_acknowledged` (`acknowledged`),
  INDEX `idx_acknowledged_at` (`acknowledged_at`),
  INDEX `idx_rule_category` (`rule_id`, `category`),
  INDEX `idx_category_level` (`category`, `level`),
  INDEX `idx_status_fired` (`status`, `fired_at`),
  INDEX `idx_level_fired` (`level`, `fired_at`),
  INDEX `idx_rule_acknowledged` (`rule_id`, `acknowledged`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警历史记录表(增强版)';

-- ======================================================
-- 插入示例数据
-- ======================================================

-- 插入通知模板示例
INSERT INTO `alert_notify_template` (`name`, `type`, `params`, `description`) VALUES 
('默认邮件模板', 'email', '{"smtp_host": "smtp.example.com", "smtp_port": 587, "from": "alert@example.com", "to": ["admin@example.com"], "user": "alert@example.com", "password": "password", "ssl": true, "subject_template": "【{level}】{rule_name} 告警通知", "content_template": "<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p><p>时间: {trigger_time}</p>"}', '默认的邮件通知模板'),

('默认HTTP模板', 'http', '{"url": "http://localhost:8080/webhook", "method": "POST", "timeout": 10, "verify_ssl": false, "headers": {"Content-Type": "application/json"}, "body_template": {"rule": "{rule_name}", "level": "{level}", "value": "{current_value}", "message": "{message}", "timestamp": "{trigger_time}"}}', '默认的HTTP Webhook通知模板'),

('乐聊群组模板', 'lechat', '{"mode": "group", "url": "http://your-host/api/message/sendTeam", "fromId": "lyj-dw", "groupId": "group-123456", "ext": {"group": "oa"}, "body_template": {"robot": {"type": "robotAnswer"}, "type": "multi", "msgs": [{"text": "🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}", "type": "text"}]}, "option": {"push": true}}', '乐聊群组通知模板'),

('乐聊个人模板', 'lechat', '{"mode": "personal", "url": "http://your-host/api/message/sendPersonal", "fromId": "lyj-dw", "userIds": "user1,user2", "ext": {"group": "oa"}, "body_template": {"robot": {"type": "robotAnswer"}, "type": "multi", "msgs": [{"text": "🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}", "type": "text"}]}, "userMapping": {"emp001": "user1", "emp002": "user2"}, "option": {"push": true}}', '乐聊个人通知模板');

-- 插入告警规则示例（包含增强抑制功能）
INSERT INTO `alert_rule` (`name`, `category`, `promql`, `condition`, `for_duration`, `level`, `description`, `suppress`, `repeat`, `duration`, `max_send_count`, `enabled`, `notify_template_id`) VALUES 

('HDFS存储使用率告警', 'hdfs', 'hdfs_capacity_used_percent', '> 85', 300, 'high', 'HDFS存储空间使用率超过85%时触发告警', '15m', 3600, 7200, 5, 1, 1),

('MySQL连接数告警', 'mysql', 'mysql_global_status_threads_connected', '> 80', 120, 'medium', 'MySQL连接数超过80时触发告警', '10m', 1800, 3600, 3, 1, 2),

('系统CPU使用率告警', 'system', '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)', '> 90', 60, 'critical', '系统CPU使用率超过90%时触发告警', '5m', 600, 1800, 10, 1, 3),

('Redis内存使用率告警', 'redis', 'redis_memory_used_percent', '> 85', 180, 'high', 'Redis内存使用率超过85%时触发告警', '10m', 1200, 3600, 4, 1, 4),

('Kafka消费延迟告警', 'kafka', 'kafka_consumer_lag_sum', '> 10000', 240, 'medium', 'Kafka消费延迟超过10000条消息时触发告警', '20m', 2400, 7200, 3, 1, 1);

-- 插入告警历史示例（包含确认状态）
INSERT INTO `alert_history` (`rule_id`, `rule_name`, `category`, `level`, `status`, `message`, `alert_value`, `condition`, `notified`, `acknowledged`, `acknowledged_by`) VALUES 

(1, 'HDFS存储使用率告警', 'hdfs', 'high', 'resolved', 'HDFS存储使用率达到87%，已超过阈值85%', '87', '> 85', 1, 1, 'admin'),

(2, 'MySQL连接数告警', 'mysql', 'medium', 'firing', 'MySQL当前连接数为85，超过阈值80', '85', '> 80', 1, 0, NULL),

(3, '系统CPU使用率告警', 'system', 'critical', 'resolved', '系统CPU使用率达到95%，已超过阈值90%', '95', '> 90', 1, 1, 'operator'),

(4, 'Redis内存使用率告警', 'redis', 'high', 'firing', 'Redis内存使用率达到88%，超过阈值85%', '88', '> 85', 1, 0, NULL);

-- ======================================================
-- 验证表结构
-- ======================================================
SHOW TABLES;
DESCRIBE alert_notify_template;
DESCRIBE alert_rule;
DESCRIBE alert_history;
