# 业务监控配置说明

## 概述

业务监控功能支持监控两种集群：
- **CDH集群**: 同时支持Azkaban和DolphinScheduler调度器
- **Apache开源集群**: 仅支持DolphinScheduler调度器

## 配置参数详解

### 1. CDH集群 - Azkaban配置

```python
# Azkaban调度器配置
azkaban_host: str = "172.16.3.233"              # Azkaban服务器地址
azkaban_port: int = 34006                       # Azkaban API端口
azkaban_web_port: int = 34006                   # Azkaban Web端口
azkaban_username: str = "admin"                 # Azkaban登录用户名
azkaban_password: str = "password"              # Azkaban登录密码
azkaban_web_url: str = "http://172.16.3.233:34006"  # Azkaban Web界面完整地址
```

**说明**:
- `azkaban_host`: Azkaban服务器IP或域名
- `azkaban_port`: Azkaban API服务端口，通常与Web端口相同
- `azkaban_username/password`: 用于API登录的用户凭据
- `azkaban_web_url`: 用于构建任务详情查看链接

### 2. CDH集群 - DolphinScheduler配置

```python
# CDH DolphinScheduler数据库配置
cdh_ds_host: str = "172.16.3.233"              # DS数据库服务器地址
cdh_ds_port: int = 3306                         # MySQL端口
cdh_ds_database: str = "dolphinscheduler"       # DS数据库名
cdh_ds_username: str = "root"                   # 数据库用户名
cdh_ds_password: str = "password123"            # 数据库密码
cdh_ds_web_url: str = "http://172.16.3.233:12345/dolphinscheduler"  # DS Web界面地址
```

**说明**:
- DS数据主要通过直连MySQL数据库查询获取
- `cdh_ds_web_url`: 用于构建任务详情查看链接

### 3. Apache开源集群 - DolphinScheduler配置

```python
# Apache DolphinScheduler数据库配置
apache_ds_host: str = "172.16.3.233"           # DS数据库服务器地址
apache_ds_port: int = 3306                      # MySQL端口
apache_ds_database: str = "dolphinscheduler_apache"  # DS数据库名（区别于CDH）
apache_ds_username: str = "root"                # 数据库用户名
apache_ds_password: str = "password123"         # 数据库密码
apache_ds_web_url: str = "http://172.16.3.233:12346/dolphinscheduler"  # DS Web界面地址
```

**说明**:
- Apache集群与CDH集群使用不同的数据库实例
- Web端口通常也不同，避免冲突

### 4. 业务监控通用配置

```python
# 通用配置
business_monitoring_enabled: bool = True        # 是否启用业务监控功能
default_query_days: int = 1                    # 默认查询天数
max_failed_jobs_display: int = 100             # 最大失败任务显示数量
max_duration_jobs_display: int = 50            # 最大执行时间排行显示数量
```

## 数据库表结构要求

### DolphinScheduler必需表
- `t_ds_process_instance`: 工作流实例表（主要数据源）
- `t_ds_process_definition`: 工作流定义表
- `t_ds_project`: 项目表

### 关键字段说明
- `state`: 任务状态（7=成功, 6=失败, 9=被杀死, 10=停止）
- `start_time/end_time`: 执行开始/结束时间
- `process_definition_id`: 关联工作流定义
- `project_id`: 关联项目

## 环境变量配置

可以通过环境变量覆盖默认配置：

```bash
# Azkaban配置
export AZKABAN_HOST="your-azkaban-host"
export AZKABAN_PORT="34006"
export AZKABAN_USERNAME="admin"
export AZKABAN_PASSWORD="your-password"

# CDH DolphinScheduler配置
export CDH_DS_HOST="your-cdh-ds-host"
export CDH_DS_PORT="3306"
export CDH_DS_DATABASE="dolphinscheduler"
export CDH_DS_USERNAME="root"
export CDH_DS_PASSWORD="your-password"

# Apache DolphinScheduler配置
export APACHE_DS_HOST="your-apache-ds-host"
export APACHE_DS_PORT="3306"
export APACHE_DS_DATABASE="dolphinscheduler_apache"
export APACHE_DS_USERNAME="root"
export APACHE_DS_PASSWORD="your-password"
```

## 网络访问要求

### 端口开放要求
- **Azkaban**: 需要开放API端口（通常与Web端口相同）
- **MySQL**: 需要开放3306端口或自定义MySQL端口
- **DolphinScheduler Web**: 需要开放Web界面端口

### 访问权限要求
- **Azkaban**: 需要具有项目查看权限的用户账号
- **MySQL**: 需要具有数据库读取权限的用户账号
- **网络**: 应用服务器需要能访问以上所有服务

## 配置验证

### 1. 测试数据库连接
```bash
# 测试MySQL连接
mysql -h {host} -P {port} -u {username} -p{password} -e "SELECT 1"
```

### 2. 测试Azkaban API
```bash
# 测试Azkaban登录
curl -X POST "http://{host}:{port}/" \
  -d "action=login&username={username}&password={password}"
```

### 3. 验证Web访问
- 访问Azkaban Web界面：`http://{azkaban_host}:{azkaban_port}`
- 访问DolphinScheduler Web界面：`http://{ds_host}:{ds_web_port}/dolphinscheduler`

## 常见问题

### 1. 连接超时
- 检查防火墙和安全组设置
- 确认服务端口是否正确开放

### 2. 认证失败
- 检查用户名密码是否正确
- 确认数据库用户权限是否足够

### 3. 数据为空
- 检查时间范围是否正确
- 确认数据库中是否有对应时间段的数据
- 检查表结构是否与预期一致

## 生产环境建议

1. **安全性**:
   - 使用环境变量或密钥管理系统存储密码
   - 创建专用的只读数据库用户
   - 限制网络访问范围

2. **性能**:
   - 配置数据库连接池
   - 添加适当的数据库索引
   - 设置合理的查询超时时间

3. **监控**:
   - 监控数据库连接状态
   - 记录API调用日志
   - 设置告警机制 