# BigDataOps 大数据运维管理平台

## 📋 项目概述

BigDataOps 是一个企业级大数据运维管理平台，提供集群监控、业务监控、告警管理和用户管理等核心功能。基于现代化的技术栈构建，支持多种大数据组件和调度系统的统一管理。

## 🚀 核心功能

### 🚨 告警系统
- **智能告警规则**: 基于PromQL的灵活告警规则配置
- **多渠道通知**: 支持邮件、HTTP Webhook、乐聊等通知方式
- **告警抑制**: 防止告警风暴，提供多维度抑制控制
- **手动确认**: 支持告警确认和手动解决
- **历史追踪**: 完整的告警历史记录和查询

### 📊 集群监控
- **实时监控**: 集群节点和大数据组件的实时状态监控
- **健康管理**: 自动检测系统健康状况，及时发现潜在问题
- **资源优化**: 监控资源使用情况，辅助资源调优决策
- **可视化展示**: 直观的图表和仪表盘展示监控数据

### 📈 业务监控
- **统一监控**: 支持多种调度系统的统一监控界面
- **实时统计**: 提供任务执行情况的实时统计和分析
- **失败分析**: 详细的失败任务分析和错误信息展示
- **性能优化**: 执行时间排行榜和性能优化建议

### 👥 用户管理
- **统一认证**: 基于LDAP的统一用户认证系统
- **组织管理**: 支持用户组和权限管理
- **批量操作**: 支持批量用户和组操作
- **安全控制**: 提供细粒度的访问控制

## 🏗️ 技术架构

### 前端技术栈
- **Vue 3**: 现代化的前端框架
- **Element Plus**: 企业级UI组件库
- **ECharts**: 数据可视化图表库
- **TypeScript**: 类型安全的JavaScript

### 后端技术栈
- **FastAPI**: 高性能Python Web框架
- **SQLAlchemy**: Python ORM框架
- **Prometheus**: 监控数据收集和存储
- **LDAP**: 用户目录服务

### 数据库
- **MySQL**: 主数据库
- **Prometheus**: 时序数据库
- **LDAP**: 用户目录数据库

## 📚 文档结构

### 核心文档
- [`docs/database_schema.sql`](docs/database_schema.sql) - 数据库建表语句
- [`docs/api_reference.md`](docs/api_reference.md) - API接口参考文档

### 功能模块文档
- [`docs/alert_system_guide.md`](docs/alert_system_guide.md) - 告警系统完整指南
- [`docs/cluster_monitoring_guide.md`](docs/cluster_monitoring_guide.md) - 集群监控完整指南
- [`docs/business_monitoring_guide.md`](docs/business_monitoring_guide.md) - 业务监控完整指南
- [`docs/user_management_guide.md`](docs/user_management_guide.md) - 用户管理完整指南

### 配置文档
- [`docs/tables.sql`](docs/tables.sql) - 数据库表结构说明

## 🛠️ 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Prometheus 2.0+

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-org/bigdata-ops.git
cd bigdata-ops
```

#### 2. 后端环境配置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、Prometheus等连接信息

# 初始化数据库
python scripts/init_db.py
```

#### 3. 前端环境配置
```bash
cd frontend/bigdata-frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置API地址等

# 启动开发服务器
npm run dev
```

#### 4. 启动服务
```bash
# 启动后端服务
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务（新终端）
cd frontend/bigdata-frontend
npm run dev
```

### 访问系统
- 前端地址: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📖 使用指南

### 告警系统使用
1. 配置告警规则：在"告警管理"页面创建和配置告警规则
2. 设置通知模板：配置邮件、HTTP或乐聊通知模板
3. 启动告警引擎：启动告警引擎开始监控
4. 查看告警历史：在"告警历史"页面查看告警记录

### 集群监控使用
1. 访问监控仪表盘：查看集群整体健康状态
2. 集群总览：查看节点状态和资源使用情况
3. 组件监控：查看各大数据组件的运行状态
4. 健康检查：定期检查集群健康状况

### 业务监控使用
1. 选择集群：选择要监控的集群（CDH或Apache）
2. 设置时间范围：选择查询的时间范围
3. 查看业务概览：查看任务执行统计信息
4. 分析失败任务：查看失败任务列表和错误信息
5. 性能分析：查看执行时间排行榜

### 用户管理使用
1. 环境选择：选择要管理的环境（生产/测试/开发）
2. 用户管理：查询、创建、修改、删除用户
3. 组管理：查询、创建、修改、删除用户组
4. 权限管理：分配和回收用户权限

## 🔧 配置说明

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bigdataops

# Prometheus配置
PROMETHEUS_URL=http://localhost:9090

# LDAP配置
LDAP_SERVER=ldap://your-ldap-server:389
LDAP_USER=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your-ldap-password

# 邮件配置
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=alert@example.com
SMTP_PASSWORD=your-smtp-password
```

### 告警规则配置
告警规则支持以下配置：
- **PromQL表达式**: 监控指标查询表达式
- **告警条件**: 触发告警的条件（如 > 80）
- **告警等级**: critical、warning、info
- **抑制时间**: 告警抑制的时间间隔
- **重复间隔**: 告警重复发送的时间间隔

### 通知模板配置
支持三种通知方式：
- **邮件通知**: SMTP邮件发送
- **HTTP通知**: Webhook回调
- **乐聊通知**: 乐聊群组消息

## 🚀 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t bigdataops .

# 运行容器
docker run -d -p 8000:8000 --name bigdataops bigdataops
```

### Kubernetes部署
```bash
# 应用配置
kubectl apply -f k8s/

# 查看状态
kubectl get pods -n bigdataops
```

## 🔍 故障排查

### 常见问题
1. **数据库连接失败**: 检查数据库配置和网络连通性
2. **Prometheus连接失败**: 检查Prometheus服务状态和配置
3. **LDAP连接失败**: 检查LDAP服务器状态和认证信息
4. **告警不发送**: 检查告警引擎状态和通知模板配置

### 日志查看
```bash
# 后端日志
tail -f logs/bigdataops.log

# 前端日志
# 在浏览器开发者工具中查看
```

### 调试工具
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 指标监控: http://localhost:8000/metrics

## 🤝 贡献指南

### 开发环境设置
1. Fork项目到你的GitHub账户
2. 克隆你的Fork到本地
3. 创建功能分支: `git checkout -b feature/your-feature`
4. 提交更改: `git commit -am 'Add some feature'`
5. 推送分支: `git push origin feature/your-feature`
6. 创建Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用TypeScript进行前端开发
- 编写单元测试和集成测试
- 更新相关文档

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目维护**: BigDataOps开发团队
- **邮箱**: bigdataops@example.com
- **问题反馈**: [GitHub Issues](https://github.com/your-org/bigdata-ops/issues)

## 📈 更新日志

### v2.0 (2024-01-15)
- ✅ 重构文档结构，按功能模块组织
- ✅ 优化告警系统，支持多种通知方式
- ✅ 增强集群监控，支持组件状态监控
- ✅ 完善业务监控，支持多调度系统
- ✅ 改进用户管理，支持LDAP集成
- ✅ 统一API接口，提供完整API文档

### v1.0 (2024-01-01)
- ✅ 基础告警功能
- ✅ 集群监控功能
- ✅ 业务监控功能
- ✅ 用户管理功能

---

**版本**: v2.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps开发团队

如有问题或建议，请联系开发团队或提交Issue。 