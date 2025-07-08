-- 告警历史表
CREATE TABLE IF NOT EXISTS `alert_history` (
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
  `notified` TINYINT(1) DEFAULT 0 COMMENT '是否已通知(0=未通知, 1=已通知)',
  `notified_at` DATETIME DEFAULT NULL COMMENT '通知时间',
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
  INDEX `idx_rule_category` (`rule_id`, `category`),
  INDEX `idx_category_level` (`category`, `level`),
  INDEX `idx_status_fired` (`status`, `fired_at`),
  INDEX `idx_level_fired` (`level`, `fired_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警历史记录表'; 