# 告警系统模块完整指南

## 📋 目录
- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [核心功能](#核心功能)
- [操作指南](#操作指南)
- [配置说明](#配置说明)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

## 🎯 系统概述

BigDataOps告警系统是一个基于Prometheus的企业级告警解决方案，提供智能告警规则管理、多渠道通知、抑制策略和手动确认功能。

### 设计目标
- **智能告警**: 基于PromQL表达式的灵活告警规则
- **抑制策略**: 防止告警风暴，提供多维度抑制控制
- **多渠道通知**: 支持邮件、HTTP Webhook、乐聊等通知方式
- **手动确认**: 支持告警确认，立即停止通知
- **历史追踪**: 完整的告警历史记录和查询

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   Alert Engine  │    │   Notification  │
│                 │    │                 │    │                 │
│ - 指标收集      │◄───┤ - 规则评估      │───►│ - 邮件发送      │
│ - 数据存储      │    │ - 状态管理      │    │ - HTTP Webhook  │
│ - 查询服务      │    │ - 抑制控制      │    │ - 乐聊通知      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ - 规则存储      │
                    │ - 历史记录      │
                    │ - 模板配置      │
                    └─────────────────┘
```

### 核心组件

#### 1. 告警引擎 (Alert Engine)
- **职责**: 规则评估、状态管理、抑制控制
- **技术**: FastAPI + APScheduler
- **特点**: 异步处理、定时调度、状态持久化

#### 2. 通知服务 (Notification Service)
- **职责**: 多渠道消息发送
- **支持**: 邮件、HTTP、乐聊（群组/个人）
- **特点**: 模板渲染、重试机制、失败处理

#### 3. 数据存储 (Database)
- **职责**: 规则配置、历史记录、模板管理
- **技术**: MySQL + SQLAlchemy ORM
- **特点**: 事务支持、索引优化、数据一致性

### 数据流设计

#### 告警触发流程
```
1. Prometheus查询 → 2. 规则评估 → 3. 条件检查 → 4. 状态更新 → 5. 通知发送
```

#### 抑制控制流程
```
告警触发 → 检查抑制条件 → 检查发送次数 → 检查持续时间 → 决定是否发送
```

## ⚙️ 核心功能

### 1. 告警规则管理

#### 规则配置要素
- **PromQL表达式**: 监控指标查询
- **触发条件**: 比较运算符和阈值
- **持续时间**: 条件持续满足时间
- **告警等级**: 严重程度分类
- **抑制策略**: 防止重复告警

#### 支持的比较操作
- `>`: 大于
- `<`: 小于
- `>=`: 大于等于
- `<=`: 小于等于
- `==`: 等于
- `!=`: 不等于
- `=`: 等于（兼容性支持）

### 2. 增强抑制策略

#### 抑制维度
- **时间抑制**: 指定时间内不重复发送
- **次数限制**: 最大发送次数控制
- **持续时间**: 告警发送的最大时长
- **再通知间隔**: 重复通知的时间间隔

#### 抑制逻辑
```python
def should_send_alert(rule, current_time):
    # 检查时间抑制
    if is_in_suppress_period(rule, current_time):
        return False
    
    # 检查发送次数
    if rule.send_count >= rule.max_send_count:
        return False
    
    # 检查持续时间
    if is_over_duration(rule, current_time):
        return False
    
    return True
```

### 3. 多渠道通知

#### 邮件通知
- **SMTP配置**: 支持SSL/TLS加密
- **模板渲染**: 支持变量替换
- **附件支持**: 可配置附件发送

#### HTTP Webhook
- **REST API**: 支持POST/GET方法
- **自定义Headers**: 认证和内容类型
- **JSON模板**: 灵活的消息格式

#### 乐聊通知
- **群组模式**: 发送到指定群组
- **个人模式**: 点对点发送
- **@功能**: 支持@指定用户
- **推送通知**: 锁屏消息推送

### 4. 手动确认机制

#### 确认功能
- **单条确认**: 确认特定告警记录
- **规则确认**: 确认规则的所有告警
- **状态更新**: 自动更新告警状态
- **通知停止**: 立即停止后续通知

#### 确认流程
```
告警触发 → 发送通知 → 用户确认 → 状态更新 → 停止通知
```

## 📖 操作指南

### 1. 创建告警规则

#### 步骤1: 基础配置
1. 进入"告警规则管理"页面
2. 点击"新增规则"按钮
3. 填写基础信息：
   - 规则名称：描述性名称
   - 组件分组：选择对应组件
   - PromQL表达式：监控指标查询
   - 比较方式：选择比较操作符
   - 阈值：设置告警阈值

#### 步骤2: 高级配置
1. 设置触发持续时间（秒）
2. 选择告警等级
3. 配置抑制策略：
   - 抑制条件：如"5m"
   - 再通知间隔：如"1800"秒
   - 发送持续时间：如"3600"秒
   - 最大发送次数：如"3"

#### 步骤3: 通知配置
1. 选择通知模板
2. 配置标签信息
3. 保存规则

### 2. 配置通知模板

#### 邮件模板配置
```json
{
  "name": "邮件告警模板",
  "type": "email",
  "params": {
    "smtp_host": "smtp.163.com",
    "smtp_port": 465,
    "from": "alert@company.com",
    "to": ["ops@company.com"],
    "user": "alert@company.com",
    "password": "your_password",
    "ssl": true,
    "subject_template": "【{level}】{rule_name} 告警通知",
    "content_template": "<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p>"
  }
}
```

#### HTTP模板配置
```json
{
  "name": "HTTP告警模板",
  "type": "http",
  "params": {
    "url": "http://your-webhook.com/alert",
    "method": "POST",
    "headers": {"Authorization": "Bearer token"},
    "body_template": {
      "rule": "{rule_name}",
      "level": "{level}",
      "value": "{current_value}",
      "time": "{trigger_time}"
    }
  }
}
```

#### 乐聊模板配置
```json
{
  "name": "乐聊群组模板",
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
        "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n时间: {trigger_time}",
        "type": "text"
      }]
    }
  }
}
```

### 3. 管理告警历史

#### 查看告警历史
1. 进入"告警历史"页面
2. 使用筛选条件：
   - 组件分组
   - 告警等级
   - 告警状态
   - 时间范围
3. 查看详细信息

#### 确认告警
1. 在告警历史列表中找到要确认的告警
2. 点击"确认"按钮
3. 系统立即停止该告警的通知

#### 解决告警
1. 点击"解决"按钮
2. 输入解决原因（可选）
3. 系统更新告警状态为已解决

### 4. 复制功能使用

#### 复制告警规则
1. 在规则列表中找到要复制的规则
2. 点击"复制"按钮
3. 系统自动复制所有配置
4. 修改规则内容后保存

#### 复制通知模板
1. 在模板列表中找到要复制的模板
2. 点击"复制"按钮
3. 系统自动复制配置
4. 修改模板内容后保存

## ⚙️ 配置说明

### 环境变量配置

#### 数据库配置
```bash
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=bigdataops
MYSQL_USERNAME=root
MYSQL_PASSWORD=password
```

#### Prometheus配置
```bash
# Prometheus连接
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_TIMEOUT=30
```

#### 邮件配置
```bash
# SMTP配置
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=alert@company.com
SMTP_PASSWORD=your_password
SMTP_SSL=true
```

### 告警引擎配置

#### 调度配置
```python
# 告警检查间隔
ALERT_CHECK_INTERVAL = 30  # 秒

