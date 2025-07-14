# BigDataOps API 文档

本文件为 BigDataOps 后端服务的接口文档，涵盖所有主要功能接口，便于前后端协作与对接。

---

## 1. 查询所有用户及其组
- **接口路径**：`POST /ldap/users`
- **请求体**：
  ```json
  {
    "env": "prod"
  }
  ```
- **说明**：返回所有 LDAP 用户及其所在组信息。

---

## 2. 查询指定用户信息
- **接口路径**：`POST /ldap/user/info`
- **请求体**：
  ```json
  {
    "uid": "hadoop",
    "env": "prod"
  }
  ```
- **说明**：根据 uid 查询用户详细信息及所在组。

---

## 3. 查询所有组及其成员
- **接口路径**：`POST /ldap/groups`
- **请求体**：
  ```json
  {
    "env": "prod"
  }
  ```
- **说明**：返回所有 LDAP 组及其成员信息。

---

## 4. 查询指定组信息
- **接口路径**：`POST /ldap/group/info`
- **请求体**：
  ```json
  {
    "groupname": "hadoop",
    "env": "prod"
  }
  ```
- **说明**：根据 groupname 查询组详细信息及成员。

---

## 5. 创建用户
- **接口路径**：`POST /ldap/user/create`
- **请求体**：
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",   // 可选
    "homeDirectory": "/home/testuser", // 可选
    "env": "prod"                  // 可选
  }
  ```
- **说明**：uidNumber 和默认 gidNumber 由后端自动生成，前端无需传递。
- **返回示例**：
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

---

## 6. 创建组
- **接口路径**：`POST /ldap/group/create`
- **请求体**：
  ```json
  {
    "groupname": "testgroup",
    "env": "prod"          // 可选
  }
  ```
- **说明**：gidNumber 由后端自动生成，前端无需传递。
- **返回示例**：
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

---

## 7. 添加用户到组
- **接口路径**：`POST /ldap/group/add`
- **请求体**：
  ```json
  {
    "username": "testuser",
    "groupname": "testgroup",
    "env": "prod"
  }
  ```
- **返回示例**：
  ```json
  {
    "success": true
  }
  ```

---

## 8. Alertmanager Webhook
- **接口路径**：`POST /alert/webhook`
- **请求体**：
  ```json
  {
    "group_id": "123456",
    "message": "告警内容"
  }
  ```
- **说明**：接收 Alertmanager 告警并转发到下游（如云信群组等）。

---

## 9. 告警规则管理

### 查询规则列表（新版，支持分页和筛选）
- **接口路径**：`GET /alert/rule`
- **查询参数**：
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认20，最大100）
  - `category`: 组件分组筛选（可选）
  - `level`: 告警等级筛选（可选）
  - `enabled`: 启用状态筛选（可选）
  - `alert_state`: 告警状态筛选（可选）
  - `name`: 规则名称搜索（可选）
- **示例**：`GET /alert/rule?page=1&size=10&category=hdfs&level=critical`
- **返回示例**：
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
          "repeat": "1h",
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
      "size": 10,
      "pages": 5
    },
    "msg": "查询成功"
  }
  ```

### 获取规则分组列表
- **接口路径**：`GET /alert/rule/categories`
- **说明**：获取所有可用的规则分组。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": ["hdfs", "hive", "spark", "mysql", "kafka", "zookeeper"],
    "msg": "查询成功"
  }
  ```

### 获取规则统计信息
- **接口路径**：`GET /alert/rule/stats`
- **说明**：获取规则的统计数据。
- **返回示例**：
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

### 查询单条规则
- **接口路径**：`GET /alert/rule/{rule_id}`
- **说明**：根据ID获取单条规则。
- **返回示例**：同上单个规则对象格式。

### 新建规则
- **接口路径**：`POST /alert/rule`
- **请求体**：
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
    "repeat": "1h",
    "enabled": true,
    "notify_template_id": 1
  }
  ```
- **说明**：`category`、`alert_state` 等字段后端会设置默认值。
- **返回示例**：返回创建的规则对象。

