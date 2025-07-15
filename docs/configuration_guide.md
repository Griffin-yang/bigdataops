# BigDataOps 配置指南

## 概述

BigDataOps 使用统一的配置文件管理所有环境配置。通过修改 `config/config.env` 文件来配置不同环境的参数。

## 配置文件结构

```
config/
├── config.template.env    # 配置模板文件
└── config.env            # 实际配置文件（需要手动创建）
```

## 快速开始

### 1. 创建配置文件

复制模板文件并重命名：

```bash
cp config/config.template.env config/config.env
```

### 2. 修改配置

编辑 `config/config.env` 文件，根据你的环境修改相应配置：

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

### 3. 启动服务

使用你的启动脚本启动服务：

```bash
./start_backend.sh
```

## 配置项说明

### 环境配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 环境标识 | `development` |

### LDAP 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LDAP_SERVER` | LDAP服务器地址 | `ldap://localhost:389` |
| `LDAP_USER` | LDAP管理员用户 | `cn=admin,dc=example,dc=com` |
| `LDAP_PASSWORD` | LDAP管理员密码 | `admin123` |
| `LDAP_BASE_DN` | LDAP基础DN | `ou=People,dc=example,dc=com` |
| `LDAP_GROUP_DN` | LDAP组DN | `ou=Group,dc=example,dc=com` |

### Prometheus 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PROMETHEUS_URL` | Prometheus服务地址 | `http://localhost:9090/` |

### MySQL 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MYSQL_HOST` | MySQL主机地址 | `localhost` |
| `MYSQL_PORT` | MySQL端口 | `3306` |
| `MYSQL_USER` | MySQL用户名 | `root` |
| `MYSQL_PASSWORD` | MySQL密码 | `123456` |
| `MYSQL_DB` | MySQL数据库名 | `alert` |

### 服务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `UVICORN_HOST` | 服务监听地址 | `0.0.0.0` |
| `UVICORN_PORT` | 服务监听端口 | `8000` |
| `UVICORN_RELOAD` | 是否启用热重载 | `true` |
| `ALERT_ENGINE_INTERVAL` | 告警引擎检查间隔(秒) | `30` |

### 业务监控配置

#### CDH集群 - Azkaban

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `AZKABAN_HOST` | Azkaban主机 | `localhost` |
| `AZKABAN_PORT` | Azkaban端口 | `8081` |
| `AZKABAN_USERNAME` | Azkaban用户名 | `azkaban` |
| `AZKABAN_PASSWORD` | Azkaban密码 | `azkaban` |
| `AZKABAN_WEB_URL` | Azkaban Web地址 | `http://localhost:8081` |

#### CDH集群 - Azkaban数据库

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `AZKABAN_DB_HOST` | Azkaban数据库主机 | `localhost` |
| `AZKABAN_DB_PORT` | Azkaban数据库端口 | `3306` |
| `AZKABAN_DB_DATABASE` | Azkaban数据库名 | `azkaban` |
| `AZKABAN_DB_USERNAME` | Azkaban数据库用户名 | `root` |
| `AZKABAN_DB_PASSWORD` | Azkaban数据库密码 | `123456` |

#### CDH集群 - DolphinScheduler

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `CDH_DS_HOST` | CDH DolphinScheduler主机 | `localhost` |
| `CDH_DS_PORT` | CDH DolphinScheduler端口 | `3306` |
| `CDH_DS_DATABASE` | CDH DolphinScheduler数据库 | `dolphinscheduler` |
| `CDH_DS_USERNAME` | CDH DolphinScheduler用户名 | `root` |
| `CDH_DS_PASSWORD` | CDH DolphinScheduler密码 | `123456` |
| `CDH_DS_WEB_URL` | CDH DolphinScheduler Web地址 | `http://localhost:12345/dolphinscheduler` |

#### Apache集群 - DolphinScheduler

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `APACHE_DS_HOST` | Apache DolphinScheduler主机 | `localhost` |
| `APACHE_DS_PORT` | Apache DolphinScheduler端口 | `3306` |
| `APACHE_DS_DATABASE` | Apache DolphinScheduler数据库 | `dolphinscheduler_apache` |
| `APACHE_DS_USERNAME` | Apache DolphinScheduler用户名 | `root` |
| `APACHE_DS_PASSWORD` | Apache DolphinScheduler密码 | `123456` |
| `APACHE_DS_WEB_URL` | Apache DolphinScheduler Web地址 | `http://localhost:22345/dolphinscheduler` |

#### 业务监控通用配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `BUSINESS_MONITORING_ENABLED` | 是否启用业务监控 | `true` |
| `DEFAULT_QUERY_DAYS` | 默认查询天数 | `1` |
| `MAX_FAILED_JOBS_DISPLAY` | 最大失败任务显示数量 | `100` |
| `MAX_DURATION_JOBS_DISPLAY` | 最大执行时间任务显示数量 | `50` |

## 环境配置示例

### 开发环境配置

```bash
ENVIRONMENT=development
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=123456
LDAP_SERVER=ldap://localhost:389
PROMETHEUS_URL=http://localhost:9090/
```

### 测试环境配置

```bash
ENVIRONMENT=test
MYSQL_HOST=test-db.example.com
MYSQL_USER=bigdataops_test
MYSQL_PASSWORD=test_password
LDAP_SERVER=ldap://test-ldap.example.com:389
PROMETHEUS_URL=http://test-prometheus.example.com:9090/
```

### 生产环境配置

```bash
ENVIRONMENT=production
MYSQL_HOST=prod-db.example.com
MYSQL_USER=bigdataops_prod
MYSQL_PASSWORD=prod_password
LDAP_SERVER=ldap://prod-ldap.example.com:389
PROMETHEUS_URL=http://prod-prometheus.example.com:9090/
```

## 配置优先级

配置加载优先级（从高到低）：

1. **环境变量** - 系统环境变量
2. **配置文件** - `config/config.env` 文件
3. **默认值** - 代码中的默认配置

## 注意事项

1. **安全性**: 生产环境中请使用强密码，并确保配置文件权限设置正确
2. **备份**: 修改配置前请备份原配置文件
3. **验证**: 修改配置后请重启服务以确保配置生效
4. **模板**: 不要直接修改 `config.template.env` 文件，应该复制后修改 `config.env`

## 故障排除

### 配置文件加载失败

如果配置文件加载失败，系统会使用默认配置并显示警告信息。检查：

1. 配置文件是否存在
2. 配置文件格式是否正确
3. 文件权限是否正确

### 配置不生效

如果配置修改后不生效：

1. 重启服务
2. 检查配置文件语法
3. 确认配置项名称正确 