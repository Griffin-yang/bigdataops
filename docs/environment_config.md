# 环境变量配置指南

## 业务监控配置

业务监控模块需要配置调度系统的连接参数。可以通过环境变量或`.env`文件进行配置。

### CDH集群配置

#### Azkaban配置
```bash
AZKABAN_HOST=your-azkaban-server.com
AZKABAN_PORT=8443
AZKABAN_USERNAME=admin
AZKABAN_PASSWORD=your-password
```

#### DolphinScheduler配置
```bash
CDH_DS_HOST=your-cdh-ds-server.com
CDH_DS_PORT=3306
CDH_DS_DATABASE=dolphinscheduler
CDH_DS_USERNAME=ds_user
CDH_DS_PASSWORD=your-password
```

### Apache集群配置

#### DolphinScheduler配置
```bash
APACHE_DS_HOST=your-apache-ds-server.com
APACHE_DS_PORT=3306
APACHE_DS_DATABASE=dolphinscheduler
APACHE_DS_USERNAME=ds_user
APACHE_DS_PASSWORD=your-password
```

### 其他系统配置

```bash
# Prometheus配置
PROMETHEUS_URL=http://your-prometheus-server:9090

# MySQL数据库配置
MYSQL_HOST=your-mysql-server.com
MYSQL_USER=your-user
MYSQL_PASSWORD=your-password
MYSQL_DB=alert

# LDAP配置
LDAP_SERVER=ldap://your-ldap-server:389
LDAP_USER=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your-ldap-password
LDAP_BASE_DN=ou=People,dc=example,dc=com
LDAP_GROUP_DN=ou=Group,dc=example,dc=com
```

## 配置方式

### 方式1：环境变量
直接设置系统环境变量：

```bash
export AZKABAN_HOST=your-azkaban-server.com
export AZKABAN_PORT=8443
# ... 其他配置
```

### 方式2：.env文件
在项目根目录创建`.env`文件：

```bash
# .env文件示例
AZKABAN_HOST=your-azkaban-server.com
AZKABAN_PORT=8443
AZKABAN_USERNAME=admin
AZKABAN_PASSWORD=your-password

CDH_DS_HOST=your-cdh-ds-server.com
CDH_DS_PORT=3306
CDH_DS_DATABASE=dolphinscheduler
CDH_DS_USERNAME=ds_user
CDH_DS_PASSWORD=your-password

APACHE_DS_HOST=your-apache-ds-server.com
APACHE_DS_PORT=3306
APACHE_DS_DATABASE=dolphinscheduler
APACHE_DS_USERNAME=ds_user
APACHE_DS_PASSWORD=your-password
```

## 配置验证

启动服务后，可以通过以下方式验证配置：

1. 查看服务启动日志
2. 访问业务监控页面测试集群连接
3. 检查API接口是否正常返回数据

## 安全建议

1. **密码保护**: 不要在代码中硬编码密码
2. **权限最小化**: 使用只读权限的数据库用户
3. **网络安全**: 确保数据库连接使用安全的网络
4. **定期更新**: 定期更换密码和访问密钥

## 故障排查

### 连接失败
- 检查网络连通性
- 验证主机名和端口
- 确认用户名密码正确

### 权限错误
- 确认数据库用户有足够权限
- 检查数据库和表是否存在
- 验证API访问权限

### 配置不生效
- 确认环境变量正确设置
- 检查.env文件格式
- 重启服务使配置生效 