### 更新规则
- **接口路径**：`PUT /alert/rule/{rule_id}`
- **请求体**：同新建规则。
- **返回示例**：返回更新后的规则对象。

### 删除规则
- **接口路径**：`DELETE /alert/rule/{rule_id}`
- **说明**：删除指定ID的规则。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"success": true},
    "msg": "删除成功"
  }
  ```

### 批量更新规则分组
- **接口路径**：`POST /alert/rule/batch_update_category`
- **请求体**：
  ```json
  {
    "rule_ids": [1, 2, 3],
    "category": "hdfs"
  }
  ```
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"updated_count": 3},
    "msg": "成功更新 3 条规则的分组"
  }
  ```

---

## 10. 告警历史管理

### 查询告警历史列表
- **接口路径**：`GET /alert/history`
- **查询参数**：
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认20，最大100）
  - `category`: 组件分组筛选（可选）
  - `level`: 告警等级筛选（可选）
  - `status`: 告警状态筛选（可选：firing, resolved）
  - `rule_name`: 规则名称搜索（可选）
  - `start_time`: 开始时间（可选，ISO格式）
  - `end_time`: 结束时间（可选，ISO格式）
- **示例**：`GET /alert/history?page=1&size=20&category=hdfs&level=critical&status=firing`
- **返回示例**：
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

### 获取告警历史统计
- **接口路径**：`GET /alert/history/stats`
- **查询参数**：
  - `days`: 统计天数（默认7天）
  - `category`: 组件分组筛选（可选）
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "total_alerts": 100,
      "firing_alerts": 5,
      "resolved_alerts": 95,
      "category_stats": [
        {
          "category": "hdfs",
          "total_count": 30,
          "firing_count": 2,
          "resolved_count": 28
        }
      ],
      "level_stats": [
        {
          "level": "critical",
          "count": 15
        }
      ],
      "daily_stats": [
        {
          "date": "2024-12-19",
          "total_count": 20,
          "firing_count": 2,
          "resolved_count": 18
        }
      ]
    },
    "msg": "查询成功"
  }
  ```

### 手动解决告警
- **接口路径**：`POST /alert/history/{history_id}/resolve`
- **请求体**：
  ```json
  {
    "reason": "手动处理完成"
  }
  ```
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"success": true},
    "msg": "告警已解决"
  }
  ```

---

## 11. 告警通知模板管理

### 查询所有模板
- **接口路径**：`GET /alert/notify_template`
- **查询参数**：
  - `type`（可选）：模板类型过滤（email/http/lechat）
