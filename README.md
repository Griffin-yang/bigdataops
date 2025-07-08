# BigDataOps 大数据运维管理平台

基于FastAPI、Vue3、Element Plus开发的企业级大数据运维管理平台，提供告警系统、用户管理、集群监控等功能。

## 🚀 技术栈

### 后端
- **FastAPI** - 现代化的Python Web框架
- **SQLAlchemy** - Python ORM框架  
- **Pydantic** - 数据验证和序列化
- **APScheduler** - 任务调度系统
- **MySQL/SQLite** - 关系型数据库
- **Requests** - HTTP客户端库

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue3 UI组件库
- **ECharts** - 数据可视化图表库
- **Vite** - 现代化前端构建工具
- **Pinia** - Vue3状态管理

## 📋 功能特性

### 1. 🚨 智能告警系统
- ✅ **多样化告警规则**: 支持PromQL表达式，灵活配置告警条件
- ✅ **增强抑制策略**: 持续时间控制、发送次数限制、每日重置
- ✅ **多通知渠道**: 邮件、HTTP Webhook、乐聊（群组/个人）
- ✅ **手动确认机制**: 支持确认告警，立即停止通知
- ✅ **模板复制功能**: 基于现有模板快速创建新模板
- ✅ **规则复制功能**: 一键复制规则配置，提高配置效率
- ✅ **实时引擎控制**: 启动/停止/测试告警引擎
- ✅ **告警历史追踪**: 完整的告警记录和查询
- ✅ **组件分类管理**: 按HDFS、Hive、Spark等组件分类管理

### 2. 👥 LDAP用户管理
- ✅ **用户管理**: 创建、查询、修改用户信息
- ✅ **组管理**: 创建、查询、修改用户组
- ✅ **权限管理**: 用户组权限分配
- ✅ **批量操作**: 支持批量用户和组操作

### 3. 📊 集群监控
- ✅ **多组件支持**: HDFS、Hive、Spark、MySQL、Kafka等
- ✅ **实时状态监控**: CPU、内存、磁盘使用率
- ✅ **可视化图表**: ECharts数据可视化
- ✅ **健康检查**: 服务健康状态检测

### 4. 🎨 现代化前端界面
- ✅ **响应式设计**: 适配各种屏幕尺寸
- ✅ **直观操作**: 统一的用户体验
- ✅ **实时更新**: 数据实时刷新
- ✅ **主题支持**: 现代化UI设计
- ✅ **表单优化**: 智能表单验证和提示

## 🛠️ 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+ 或 SQLite

### 一键启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd BigDataOps

# 2. 启动后端（自动创建虚拟环境和安装依赖）
./start_backend.sh

# 3. 启动前端（自动安装依赖）
./start_frontend.sh
```

### 手动启动
```bash
# 后端启动
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端启动
cd frontend/bigdata-frontend
npm install
npm run dev
```

### 数据库初始化
```bash
# 重建数据库（包含增强功能）
./rebuild_database.sh
```

### 访问地址
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000  
- **API文档**: http://localhost:8000/docs
- **默认登录**: admin / admin

## 📊 系统架构

```
BigDataOps/
├── app/                    # 后端应用
│   ├── alert/             # 告警模块
│   │   ├── controllers/   # 控制器
│   │   ├── services/      # 业务逻辑
│   │   ├── downstream/    # 下游通知
│   │   └── sql/          # SQL脚本
│   ├── ldap/             # LDAP模块
│   ├── models/           # 数据模型
│   ├── utils/            # 工具函数
│   └── main.py           # 应用入口
├── frontend/              # 前端应用
│   └── bigdata-frontend/  # Vue3项目
│       ├── src/
│       │   ├── views/     # 页面组件
│       │   ├── utils/     # 工具函数
│       │   └── router/    # 路由配置
│       └── package.json
├── docs/                 # 文档
├── start_backend.sh      # 后端启动脚本
├── start_frontend.sh     # 前端启动脚本
└── requirements.txt      # Python依赖
```

## 🔧 配置说明

### 告警模板配置

#### 邮件模板示例
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
    "subject_template": "【{level}】{rule_name} 告警",
    "content_template": "<h2>{rule_name}</h2><p>当前值: {current_value}</p>"
  }
}
```

#### HTTP模板示例  
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
      "value": "{current_value}"
    }
  }
}
```

### 告警规则配置
```json
{
  "name": "CPU使用率告警",
  "promql": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
  "condition": "> 80",
  "level": "critical",
  "repeat": 300,
  "enabled": true,
  "notify_template_id": 1
}
```

## 🧪 测试

### 后端测试
```bash
# 运行完整功能测试
python test_alert_system.py
```

### 手动测试API
```bash
# 健康检查
curl http://localhost:8000/health

# 获取告警规则
curl http://localhost:8000/alert/rule

# 获取告警模板  
curl http://localhost:8000/alert/notify_template
```

## 📝 开发说明

### 后端开发
- 基于FastAPI框架，采用模块化设计
- 使用SQLAlchemy ORM，支持多种数据库
- 统一的接口返回格式：`{"code": 0/1, "data": xxx, "msg": "描述"}`
- 完整的日志记录和异常处理

### 前端开发
- 采用Vue3 Composition API
- TypeScript类型安全
- Element Plus组件库
- 统一的API请求封装
- 响应式设计支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## �� 许可证

MIT License 