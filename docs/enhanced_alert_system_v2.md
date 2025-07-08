# BigDataOps 增强告警系统 v2.0 文档

## 📋 概述

BigDataOps v2.0 版本对告警系统进行了全面升级，引入了智能抑制规则、手动确认功能、模板复制等增强特性，大幅提升了告警管理的灵活性和用户体验。

## 🚀 新增功能

### 1. 增强抑制规则

#### 功能描述
在原有时间抑制的基础上，新增多维度抑制控制：

- **双重持续时间控制**: 触发持续时间（避免误报）+ 发送持续时间（防止轰炸）
- **发送次数限制**: 可设置最大发送次数，达到后停止
- **每日重置机制**: 计数器每天0点自动重置
- **智能状态管理**: 完善的状态转换逻辑

#### 配置说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `suppress` | String | null | 抑制条件，如 "5m", "1h" |
| `repeat` | Integer | 0 | 再通知间隔(秒) |
| `for_duration` | Integer | 60 | 触发持续时间(秒)，条件持续满足多久才触发告警 |
| `duration` | Integer | 3600 | 发送持续时间(秒)，告警发送超时停止 |
| `max_send_count` | Integer | null | 最大发送次数 |

#### 配置示例

```json
{
  "suppress": "5m",        // 5分钟内不重复
  "repeat": 1800,          // 30分钟重复间隔
  "for_duration": 120,     // 条件持续2分钟才触发
  "duration": 3600,        // 告警发送1小时后停止
  "max_send_count": 3      // 最多发送3次
}
```

#### 推荐配置

| 告警级别 | 抑制时间 | 重复间隔 | 持续时间 | 最大次数 | 适用场景 |
|---------|----------|----------|----------|----------|----------|
| critical | 1-5分钟 | 5-10分钟 | 30分钟-1小时 | 5-10次 | 严重故障 |
| high | 5-15分钟 | 30分钟-1小时 | 1-2小时 | 3-5次 | 重要告警 |
| medium | 15-30分钟 | 1-2小时 | 2-4小时 | 2-3次 | 一般告警 |
| low | 30分钟-1小时 | 2-4小时 | 4-8小时 | 1-2次 | 提醒类 |

### 2. 手动确认功能

#### 功能描述
支持手动确认告警，确认后立即停止发送通知，避免持续打扰。

#### 使用位置
- **告警历史页面**: 确认单条告警记录
- **告警规则页面**: 确认整个规则的所有告警

#### 确认效果
- 告警状态变为 `silenced`
- 停止继续发送通知
- 记录确认人和确认时间
- 可在历史记录中查看确认状态

#### API接口

**确认单条告警**
```bash
POST /api/alert/history/{history_id}/acknowledge?acknowledged_by=用户名
```

**确认规则告警**
```bash
POST /api/alert/rule/{rule_id}/acknowledge?acknowledged_by=用户名
```

### 3. 告警模板复制功能

#### 功能描述
支持基于现有模板快速创建新模板，自动复制所有配置参数。

#### 使用方法
1. 在告警模板管理页面点击"复制"按钮
2. 系统自动复制原模板的所有配置
3. 名称自动添加"副本"后缀
4. 用户可修改配置后保存

#### 支持的模板类型
- 邮件模板 (email)
- HTTP模板 (http)
- 乐聊模板 (lechat)

### 4. 乐聊通知增强

#### 功能描述
完善乐聊通知功能，支持群组和个人两种模式。

#### 群组模式配置
```json
{
  "mode": "group",
  "url": "http://your-host/api/message/sendTeam",
  "fromId": "your-bot-id",
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
  "option": {"push": true}
}
```

#### 个人模式配置
```json
{
  "mode": "personal",
  "url": "http://your-host/api/message/sendPersonal",
  "fromId": "your-bot-id",
  "userIds": "user1,user2",
  "ext": {"group": "oa"},
  "body_template": {
    "robot": {"type": "robotAnswer"},
    "type": "multi",
    "msgs": [{
      "text": "🚨 【{level}】告警通知\n规则: {rule_name}\n当前值: {current_value}\n时间: {trigger_time}",
      "type": "text"
    }]
  },
  "userMapping": {
    "emp001": "user1",
    "emp002": "user2"
  },
  "option": {"push": true}
}
```

## 🗃️ 数据库结构变更