- **说明**：获取所有通知模板，支持按类型筛选。
- **返回示例**：
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
      },
      {
        "id": 2,
        "name": "HTTP通知模板",
        "type": "http",
        "params": {
          "url": "https://api.example.com/webhook",
          "method": "POST",
          "headers": {"Content-Type": "application/json"},
          "body_template": {
            "alert": {
              "rule": "{rule_name}",
              "level": "{level}",
              "value": "{current_value}"
            }
          },
          "timeout": 10,
          "verify_ssl": true
        },
        "created_at": "2024-06-01T12:00:00Z",
        "updated_at": "2024-06-01T12:00:00Z"
      },
      {
        "id": 3,
        "name": "乐聊告警模板",
        "type": "lechat",
        "params": {
          "url": "http://your-host/api/message/sendTeam",
          "fromId": "lyj-dw",
          "groupId": "group-123456",
          "ext": {"group": "oa"},
          "body_template": {
            "robot": {"type": "robotAnswer"},
            "type": "multi",
            "msgs": [{
              "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n时间: {trigger_time}",
              "type": "text"
            }]
          },
          "pushcontent": "告警提醒",
          "option": {"push": true}
        },
        "created_at": "2024-06-01T12:00:00Z",
        "updated_at": "2024-06-01T12:00:00Z"
      }
    ],
    "msg": "查询成功"
  }
  ```

### 获取单个模板
- **接口路径**：`GET /alert/notify_template/{template_id}`
- **说明**：根据ID获取单个模板详情。
- **返回示例**：返回单个模板对象。

### 新建模板
- **接口路径**：`POST /alert/notify_template`
- **请求体示例（邮件模板）**：
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
- **请求体示例（HTTP模板）**：
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
- **请求体示例（乐聊群组模板）**：
  ```json
  {
    "name": "乐聊群组告警模板",
    "type": "lechat",
    "params": {
      "mode": "group",
      "url": "http://your-host/api/message/sendTeam",
      "fromId": "lyj-dw",
      "groupId": "group-123456",
      "ext": {
        "group": "oa",
        "hait": ["10001"],
        "atName": ["@张三(研发部)"],
        "haitPosition": [0]
      },
      "body_template": {
        "robot": {"type": "robotAnswer"},
        "type": "multi",
        "msgs": [{
          "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n触发时间: {trigger_time}\n描述: {description}",
          "type": "text"
        }]
      },
      "pushcontent": "告警提醒",
      "option": {"push": true},
      "payload": "{\"custom_data\": \"value\"}"
    }
  }
  ```
- **请求体示例（乐聊个人模板）**：
  ```json
  {
    "name": "乐聊个人告警模板",
    "type": "lechat",
    "params": {
      "mode": "personal",
      "url": "http://your-host/api/message/sendPersonal",
      "fromId": "lyj-dw",
      "userIds": "233655,056518,283669",
      "ext": {
        "group": "oa"
      },
      "body_template": {
        "robot": {"type": "robotAnswer"},
        "type": "multi",
        "msgs": [{
          "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n触发时间: {trigger_time}\n描述: {description}",
          "type": "text"
        }]
      },
      "userMapping": {
        "233655": "br",
        "056518": "056518",
        "283669": "dq",
        "357768": "GaoYuFei",
        "391302": "391302"
      },
      "pushcontent": "告警提醒",
      "option": {"push": true}
    }
  }
  ```
- **说明**：
  - **乐聊模板参数详解**：
    - `mode`：发送模式（必填）
      - `group`：群组模式，发送到乐聊群组
      - `personal`：个人模式，点对点发送给指定用户
    - `url`：乐聊API接口地址（必填）
    - `fromId`：消息发送者账号（必填）
    - **群组模式参数**：
      - `groupId`：群组ID，接收消息的群（群组模式必填）
    - **个人模式参数**：
      - `userIds`：用户工号列表，多个用逗号分隔（个人模式必填）
      - `userMapping`：工号到用户ID的映射表（个人模式可选）
    - `ext`：扩展字段，JSON对象格式，包含：
      - `group`：系统标识，如"oa"（必填）
      - `hait`：被@人的IM账号列表（可选）
      - `atName`：展示用的@名（可选）
      - `haitPosition`：@位置顺序（可选）
    - `body_template`：消息体模板，JSON对象格式（必填）
    - `pushcontent`：锁屏推送提示内容（可选）
    - `option`：发送选项，如是否推送（可选）
    - `payload`：iOS专用推送字段，JSON字符串，不超过2KB（可选）
  - **支持的变量**：`{rule_name}`, `{level}`, `{current_value}`, `{trigger_time}`, `{description}`, `{labels}` 等
- **返回示例**：返回创建的模板对象。

### 更新模板
- **接口路径**：`PUT /alert/notify_template/{template_id}`
- **请求体**：
  ```json
  {
    "name": "更新后的模板名称",
    "params": {
      // 更新的参数，格式同新建模板
    }
  }
  ```
- **说明**：只能更新name和params字段，type字段不可修改。
- **返回示例**：返回更新后的模板对象。

### 删除模板
- **接口路径**：`DELETE /alert/notify_template/{template_id}`
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"success": true},
    "msg": "删除成功"
  }
  ```

---

## 12. 告警引擎控制