# 规则评估超时
RULE_EVALUATION_TIMEOUT = 10  # 秒

# 通知发送超时
NOTIFICATION_TIMEOUT = 30  # 秒
```

#### 抑制配置
```python
# 默认抑制时间
DEFAULT_SUPPRESS_TIME = "5m"

# 默认发送持续时间
DEFAULT_DURATION = 3600  # 秒

# 默认最大发送次数
DEFAULT_MAX_SEND_COUNT = 5
```

## 🔧 故障排查

### 常见问题

#### 1. 告警不触发
**症状**: 配置了告警规则但没有触发

**排查步骤**:
1. 检查Prometheus连接
   ```bash
   curl http://localhost:9090/api/v1/query?query=up
   ```

2. 验证PromQL表达式
   ```bash
   curl "http://localhost:9090/api/v1/query?query=your_promql_expression"
   ```

3. 检查告警引擎状态
   ```bash
   curl http://localhost:8000/api/alert/engine/status
   ```

4. 查看后端日志
   ```bash
   tail -f /var/log/bigdataops/alert.log
   ```

#### 2. 通知发送失败
**症状**: 告警触发但通知没有发送

**排查步骤**:
1. 检查模板配置
   - 验证SMTP配置
   - 检查HTTP URL可访问性
   - 确认乐聊API配置

2. 查看通知日志
   ```bash
   grep "notification" /var/log/bigdataops/alert.log
   ```

3. 测试通知模板
   ```bash
   curl -X POST "http://localhost:8000/api/alert/notify_template/test" \
     -H "Content-Type: application/json" \
     -d '{"template_id": 1, "test_data": {...}}'
   ```

#### 3. 抑制策略不生效
**症状**: 告警重复发送，抑制策略无效

**排查步骤**:
1. 检查规则配置
   ```sql
   SELECT name, suppress, repeat, duration, max_send_count 
   FROM alert_rule WHERE id = ?;
   ```

2. 检查告警状态
   ```sql
   SELECT alert_state, send_count, alert_start_time 
   FROM alert_rule WHERE id = ?;
   ```

3. 查看抑制逻辑日志
   ```bash
   grep "suppress" /var/log/bigdataops/alert.log
   ```

### 调试工具

#### 告警引擎测试
```bash
# 测试规则
curl -X POST "http://localhost:8000/api/alert/engine/test" \
  -H "Content-Type: application/json" \
  -d '{"rule_id": 1}'

