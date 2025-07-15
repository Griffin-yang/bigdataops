# BigDataOps API 参考文档

## 📋 目录
- [概述](#概述)
- [通用规范](#通用规范)
- [认证与授权](#认证与授权)
- [告警系统API](#告警系统api)
- [集群监控API](#集群监控api)
- [业务监控API](#业务监控api)
- [用户管理API](#用户管理api)
- [错误码说明](#错误码说明)

## 🎯 概述

BigDataOps API 提供完整的RESTful接口，支持告警系统、集群监控、业务监控和用户管理等核心功能。

### 基础信息
- **基础URL**: `http://localhost:8000/api`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 版本信息
- **当前版本**: v2.0
- **兼容性**: 向后兼容v1.0

## 📋 通用规范

### 请求格式
所有请求使用JSON格式，Content-Type设置为`application/json`。

### 响应格式
所有API响应遵循统一格式：

```json
{
  "code": 0,           // 0表示成功，其他表示错误
  "data": {},          // 返回的数据，成功时有值，失败时为null
  "msg": "操作成功"     // 响应消息
}
```

### 分页参数
支持分页的接口使用以下参数：
- `page`: 页码（默认1）
- `size`: 每页数量（默认20，最大100）

### 时间格式
- 日期时间使用ISO 8601格式：`YYYY-MM-DDTHH:mm:ssZ`
- 日期使用格式：`YYYY-MM-DD`

## 🔐 认证与授权

### 认证方式
目前支持以下认证方式：
- **Session认证**: 基于Cookie的会话认证
- **Token认证**: 基于JWT的令牌认证（计划中）

### 权限控制
- **用户权限**: 基于用户角色的权限控制
- **资源权限**: 基于资源的访问控制
- **操作权限**: 基于操作的权限验证

---

## 🚨 告警系统API

### 告警规则管理

#### 查询规则列表
```http
GET /alert/rule
```

**查询参数**:
- `page`: 页码（默认1）
- `size`: 每页数量（默认20，最大100）
- `category`: 组件分组筛选（可选）
- `level`: 告警等级筛选（可选）
- `enabled`: 启用状态筛选（可选）
- `alert_state`: 告警状态筛选（可选）
- `name`: 规则名称搜索（可选）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "HDFS DataNode 存储使用率告警",
        "category": "hdfs",
        "promql": "hdfs_datanode_capacity_used_percent",
        "condition": "> 80",
        "level": "critical",
        "description": "DataNode存储使用率过高",
        "labels": "cluster=prod,team=bigdata",
        "suppress": "5m",
        "repeat": 1800,
        "enabled": true,
        "alert_state": "ok",
        "last_alert_time": "2024-12-19T10:30:00Z",
        "notify_template_id": 1,
        "created_at": "2024-06-01T12:00:00Z",
        "updated_at": "2024-06-01T12:00:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "msg": "查询成功"
}
```

#### 获取规则分组列表
```http
GET /alert/rule/categories
```

**响应示例**:
```json
{
  "code": 0,
  "data": ["hdfs", "hive", "spark", "mysql", "kafka", "zookeeper"],
  "msg": "查询成功"
}
```

#### 获取规则统计信息
```http
GET /alert/rule/stats
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "total_rules": 100,
    "enabled_rules": 85,
    "alerting_rules": 5,
    "category_stats": [
      {
        "category": "hdfs",
        "total_count": 20,
        "enabled_count": 18,
        "alerting_count": 2
      }
    ],
    "level_stats": [
      {
        "level": "critical",
        "count": 15
      }
    ]
  },
  "msg": "查询成功"
}
```

#### 查询单条规则
```http
GET /alert/rule/{rule_id}
```

#### 新建规则
```http
POST /alert/rule
```

**请求体**:
```json
{
  "name": "HDFS DataNode 存储使用率告警",
  "category": "hdfs",
  "promql": "hdfs_datanode_capacity_used_percent",
  "condition": "> 80",
  "level": "critical",
  "description": "DataNode存储使用率过高",
  "labels": "cluster=prod,team=bigdata",
  "suppress": "5m",
  "repeat": 1800,
  "enabled": true,
  "notify_template_id": 1
}
```

#### 更新规则
```http
PUT /alert/rule/{rule_id}
```

#### 删除规则
```http
DELETE /alert/rule/{rule_id}
```

#### 批量更新规则分组
```http
POST /alert/rule/batch_update_category
```

**请求体**:
```json
{
  "rule_ids": [1, 2, 3],
  "category": "hdfs"
}
```

### 告警历史管理

#### 查询告警历史列表
```http
GET /alert/history
```

**查询参数**:
- `page`: 页码（默认1）
- `size`: 每页数量（默认20，最大100）
- `category`: 组件分组筛选（可选）
- `level`: 告警等级筛选（可选）
- `status`: 告警状态筛选（可选：firing, resolved）
- `rule_name`: 规则名称搜索（可选）
- `start_time`: 开始时间（可选，ISO格式）
- `end_time`: 结束时间（可选，ISO格式）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "rule_id": 1,
        "rule_name": "HDFS DataNode 存储使用率告警",
        "category": "hdfs",
        "level": "critical",
        "alert_value": "85.5",
        "condition": "> 80",
        "labels": "cluster=prod,team=bigdata",
        "status": "firing",
        "fired_at": "2024-12-19T10:30:00Z",
        "resolved_at": null,
        "created_at": "2024-12-19T10:30:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "size": 20,
    "pages": 8
  },
  "msg": "查询成功"
}
```

#### 获取告警历史统计
```http
GET /alert/history/stats
```

**查询参数**:
- `days`: 统计天数（默认7天）
- `category`: 组件分组筛选（可选）

#### 手动解决告警
```http
POST /alert/history/{history_id}/resolve
```

**请求体**:
```json
{
  "reason": "手动处理完成"
}
```

#### 确认告警
```http
POST /alert/history/{history_id}/acknowledge
```

**查询参数**:
- `acknowledged_by`: 确认人（必填）

#### 删除告警历史记录
```http
DELETE /alert/history/{history_id}
```

#### 批量删除告警历史
```http
POST /alert/history/batch_delete
```

**请求体**:
```json
{
  "history_ids": [1, 2, 3, 4, 5]
}
```

### 告警通知模板管理

#### 查询所有模板
```http
GET /alert/notify_template
```

**查询参数**:
- `type`（可选）：模板类型过滤（email/http/lechat）

**响应示例**:
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "邮件通知模板",
      "type": "email",
      "params": {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "from": "alert@example.com",
        "to": ["admin@example.com"],
        "user": "alert@example.com",
        "password": "password",
        "ssl": true,
        "subject_template": "【{level}】{rule_name} 告警通知",
        "content_template": "<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p>"
      },
      "created_at": "2024-06-01T12:00:00Z",
      "updated_at": "2024-06-01T12:00:00Z"
    }
  ],
  "msg": "查询成功"
}
```

#### 获取单个模板
```http
GET /alert/notify_template/{template_id}
```

#### 新建模板
```http
POST /alert/notify_template
```

**请求体示例（邮件模板）**:
```json
{
  "name": "邮件通知模板",
  "type": "email",
  "params": {
    "smtp_host": "smtp.163.com",
    "smtp_port": 465,
    "from": "sender@163.com",
    "to": ["receiver1@qq.com", "receiver2@qq.com"],
    "user": "sender@163.com",
    "password": "smtp_password",
    "ssl": true,
    "subject_template": "【{level}】{rule_name} 告警通知",
    "content_template": "<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p>"
  }
}
```

**请求体示例（HTTP模板）**:
```json
{
  "name": "HTTP通知模板",
  "type": "http",
  "params": {
    "url": "https://api.example.com/webhook",
    "method": "POST",
    "headers": {"Content-Type": "application/json", "Authorization": "Bearer token"},
    "body_template": {
      "alert": {
        "rule": "{rule_name}",
        "level": "{level}",
        "value": "{current_value}",
        "time": "{trigger_time}"
      }
    },
    "timeout": 10,
    "verify_ssl": true
  }
}
```

**请求体示例（乐聊群组模板）**:
```json
{
  "name": "乐聊群组告警模板",
  "type": "lechat",
  "params": {
    "mode": "group",
    "url": "http://your-host/api/message/sendTeam",
    "fromId": "lyj-dw",
    "groupId": "group-123456",
    "ext": {"group": "oa"},
    "body_template": {
      "robot": {"type": "robotAnswer"},
      "type": "multi",
      "msgs": [{
        "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n触发时间: {trigger_time}\n描述: {description}",
        "type": "text"
      }]
    },
    "pushcontent": "告警提醒",
    "option": {"push": true}
  }
}
```

#### 更新模板
```http
PUT /alert/notify_template/{template_id}
```

#### 删除模板
```http
DELETE /alert/notify_template/{template_id}
```

### 告警引擎控制

#### 启动告警引擎
```http
POST /alert/engine/start
```

#### 停止告警引擎
```http
POST /alert/engine/stop
```

#### 获取引擎状态
```http
GET /alert/engine/status
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "status": "running",
    "last_check": "2024-12-19T10:30:00Z",
    "rules_count": 50,
    "active_alerts": 3
  },
  "msg": "查询成功"
}
```

#### 测试规则
```http
POST /alert/engine/test
```

**请求体**:
```json
{
  "promql": "up == 0",
  "labels": "instance=localhost:9090"
}
```

---

## 📊 集群监控API

### 集群概览

#### 获取集群健康状态
```http
GET /cluster/health
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "status": "healthy",
    "message": "集群运行正常",
    "details": {
      "total_nodes": 5,
      "healthy_nodes": 4,
      "unhealthy_nodes": 1,
      "avg_cpu_usage": 65.2,
      "avg_memory_usage": 72.8
    }
  },
  "msg": "查询成功"
}
```

#### 获取集群总览信息
```http
GET /cluster/overview
```

**查询参数**:
- `service`: 服务筛选（可选，如："大数据"）
- `job`: 任务筛选（可选，如："consul-node"）
- `role`: 角色筛选（可选，如："bigdata-storage"）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "total_nodes": 10,
    "healthy_nodes": 8,
    "unhealthy_nodes": 2,
    "avg_cpu_usage": 65.5,
    "avg_memory_usage": 72.3,
    "avg_disk_usage": 45.8,
    "services_status": {
      "HDFS": {"healthy": 8, "total": 10},
      "YARN": {"healthy": 6, "total": 8}
    },
    "service_distribution": {
      "大数据": {"total": 10, "healthy": 8}
    },
    "filter_applied": {
      "service": "大数据",
      "job": null,
      "role": null
    },
    "update_time": "2024-12-19T10:30:00Z"
  },
  "msg": "查询成功"
}
```