### 启动告警引擎
- **接口路径**：`POST /alert/engine/start`
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"success": true},
    "msg": "告警引擎启动成功"
  }
  ```

### 停止告警引擎
- **接口路径**：`POST /alert/engine/stop`
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"success": true},
    "msg": "告警引擎停止成功"
  }
  ```

### 获取引擎状态
- **接口路径**：`GET /alert/engine/status`
- **返回示例**：
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

### 测试规则
- **接口路径**：`POST /alert/engine/test`
- **请求体**：
  ```json
  {
    "promql": "up == 0",
    "labels": "instance=localhost:9090"
  }
  ```
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "result": "success",
      "value": "1",
      "labels": {"instance": "localhost:9090"},
      "timestamp": "2024-12-19T10:30:00Z"
    },
    "msg": "测试成功"
  }
  ```

---

## 16. 集群监控管理

### 获取集群总览信息
- **接口路径**：`GET /api/cluster/overview`
- **查询参数**：
  - `service`: 服务筛选（可选，如："大数据"）
  - `job`: 任务筛选（可选，如："consul-node"）
  - `role`: 角色筛选（可选，如："bigdata-storage"）
- **说明**：获取集群节点、资源使用情况等总览数据。支持按服务、任务、角色筛选。
- **示例**：`GET /api/cluster/overview?service=大数据&role=bigdata-storage`
- **返回示例**：
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

### 获取集群节点列表
- **接口路径**：`GET /api/cluster/nodes`
- **查询参数**：
  - `status`: 节点状态筛选（可选：healthy/unhealthy）
  - `service`: 服务筛选（可选，如："大数据"）
  - `job`: 任务筛选（可选，如："consul-node"）
  - `role`: 角色筛选（可选，如："bigdata-storage"）
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认20，最大100）
- **示例**：`GET /api/cluster/nodes?service=大数据&status=healthy&page=1&size=10`
- **返回示例**：
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

### 获取组件概览
- **接口路径**：`GET /api/cluster/components`
- **说明**：获取所有大数据组件的状态概览。
- **返回示例**：
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

### 获取组件详细信息
- **接口路径**：`GET /api/cluster/components/{component_name}`
- **说明**：获取特定组件的详细监控信息。
- **示例**：`GET /api/cluster/components/HDFS`
- **返回示例**：
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

### 集群健康检查
- **接口路径**：`GET /api/cluster/health`
- **说明**：快速健康检查接口，用于监控系统。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "status": "healthy",
      "message": "集群状态良好",
      "details": {
        "total_nodes": 10,
        "healthy_nodes": 10,
        "unhealthy_nodes": 0,
        "avg_cpu_usage": 65.5,
        "avg_memory_usage": 72.3
      }
    },
    "msg": "健康检查完成"
  }
  ```

### 集群监控筛选参数说明

**可用的service值**：
- `大数据`：主要大数据服务
- `bigdata-ds-new`：数据科学服务
- `bigdata-hadoop-new`：Hadoop服务
- `bigdata-hive-new`：Hive服务  
- `bigdata-zookeeper-new`：ZooKeeper服务

**可用的job值**：
- `consul-node`：Consul节点监控
- `bigdata-ds-new`：大数据数据科学
- `bigdata-hadoop-new`：大数据Hadoop服务
- `bigdata-hive-new`：大数据Hive服务
- `bigdata-zookeeper-new`：大数据ZooKeeper服务
- `bigdata-exporter-new`：大数据导出器

**可用的role值**：
- `bigdata-storage`：存储节点
- `bigdata-compute`：计算节点
- `bigdata-master`：主节点

**说明**：
- 推荐使用`service="大数据"`作为默认筛选条件
- 可以组合多个筛选条件进行精确查询
- 不提供筛选参数时返回所有节点数据
- 前端界面默认显示`service="大数据"`的节点，并提供job、role等筛选选项
- 支持按job筛选来查看特定大数据组件所在的机器

---

## 17. 业务监控管理

### 获取可用集群列表
- **接口路径**：`GET /api/business/clusters`
- **说明**：获取支持业务监控的集群列表。
- **返回示例**：
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