# 手动触发告警
curl -X POST "http://localhost:8000/api/alert/engine/trigger" \
  -H "Content-Type: application/json" \
  -d '{"rule_id": 1, "force": true}'
```

#### 数据库查询
```sql
-- 查看告警规则状态
SELECT name, alert_state, send_count, last_alert_time 
FROM alert_rule WHERE enabled = 1;

-- 查看最近告警历史
SELECT rule_name, status, created_at, acknowledged 
FROM alert_history 
ORDER BY created_at DESC LIMIT 10;

-- 查看确认状态
SELECT rule_name, acknowledged_by, acknowledged_at 
FROM alert_history 
WHERE acknowledged = 1;
```

## 🎯 最佳实践

### 1. 告警规则设计

#### 规则命名规范
- 使用描述性名称
- 包含组件和指标信息
- 示例：`HDFS_DataNode_Storage_Usage_Alert`

#### 阈值设置建议
- **CPU使用率**: 80%警告，90%严重
- **内存使用率**: 85%警告，95%严重
- **磁盘使用率**: 85%警告，95%严重
- **服务状态**: 0表示异常，1表示正常

#### 持续时间配置
- **系统级告警**: 30-60秒
- **应用级告警**: 60-120秒
- **业务级告警**: 120-300秒

### 2. 抑制策略优化

#### 抑制时间设置
| 告警等级 | 抑制时间 | 再通知间隔 | 最大次数 |
|---------|---------|-----------|---------|
| Critical | 1-2分钟 | 5-10分钟 | 5-10次 |
| High | 2-5分钟 | 10-30分钟 | 3-5次 |
| Medium | 5-15分钟 | 30-60分钟 | 2-3次 |
| Low | 15-30分钟 | 1-2小时 | 1-2次 |

#### 避免告警风暴
- 设置合理的抑制时间
- 使用分层告警策略
- 配置告警聚合规则

### 3. 通知配置优化

#### 邮件模板设计
- 使用HTML格式提高可读性
- 包含关键信息：规则名、等级、当前值、时间
- 添加故障排查建议

#### 乐聊消息优化
- 使用表情符号提高可读性
- 结构化消息格式
- 支持@相关人员

### 4. 监控和维护

#### 系统监控
- 监控告警引擎状态
- 跟踪通知发送成功率
- 监控数据库性能

#### 定期维护
- 清理历史告警数据
- 优化数据库索引
- 更新告警规则配置

### 5. 安全考虑

#### 访问控制
- 限制告警接口访问
- 使用HTTPS传输
- 配置API认证

#### 数据保护
- 加密敏感配置信息
- 定期备份告警配置
- 审计告警操作日志

---

**版本**: v2.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps开发团队

如有问题或建议，请联系开发团队或提交Issue。 