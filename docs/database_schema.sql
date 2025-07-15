-- ======================================================
-- BigDataOps 大数据运维管理平台 - 数据库建表语句
-- 版本: v2.0
-- 包含: 告警系统、用户管理、集群监控、业务监控等完整功能
-- ======================================================

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS `alert_history`;
DROP TABLE IF EXISTS `alert_rule`;
DROP TABLE IF EXISTS `alert_notify_template`;
-- ======================================================
-- 告警通知模板表
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
  `condition` VARCHAR(64) NOT NULL COMMENT '触发条件(如: > 80, < 0.5, = 0)',
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
  `status` VARCHAR(32) NOT NULL COMMENT '告警状态(triggered/recovered)',
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
-- 用户管理表（预留）
-- ======================================================
CREATE TABLE `user_management` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `username` VARCHAR(64) NOT NULL UNIQUE COMMENT '用户名',
  `email` VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
  `role` VARCHAR(32) DEFAULT 'user' COMMENT '用户角色(admin/user)',
  `status` TINYINT(1) DEFAULT 1 COMMENT '用户状态(0=禁用, 1=启用)',
  `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_username` (`username`),
  INDEX `idx_role` (`role`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户管理表';

-- ======================================================
-- 系统配置表（预留）
-- ======================================================
CREATE TABLE `system_config` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `config_key` VARCHAR(128) NOT NULL UNIQUE COMMENT '配置键',
  `config_value` TEXT NOT NULL COMMENT '配置值',
  `description` TEXT DEFAULT NULL COMMENT '配置描述',
  `category` VARCHAR(64) DEFAULT 'system' COMMENT '配置分类',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_config_key` (`config_key`),
  INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- ======================================================
-- 操作日志表（预留）
-- ======================================================
CREATE TABLE `operation_log` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `user_id` INT DEFAULT NULL COMMENT '操作用户ID',
  `username` VARCHAR(64) DEFAULT NULL COMMENT '操作用户名',
  `operation` VARCHAR(128) NOT NULL COMMENT '操作类型',
  `resource` VARCHAR(128) DEFAULT NULL COMMENT '操作资源',
  `resource_id` INT DEFAULT NULL COMMENT '资源ID',
  `details` JSON DEFAULT NULL COMMENT '操作详情',
  `ip_address` VARCHAR(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` TEXT DEFAULT NULL COMMENT '用户代理',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  
  -- 索引
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_operation` (`operation`),
  INDEX `idx_resource` (`resource`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- ======================================================
-- 验证表结构
-- ======================================================
SHOW TABLES; 