### 获取业务监控概览
- **接口路径**：`GET /api/business/overview`
- **查询参数**：
  - `cluster_name`: 集群名称（必填）
  - `start_date`: 开始日期 YYYY-MM-DD（可选，默认昨天）
  - `end_date`: 结束日期 YYYY-MM-DD（可选，默认昨天）
- **示例**：`GET /api/business/overview?cluster_name=cdh&start_date=2024-12-18&end_date=2024-12-19`
- **返回示例**：
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

### 获取失败任务列表
- **接口路径**：`GET /api/business/failed-jobs`
- **查询参数**：
  - `cluster_name`: 集群名称（必填）
  - `start_date`: 开始日期 YYYY-MM-DD（可选）
  - `end_date`: 结束日期 YYYY-MM-DD（可选）
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认20）
- **返回示例**：
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

### 获取执行时间排行榜
- **接口路径**：`GET /api/business/top-duration-jobs`
- **查询参数**：
  - `cluster_name`: 集群名称（必填）
  - `start_date`: 开始日期 YYYY-MM-DD（可选）
  - `end_date`: 结束日期 YYYY-MM-DD（可选）
  - `limit`: 返回数量限制（默认50）
- **返回示例**：
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

### 获取业务统计数据
- **接口路径**：`GET /api/business/statistics`
- **查询参数**：
  - `cluster_name`: 集群名称（必填）
  - `start_date`: 开始日期 YYYY-MM-DD（可选）
  - `end_date`: 结束日期 YYYY-MM-DD（可选）
- **返回示例**：
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

## 18. 告警历史扩展功能

### 获取告警分组列表
- **接口路径**：`GET /alert/history/categories`
- **说明**：获取告警历史中存在的所有分组。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": ["hdfs", "hive", "spark", "mysql", "kafka", "zookeeper"],
    "msg": "查询成功"
  }
  ```

### 删除告警历史记录
- **接口路径**：`DELETE /alert/history/{history_id}`
- **说明**：删除指定的告警历史记录。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"id": 123},
    "msg": "删除成功"
  }
  ```

### 批量删除告警历史
- **接口路径**：`POST /alert/history/batch_delete`
- **请求体**：
  ```json
  {
    "history_ids": [1, 2, 3, 4, 5]
  }
  ```
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {"deleted_count": 5},
    "msg": "成功删除 5 条记录"
  }
  ```

### 确认告警（停止发送）
- **接口路径**：`POST /alert/history/{history_id}/acknowledge`
- **查询参数**：
  - `acknowledged_by`: 确认人（必填）
- **说明**：确认指定告警，停止继续发送通知。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "history_id": 123,
      "acknowledged_by": "admin",
      "acknowledged_at": "2024-12-19T10:30:00Z"
    },
    "msg": "告警确认成功，已停止发送"
  }
  ```

### 确认规则的所有告警
- **接口路径**：`POST /alert/rule/{rule_id}/acknowledge`
- **查询参数**：
  - `acknowledged_by`: 确认人（必填）
- **说明**：确认指定规则的所有告警，将规则状态设为静默。
- **返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "rule_id": 15,
      "acknowledged_by": "admin",
      "previous_state": "alerting"
    },
    "msg": "规则告警确认成功，已停止发送"
  }
  ```

---

## 通用响应格式

所有接口都遵循统一的响应格式：

```json
{
  "code": 0,           // 0表示成功，其他表示错误
  "data": {},          // 返回的数据，成功时有值，失败时为null
  "msg": "操作成功"     // 响应消息
}
```

## 组件分组常量

系统支持以下组件分组：
- `hdfs`: HDFS
- `hive`: Hive  
- `spark`: Spark
- `mysql`: MySQL
- `kafka`: Kafka
- `zookeeper`: ZooKeeper
- `yarn`: YARN
- `hbase`: HBase
- `elasticsearch`: Elasticsearch
- `prometheus`: Prometheus
- `grafana`: Grafana
- `other`: 其他

## 告警等级常量

- `critical`: 严重
- `warning`: 警告  
- `info`: 信息

## 告警状态常量

- `ok`: 正常
- `alerting`: 告警中
- `silenced`: 已静默

---

## 13. 乐聊告警集成

### 乐聊API接口格式

乐聊告警使用 `application/x-www-form-urlencoded` 格式发送请求，具体格式如下：

```bash
curl -X POST http://your-host/api/message/sendTeam \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'type=100' \
  -d 'body={"robot":{"type":"robotAnswer"},"type":"multi","msgs":[{"text":"告警内容","type":"text"}]}' \
  -d 'ext={"group":"oa"}' \
  -d 'fromId=lyj-dw' \
  -d 'groupId=group-123456' \
  -d 'pushcontent=告警提醒' \
  -d 'option={"push":true}'