#### 获取集群节点列表
```http
GET /cluster/nodes
```

**查询参数**:
- `status`: 节点状态筛选（可选：healthy/unhealthy）
- `service`: 服务筛选（可选，如："大数据"）
- `job`: 任务筛选（可选，如："consul-node"）
- `role`: 角色筛选（可选，如："bigdata-storage"）
- `page`: 页码（默认1）
- `size`: 每页数量（默认20，最大100）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "instance": "192.168.132.2:9100",
        "hostname": "bigdata-storage-node1.leyoujia.com",
        "job": "consul-node",
        "service": "大数据",
        "role": "bigdata-storage",
        "location": "深圳亚森3F-305",
        "rack": "01-09",
        "env": "pro",
        "status": "up",
        "cpu_usage": 68.5,
        "memory_usage": 75.2,
        "disk_usage": 45.8,
        "network_bytes_recv": 1024000,
        "network_bytes_sent": 2048000,
        "load_1m": 1.25,
        "uptime": 86400,
        "uptime_formatted": "1天0小时",
        "last_seen": "2024-12-19T10:30:00Z",
        "roles": ["DataNode", "NodeManager"]
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10,
    "pages": 1
  },
  "msg": "查询成功"
}
```

### 组件监控

#### 获取组件概览
```http
GET /cluster/components
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "components": [
      {
        "name": "HDFS",
        "status": "healthy",
        "total_instances": 12,
        "healthy_instances": 11,
        "unhealthy_instances": 1,
        "key_metrics": {
          "capacity_used_percent": 65.2,
          "blocks_total": 1500000,
          "blocks_corrupt": 0
        }
      },
      {
        "name": "YARN",
        "status": "healthy",
        "total_instances": 8,
        "healthy_instances": 8,
        "unhealthy_instances": 0,
        "key_metrics": {
          "apps_running": 25,
          "apps_pending": 3,
          "memory_available_mb": 819200
        }
      }
    ]
  },
  "msg": "查询成功"
}
```

#### 获取组件详细信息
```http
GET /cluster/components/{component_name}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "name": "HDFS",
    "status": "healthy",
    "version": "3.3.4",
    "instances": [
      {
        "type": "NameNode",
        "hostname": "bigdata-master-001",
        "status": "active",
        "metrics": {
          "capacity_total_gb": 5120,
          "capacity_used_gb": 3340,
          "files_total": 2500000,
          "blocks_total": 1500000
        }
      }
    ],
    "alerts": [
      {
        "level": "warning",
        "message": "DataNode存储使用率超过80%"
      }
    ]
  },
  "msg": "查询成功"
}
```

---

## 📈 业务监控API

### 集群管理

#### 获取可用集群列表
```http
GET /business/clusters
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "name": "CDH集群",
      "value": "cdh",
      "schedulers": ["Azkaban", "DolphinScheduler"],
      "description": "CDH集群支持Azkaban和DolphinScheduler调度"
    },
    {
      "name": "Apache集群",
      "value": "apache",
      "schedulers": ["DolphinScheduler"],
      "description": "Apache开源集群使用DolphinScheduler调度"
    }
  ]
}
```

### 业务概览

#### 获取业务监控概览
```http
GET /business/overview
```

**查询参数**:
- `cluster_name`: 集群名称（必填）
- `start_date`: 开始日期 YYYY-MM-DD（可选，默认昨天）
- `end_date`: 结束日期 YYYY-MM-DD（可选，默认昨天）

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total_jobs": 1250,
    "success_jobs": 1180,
    "failed_jobs": 70,
    "success_rate": 94.4,
    "scheduler_distribution": {
      "Azkaban": 750,
      "DolphinScheduler": 500
    },
    "peak_execution_hour": "14:00",
    "avg_execution_time": "8.5分钟"
  }
}
```

