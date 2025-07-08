-- 告警规则表
CREATE TABLE IF NOT EXISTS `alert_rule` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `name` VARCHAR(128) NOT NULL COMMENT '规则名称',
  `category` VARCHAR(64) DEFAULT 'other' COMMENT '组件分组(hdfs/hive/spark/mysql/kafka/zookeeper/yarn/hbase/elasticsearch/prometheus/grafana/other)',
  `promql` TEXT NOT NULL COMMENT 'PromQL查询表达式',
  `condition` VARCHAR(64) NOT NULL COMMENT '触发条件(如: > 80, < 0.5)',
  `level` VARCHAR(32) NOT NULL DEFAULT 'medium' COMMENT '告警等级(low/medium/high/critical)',
  `description` TEXT DEFAULT NULL COMMENT '规则描述',
  `labels` JSON DEFAULT NULL COMMENT '规则标签(JSON格式，用于分组和过滤)',
  `suppress` VARCHAR(128) DEFAULT NULL COMMENT '抑制条件(如: 5m, 1h)',
  `repeat` INT DEFAULT 0 COMMENT '再通知间隔(秒，0表示不重复)',
  `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用(0=禁用, 1=启用)',
  `alert_state` VARCHAR(32) DEFAULT 'ok' COMMENT '当前告警状态(ok/alerting/silenced)',
  `last_alert_time` DATETIME DEFAULT NULL COMMENT '最后一次告警时间',
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
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_category_level` (`category`, `level`),
  INDEX `idx_enabled_state` (`enabled`, `alert_state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则表'; 