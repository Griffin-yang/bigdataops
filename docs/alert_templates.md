# 告警通知模板配置说明

## 1. 邮件告警模板

### 基本配置
```json
{
  "smtp_host": "smtp.163.com",
  "smtp_port": 465,
  "from": "sender@163.com",
  "to": ["receiver1@qq.com", "receiver2@qq.com"],
  "cc": ["cc@qq.com"],
  "require_auth": true,
  "user": "sender@163.com",
  "password": "smtp_password",
  "starttls": false,
  "ssl": true
}
```

### 模板变量
邮件主题和内容支持以下变量：
- `{rule_name}`: 规则名称
- `{level}`: 告警等级
- `{condition}`: 触发条件
- `{current_value}`: 当前值
- `{trigger_time}`: 触发时间
- `{message}`: 告警消息
- `{promql}`: PromQL表达式

### 自定义模板
```json
{
  "smtp_host": "smtp.163.com",
  "smtp_port": 465,
  "from": "alert@company.com",
  "to": ["ops@company.com"],
  "require_auth": true,
  "user": "alert@company.com",
  "password": "your_password",
  "ssl": true,
  "subject_template": "【{level}】{rule_name} 告警通知",
  "content_template": "<h2>告警详情</h2><table border='1'><tr><td>规则名称</td><td>{rule_name}</td></tr><tr><td>告警等级</td><td>{level}</td></tr><tr><td>触发条件</td><td>{condition}</td></tr><tr><td>当前值</td><td>{current_value}</td></tr><tr><td>触发时间</td><td>{trigger_time}</td></tr></table>",
  "attachments": []
}
```

## 2. HTTP告警模板

### 基本配置
```json
{
  "url": "http://example.com/webhook",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer your_token",
    "Content-Type": "application/json"
  },
  "timeout": 10,
  "verify_ssl": true
}
```

### 自定义Body模板
```json
{
  "url": "http://example.com/webhook",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer your_token"
  },
  "body_template": {
    "alert_type": "prometheus",
    "rule_name": "{rule_name}",
    "level": "{level}",
    "condition": "{condition}",
    "current_value": "{current_value}",
    "trigger_time": "{trigger_time}",
    "message": "{message}",
    "extra_info": {
      "promql": "{promql}",
      "source": "BigDataOps"
    }
  },
  "timeout": 15,
  "verify_ssl": true
}
```

### 字符串模板
```json
{
  "url": "http://example.com/webhook",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body_template": "{\"alert\": \"{rule_name}\", \"level\": \"{level}\", \"value\": \"{current_value}\", \"time\": \"{trigger_time}\"}"
}
```

## 3. 模板创建示例

### 创建邮件模板
```bash
curl -X POST "http://localhost:8000/alert/notify_template" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "默认邮件告警",
    "type": "email",
    "params": {
      "smtp_host": "smtp.163.com",
      "smtp_port": 465,
      "from": "alert@company.com",
      "to": ["ops@company.com"],
      "require_auth": true,
      "user": "alert@company.com",
      "password": "password",
      "ssl": true,
      "subject_template": "【{level}】{rule_name} 告警",
      "content_template": "<h2>{rule_name}</h2><p>当前值: {current_value}</p><p>条件: {condition}</p><p>时间: {trigger_time}</p>"
    }
  }'
```

### 创建HTTP模板
```bash
curl -X POST "http://localhost:8000/alert/notify_template" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Webhook告警",
    "type": "http",
    "params": {
      "url": "http://your-webhook.com/alert",
      "method": "POST",
      "headers": {"Authorization": "Bearer token123"},
      "body_template": {
        "rule": "{rule_name}",
        "level": "{level}",
        "value": "{current_value}",
        "time": "{trigger_time}"
      }
    }
  }'
```

## 4. 配置注意事项

1. **邮件配置**：
   - 确保SMTP服务器地址和端口正确
   - 根据邮箱服务商选择SSL或STARTTLS
   - 使用应用专用密码而非登录密码

2. **HTTP配置**：
   - 确保目标URL可访问
   - 根据接收方要求设置正确的headers
   - 考虑设置合理的超时时间

3. **模板变量**：
   - 所有变量都会被自动转换为字符串
   - 未定义的变量会保持原样
   - 建议在模板中包含关键信息以便故障排查 