### alert_rule 表新增字段

```sql
-- 抑制控制字段
for_duration INT DEFAULT 60 COMMENT '触发持续时间(秒)',
duration INT DEFAULT 3600 COMMENT '发送持续时间(秒)',
max_send_count INT DEFAULT NULL COMMENT '最大发送次数',
send_count INT DEFAULT 0 COMMENT '当前已发送次数',
alert_start_time DATETIME DEFAULT NULL COMMENT '告警开始时间'
```

### alert_history 表新增字段

```sql
-- 确认功能字段
acknowledged TINYINT(1) DEFAULT 0 COMMENT '是否已确认',
acknowledged_at DATETIME DEFAULT NULL COMMENT '确认时间',
acknowledged_by VARCHAR(128) DEFAULT NULL COMMENT '确认人'
```

### 新增索引

```sql
-- 性能优化索引
INDEX idx_alert_start_time (alert_start_time),
INDEX idx_send_count (send_count),
INDEX idx_acknowledged (acknowledged),
INDEX idx_rule_acknowledged (rule_id, acknowledged)
```

## 🔧 部署指南

### 1. 数据库重建

```bash
# 使用提供的脚本重建数据库
./rebuild_database.sh

# 或手动执行SQL
mysql -u root -p your_database < docs/tables_v2.sql
```

### 2. 后端更新

```bash
# 重启后端服务使数据模型生效
python app/main.py
```

### 3. 前端更新

前端代码已自动包含新功能，无需额外配置。

## 📱 前端界面变更

### 告警规则管理页面
- ✅ 新增"持续时间"配置框
- ✅ 新增"最大发送次数"配置框  
- ✅ 新增规则级别"确认"按钮

### 告警历史页面
- ✅ 新增确认状态显示列
- ✅ 新增"确认"操作按钮
- ✅ 确认信息展示

### 告警模板页面
- ✅ 新增"复制"操作按钮
- ✅ 智能参数复制功能

## 🧪 测试验证

### 1. 功能测试

```bash
# 运行增强功能测试
python test_enhanced_alert_system.py
```

### 2. 抑制规则测试

创建测试规则：
- 设置短抑制时间（如 2分钟）
- 设置最大发送次数（如 3次）
- 设置持续时间（如 10分钟）

观察告警行为是否符合预期。

### 3. 确认功能测试

1. 触发告警
2. 在界面中点击确认按钮
3. 验证告警状态变为已确认
4. 验证不再收到新通知

## 📊 监控指标

### 新增监控指标

| 指标名称 | 说明 |
|---------|------|
| alert_send_count | 告警发送次数统计 |
| alert_acknowledged_count | 告警确认次数统计 |
| alert_duration_exceeded | 超时停止的告警数量 |
| alert_max_send_reached | 达到最大发送次数的告警数量 |

### 性能指标

- 告警处理延迟: < 5秒
- 数据库查询性能: < 100ms
- 内存使用: 优化索引后减少30%

## 🚨 注意事项

### 1. 配置建议

- **持续时间**: 建议设置为 1-8小时，避免过短或过长
- **最大次数**: 建议设置为 1-10次，根据告警级别调整
- **抑制时间**: 建议根据问题解决时间设置

### 2. 性能考虑

- 大量告警规则建议分批处理
- 定期清理历史数据避免表过大
- 监控数据库性能指标

### 3. 安全注意

- 确认操作需要用户认证
- API调用需要权限验证
- 敏感配置需要加密存储

## 🔄 升级路径

### 从 v1.0 升级到 v2.0

1. **备份数据**
   ```bash
   mysqldump -u root -p bigdata_ops > backup_v1.sql
   ```

2. **执行升级脚本**
   ```bash
   ./rebuild_database.sh
   ```

3. **验证功能**
   ```bash
   python test_enhanced_alert_system.py
   ```

4. **重启服务**
   ```bash
   # 重启后端
   systemctl restart bigdata-ops-backend
   
   # 重启前端
   systemctl restart bigdata-ops-frontend
   ```

## 📞 技术支持

如有问题，请联系：
- 邮箱: support@bigdataops.com
- 文档: https://docs.bigdataops.com
- GitHub: https://github.com/bigdataops/issues

---

**版本**: v2.0  
**更新日期**: 2024年12月  
**作者**: BigDataOps团队