### 失败任务分析

#### 获取失败任务列表
```http
GET /business/failed-jobs
```

**查询参数**:
- `cluster_name`: 集群名称（必填）
- `start_date`: 开始日期 YYYY-MM-DD（可选）
- `end_date`: 结束日期 YYYY-MM-DD（可选）
- `page`: 页码（默认1）
- `size`: 每页数量（默认20）

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [
      {
        "job_id": "job_20241219_001",
        "job_name": "数据ETL处理任务",
        "scheduler": "Azkaban",
        "start_time": "2024-12-19T08:30:00Z",
        "end_time": "2024-12-19T08:45:00Z",
        "duration": "15分钟",
        "error_message": "HDFS空间不足",
        "retry_count": 2,
        "job_url": "http://azkaban.example.com/executor?execid=12345"
      }
    ],
    "total": 70,
    "page": 1,
    "size": 20,
    "pages": 4
  }
}
```

### 性能分析

#### 获取执行时间排行榜
```http
GET /business/top-duration-jobs
```

**查询参数**:
- `cluster_name`: 集群名称（必填）
- `start_date`: 开始日期 YYYY-MM-DD（可选）
- `end_date`: 结束日期 YYYY-MM-DD（可选）
- `limit`: 返回数量限制（默认50）

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "rank": 1,
      "job_id": "job_20241219_010",
      "job_name": "大数据全量同步任务",
      "scheduler": "DolphinScheduler",
      "duration": "2小时35分钟",
      "duration_seconds": 9300,
      "start_time": "2024-12-19T02:00:00Z",
      "end_time": "2024-12-19T04:35:00Z",
      "status": "success"
    }
  ]
}
```

