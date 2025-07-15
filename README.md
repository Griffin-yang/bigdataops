# BigDataOps - 大数据运维监控平台

BigDataOps 是一个综合性的开源大数据运维监控平台，提供集群监控、业务监控、告警管理、用户管理等功能。

## 🚀 功能特性

- **集群监控**: 支持 CDH 和 Apache 开源集群监控
- **业务监控**: 监控 Azkaban 和 DolphinScheduler 任务执行
- **告警系统**: 灵活的告警规则和多种通知方式
- **用户管理**: LDAP 集成用户认证和权限管理
- **可视化界面**: 现代化的 Vue.js 前端界面

## 📋 系统要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- LDAP 服务器（可选）

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd BigDataOps
```

### 2. 配置环境

复制配置模板并修改：

```bash
cp config/config.template.env config/config.env
```

编辑 `config/config.env` 文件，根据你的环境修改配置：

```bash
# 环境标识
ENVIRONMENT=development

# 数据库配置
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=alert

# LDAP配置
LDAP_SERVER=ldap://your_ldap_server:389
LDAP_USER=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your_ldap_password
```

### 3. 安装依赖

#### 后端依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd frontend/bigdata-frontend
npm install
```

### 4. 初始化数据库

```bash
# 重建数据库（可选）
./rebuild_database.sh
```

### 5. 启动服务

#### 启动后端

```bash
./start_backend.sh
```

#### 启动前端

```bash
./start_frontend.sh
```

### 6. 访问系统

- 前端地址: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
BigDataOps/
├── app/                    # 后端应用
│   ├── alert/             # 告警模块
│   ├── business/          # 业务监控模块
│   ├── cluster/           # 集群监控模块
│   ├── ldap/              # LDAP认证模块
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── config/                # 配置文件
│   ├── config.template.env # 配置模板
│   └── config.env         # 实际配置（需手动创建）
├── frontend/              # 前端应用
│   └── bigdata-frontend/  # Vue.js前端
├── docs/                  # 文档
├── scripts/               # 脚本文件
└── requirements.txt       # Python依赖
```

## ⚙️ 配置管理

BigDataOps 使用统一的配置文件管理所有环境配置。详细配置说明请参考 [配置指南](docs/configuration_guide.md)。

### 主要配置项

- **环境配置**: 开发、测试、生产环境标识
- **数据库配置**: MySQL 连接参数
- **LDAP配置**: 用户认证服务器配置
- **监控配置**: Prometheus、Azkaban、DolphinScheduler 配置
- **告警配置**: 告警引擎和通知配置

### 配置优先级

1. 环境变量
2. 配置文件 (`config/config.env`)
3. 默认值

## 📚 文档

- [配置指南](docs/configuration_guide.md) - 详细的配置说明
- [API参考](docs/api_reference.md) - API接口文档
- [告警系统指南](docs/alert_system_guide.md) - 告警功能使用指南
- [集群监控指南](docs/cluster_monitoring_guide.md) - 集群监控功能说明
- [业务监控指南](docs/business_monitoring_guide.md) - 业务监控功能说明
- [用户管理指南](docs/user_management_guide.md) - 用户管理功能说明

## 🔧 开发指南

### 后端开发

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend/bigdata-frontend

# 启动开发服务器
npm run dev
```

### 代码规范

- 后端使用 Python 类型注解
- 前端使用 TypeScript
- 遵循 PEP 8 和 ESLint 规范

## 🐛 故障排除

### 常见问题

1. **配置文件加载失败**
   - 检查 `config/config.env` 文件是否存在
   - 验证配置文件格式是否正确

2. **数据库连接失败**
   - 检查 MySQL 服务状态
   - 验证数据库配置参数

3. **LDAP连接失败**
   - 检查 LDAP 服务器状态
   - 验证 LDAP 配置参数

### 日志查看

```bash
# 查看后端日志
tail -f logs/bigdataops.log

# 查看前端日志
cd frontend/bigdata-frontend
npm run build
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

---

**版本**: v2.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps开发团队 