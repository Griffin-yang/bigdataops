-- 告警通知模板表
CREATE TABLE IF NOT EXISTS `alert_notify_template` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `name` VARCHAR(128) NOT NULL COMMENT '模板名称',
  `type` VARCHAR(32) NOT NULL COMMENT '模板类型(email/http)',
  `params` TEXT NOT NULL COMMENT '模板参数配置(JSON格式)',
  `description` TEXT DEFAULT NULL COMMENT '模板描述',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_type` (`type`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警通知模板表'; 