#### 获取业务统计数据
```http
GET /business/statistics
```

**查询参数**:
- `cluster_name`: 集群名称（必填）
- `start_date`: 开始日期 YYYY-MM-DD（可选）
- `end_date`: 结束日期 YYYY-MM-DD（可选）

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "hourly_distribution": [
      {"hour": "00:00", "count": 25},
      {"hour": "01:00", "count": 40}
    ],
    "scheduler_performance": {
      "Azkaban": {
        "total": 750,
        "success": 720,
        "failed": 30,
        "avg_duration": "6.2分钟"
      },
      "DolphinScheduler": {
        "total": 500,
        "success": 460,
        "failed": 40,
        "avg_duration": "12.8分钟"
      }
    },
    "job_type_distribution": {
      "ETL": 450,
      "数据同步": 380,
      "报表生成": 280,
      "数据清洗": 140
    }
  }
}
```

---

## 👥 用户管理API

### 用户管理

#### 查询所有用户及其组
```http
POST /ldap/users
```

**请求体**:
```json
{
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "users": [
    {
      "uid": "hadoop",
      "username": "hadoop",
      "email": "hadoop@example.com",
      "gidNumber": "1000",
      "homeDirectory": "/home/hadoop",
      "groups": ["hadoop", "bigdata"]
    }
  ]
}
```

#### 查询指定用户信息
```http
POST /ldap/user/info
```

**请求体**:
```json
{
  "uid": "hadoop",
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "user": {
    "uid": "hadoop",
    "username": "hadoop",
    "email": "hadoop@example.com",
    "gidNumber": "1000",
    "homeDirectory": "/home/hadoop",
    "groups": ["hadoop", "bigdata"]
  }
}
```

#### 创建用户
```http
POST /ldap/user/create
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "homeDirectory": "/home/testuser",
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "user": {
    "uid": "testuser",
    "username": "testuser",
    "email": "test@example.com",
    "gidNumber": "100123",
    "homeDirectory": "/home/testuser",
    "groups": []
  }
}
```

### 组管理

#### 查询所有组及其成员
```http
POST /ldap/groups
```

**请求体**:
```json
{
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "groups": [
    {
      "groupname": "hadoop",
      "gidNumber": "1000",
      "members": ["hadoop", "hdfs", "yarn"]
    }
  ]
}
```

#### 查询指定组信息
```http
POST /ldap/group/info
```

**请求体**:
```json
{
  "groupname": "hadoop",
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "group": {
    "groupname": "hadoop",
    "gidNumber": "1000",
    "members": ["hadoop", "hdfs", "yarn"]
  }
}
```

#### 创建组
```http
POST /ldap/group/create
```

**请求体**:
```json
{
  "groupname": "testgroup",
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true,
  "group": {
    "groupname": "testgroup",
    "gidNumber": "100234",
    "members": []
  }
}
```

#### 添加用户到组
```http
POST /ldap/group/add
```

**请求体**:
```json
{
  "username": "testuser",
  "groupname": "testgroup",
  "env": "prod"
}
```

**响应示例**:
```json
{
  "success": true
}
```

---

## ❌ 错误码说明

### 通用错误码
| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 1 | 通用错误 | 查看错误消息 |
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未授权 | 检查认证信息 |
| 403 | 禁止访问 | 检查权限 |
| 404 | 资源不存在 | 检查资源ID |
| 500 | 服务器内部错误 | 联系管理员 |

### 业务错误码
| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 1001 | 数据库连接失败 | 检查数据库配置 |
| 1002 | LDAP连接失败 | 检查LDAP配置 |
| 1003 | Prometheus连接失败 | 检查Prometheus配置 |
| 2001 | 告警规则不存在 | 检查规则ID |
| 2002 | 通知模板不存在 | 检查模板ID |
| 2003 | 告警引擎未启动 | 启动告警引擎 |
| 3001 | 集群不存在 | 检查集群配置 |
| 3002 | 调度系统连接失败 | 检查调度系统配置 |
| 4001 | 用户不存在 | 检查用户ID |
| 4002 | 组不存在 | 检查组名 |
| 4003 | 权限不足 | 联系管理员 |

### 错误响应示例
```json
{
  "code": 1001,
  "data": null,
  "msg": "数据库连接失败: Connection refused"
}
```

---

## 📝 使用示例

### 创建告警规则
```bash
curl -X POST "http://localhost:8000/api/alert/rule" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CPU使用率告警",
    "category": "system",
    "promql": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
    "condition": "> 80",
    "level": "critical",
    "description": "系统CPU使用率过高",
    "suppress": "5m",
    "repeat": 1800,
    "enabled": true,
    "notify_template_id": 1
  }'
```

### 查询集群状态
```bash
curl "http://localhost:8000/api/cluster/health"
```

### 获取业务监控数据
```bash
curl "http://localhost:8000/api/business/overview?cluster_name=cdh&start_date=2024-01-15&end_date=2024-01-15"
```

### 查询用户信息
```bash
curl -X POST "http://localhost:8000/api/ldap/users" \
  -H "Content-Type: application/json" \
  -d '{"env": "prod"}'
```

---

**版本**: v2.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps开发团队

如有问题或建议，请联系开发团队或提交Issue。 