```

### 请求参数说明

| 参数名 | 是否必须 | 说明 |
|--------|----------|------|
| type | 是 | 消息类型，固定为 "100"（表示文本消息） |
| body | 是 | 消息体 JSON 字符串，包含文本内容、可选的 @人信息 |
| ext | 是 | 扩展字段 JSON 字符串，至少包含 "group"（系统标识，如 "oa"） |
| fromId | 是 | 消息发送者账号 |
| groupId | 是 | 群组 ID（接收消息的群） |
| option | 否 | 发送选项，如是否推送，格式：{"push":true} |
| pushcontent | 否 | 锁屏推送提示内容（如任务提醒） |
| payload | 否 | iOS 专用推送字段（JSON字符串，不超过2KB） |

### ext 扩展字段格式

```json
{
  "group": "oa",
  "hait": ["10001"],
  "atName": ["@张三(研发部)"],
  "haitPosition": [0]
}
```

- 若无 @人，可简化为：`{"group":"oa"}`
- `hait` 为被 @ 人的 IM账号列表
- `atName` 为展示用的@名
- `haitPosition` 与上述两个一一对应，表示@位置顺序

### 消息体格式示例

```json
{
  "robot": {"type": "robotAnswer"},
  "type": "multi",
  "msgs": [
    {
      "text": "🚨 【高】告警通知\n规则名称: CPU使用率过高\n当前值: 85%\n触发时间: 2024-12-25 10:30:00\n描述: 服务器CPU使用率超过阈值",
      "type": "text"
    }
  ]
}
```

### 告警分发接口

- **接口路径**：`POST /alert/dispatch`
- **群组模式请求体示例**：
  ```json
  {
    "level": "high",
    "downstream": "lechat",
    "params": {
      "mode": "group",
      "url": "http://your-host/api/message/sendTeam",
      "fromId": "lyj-dw",
      "groupId": "group-123456",
      "ext": "{\"group\":\"oa\"}",
      "body": "{\"robot\":{\"type\":\"robotAnswer\"},\"type\":\"multi\",\"msgs\":[{\"text\":\"告警内容\",\"type\":\"text\"}]}",
      "pushcontent": "告警提醒"
    }
  }
  ```
- **个人模式请求体示例**：
  ```json
  {
    "level": "high",
    "downstream": "lechat",
    "params": {
      "mode": "personal",
      "url": "http://your-host/api/message/sendPersonal",
      "fromId": "lyj-dw",
      "userIds": "233655,056518,283669",
      "ext": "{\"group\":\"oa\"}",
      "body": "{\"robot\":{\"type\":\"robotAnswer\"},\"type\":\"multi\",\"msgs\":[{\"text\":\"CPU使用率告警\",\"type\":\"text\"}]}",
      "userMapping": {
        "233655": "br",
        "056518": "056518", 
        "283669": "dq"
      },
      "pushcontent": "告警提醒"
    }
  }
  ```
- **群组模式返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "success": true,
      "status_code": 200,
      "response": "ok",
      "msg": "乐聊群组告警发送成功"
    },
    "msg": "分发成功"
  }
  ```
- **个人模式返回示例**：
  ```json
  {
    "code": 0,
    "data": {
      "success": true,
      "total_count": 3,
      "success_count": 3,
      "failed_count": 0,
      "results": [
        {
          "user_id": "233655",
          "mapped_user_id": "br",
          "success": true,
          "status_code": 200,
          "response": "ok"
        },
        {
          "user_id": "056518", 
          "mapped_user_id": "056518",
          "success": true,
          "status_code": 200,
          "response": "ok"
        },
        {
          "user_id": "283669",
          "mapped_user_id": "dq", 
          "success": true,
          "status_code": 200,
          "response": "ok"
        }
      ],
      "msg": "乐聊个人告警发送完成: 成功 3/3"
    },
    "msg": "分发成功"
  }
  ```

### 模板变量支持

在乐聊模板中，可以使用以下变量进行动态替换：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{rule_name}` | 规则名称 | "CPU使用率告警" |
| `{level}` | 告警等级 | "high", "critical" |
| `{current_value}` | 当前监控值 | "85%" |
| `{threshold}` | 告警阈值 | "80" |
| `{trigger_time}` | 触发时间 | "2024-12-25 10:30:00" |
| `{description}` | 规则描述 | "服务器CPU使用率过高" |
| `{labels}` | 标签信息 | "cluster=prod,service=api" |

使用示例：
```json
{
  "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n时间: {trigger_time}"
}
```

---

## 14. 下游告警通知参数说明

### 1. IM（自定义接口）
- **类型**：im
- **参数**：
  - 由后端配置，通常只需传递内容、群id等
- **示例**：
  ```json
  {
    "downstream": "im",
    "params": {
      "content": "告警内容...",
      "group_id": "123456"
    }
  }
  ```

### 2. 邮件（本地SMTP发送）
- **类型**：email
- **参数**：
  - `smtp_host`：SMTP服务器
  - `smtp_port`：端口
  - `smtp_user`：用户名
  - `smtp_password`：密码
  - `from_addr`：发件人
  - `to_addrs`：收件人（逗号分隔）
  - `ssl`：是否SSL（bool）
  - `subject`：主题
  - `content_type`：plain/html
  - `content`：正文
- **示例**：
  ```json
  {
    "downstream": "email",
    "params": {
      "smtp_host": "smtp.example.com",
      "smtp_port": 465,
      "smtp_user": "user@example.com",
      "smtp_password": "password",
      "from_addr": "user@example.com",
      "to_addrs": "a@b.com,b@c.com",
      "ssl": true,
      "subject": "告警",
      "content_type": "plain",
      "content": "CPU使用率过高"
    }
  }
  ```
- **返回示例**：
  ```json
  { "success": true }
  ```

### 3. 企业微信
- **类型**：wecom
- **参数**：
  - `corp_id`：企业ID
  - `corp_secret`：密钥
  - `agent_id`：应用ID（或chat_id）
  - `to_user`：接收人（用|分隔，@all为全员）
  - `msg_type`：消息类型（text等）
  - `content`：内容
- **示例**：
  ```json
  {
    "downstream": "wecom",
    "params": {
      "corp_id": "xxx",
      "corp_secret": "yyy",
      "agent_id": 1000002,
      "to_user": "@all",
      "msg_type": "text",
      "content": "CPU告警: 95%"
    }
  }
  ```
- **返回示例**：
  ```json
  { "errcode": 0, "errmsg": "ok" }
  ```

### 4. HTTP
- **类型**：http
- **参数**：
  - `url`：目标地址
  - `method`：请求方式（POST/GET等）
  - `headers`：请求头（字典）
  - `body`：请求体（字符串，支持模板）
  - `content_type`：内容类型
- **示例**：
  ```json
  {
    "downstream": "http",
    "params": {
      "url": "http://example.com/alert",
      "method": "POST",
      "headers": {"Authorization": "Bearer xxx"},
      "body": "{\"msg\": \"CPU告警\"}",
      "content_type": "application/json"
    }
  }
  ```
- **返回示例**：
  ```json
  { "success": true, "status_code": 200, "resp": "ok" }
  ```

---

## 15. 通知渠道模板管理（旧版接口说明）

### 查询所有模板
- **接口路径**：`GET /alert/notify_template`
- **请求参数**：
  - `type`（可选）：下游类型过滤（email/wecom/http等）
- **返回示例**：
  ```json
  [
    {
      "id": 1,
      "name": "运维组邮箱",
      "type": "email",
      "params": {
        "to_addrs": "a@b.com,b@c.com",
        "subject": "告警",
        "content_type": "plain"
      },
      "created_at": "2024-06-01T12:00:00",
      "updated_at": "2024-06-01T12:00:00"
    }
  ]
  ```

### 查询单个模板
- **接口路径**：`GET /alert/notify_template/{template_id}`
- **返回示例**：同上，返回单个对象。

### 新建模板
- **接口路径**：`POST /alert/notify_template`
- **请求体**：
  ```json
  {
    "name": "运维组邮箱",
    "type": "email",
    "params": {
      "to_addrs": "a@b.com,b@c.com",
      "subject": "告警",
      "content_type": "plain"
    }
  }
  ```
- **返回示例**：同上，返回新建对象。

### 更新模板
- **接口路径**：`PUT /alert/notify_template/{template_id}`
- **请求体**：同上。
- **返回示例**：同上，返回更新后对象。

### 删除模板
- **接口路径**：`DELETE /alert/notify_template/{template_id}`
- **返回示例**：
  ```json
  { "success": true }
  ```

---

> 所有接口均支持通过 env 参数区分环境，所有请求和返回均为 JSON 格式。 

---

## 新增功能说明

### Job筛选选项更新

**可用的job值**：
- `consul-node`：Consul节点监控
- `bigdata-ds-new`：大数据数据科学
- `bigdata-hadoop-new`：大数据Hadoop服务
- `bigdata-hive-new`：大数据Hive服务
- `bigdata-zookeeper-new`：大数据ZooKeeper服务
- `bigdata-exporter-new`：大数据导出器

**前端筛选增强**：
- 支持`filterable`和`allow-create`，可以输入自定义job参数
- 默认提供常用的大数据组件job选项

### 基于port_status的服务角色查询

**功能说明**：
- 节点的服务角色现在基于`port_status`指标查询
- 自动解析运行在每个节点上的具体服务组件
- 支持健康状态检查（只显示status=1的服务）

**port_status指标格式**：
```prometheus
port_status{group="bigdata-exporter", instance="192.168.7.20:9333", job="bigdata-exporter-new", name="Ranger-admin_bd-prod-lyj-master02", port="6080", role="bigdata-exporter"}
```

**支持的服务识别**：
- **Ranger**: Ranger Admin (6080), Ranger UserSync (5151)
- **HDFS**: NameNode (9870), DataNode (9864), JournalNode (8485)
- **YARN**: ResourceManager (8088), NodeManager (8042)
- **Hive**: HiveServer2 (10000), Hive MetaStore (9083)
- **Spark**: Spark History Server (18080/18081)
- **DolphinScheduler**: DS-Master (5678), DS-ApiServer (12345)
- **ZooKeeper**: ZooKeeper (2181)
- **其他**: LDAP (389), Kafka (9092), Elasticsearch (9200), Grafana (3000), Prometheus (9090)

**角色识别逻辑**：
1. 首先通过服务名称匹配（如：Ranger-admin → Ranger Admin）
2. 如果名称匹配失败，通过端口号推断服务类型
3. 最后使用name字段的前缀作为角色名

**查询示例**：
```bash
# 查询特定节点的服务角色
GET /api/cluster/nodes?service=大数据&job=bigdata-exporter-new

# 返回的roles字段示例：
"roles": ["Ranger Admin", "HDFS JournalNode", "DolphinScheduler API", "ZooKeeper"]
```

**优势**：
- 实时反映节点上实际运行的服务
- 基于健康状态（port_status=1）显示可用服务
- 支持动态服务发现和角色识别
- 提供详细的服务端口信息 