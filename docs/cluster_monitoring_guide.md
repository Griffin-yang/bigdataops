# 集群监控模块完整指南

## 📋 目录
- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [核心功能](#核心功能)
- [操作指南](#操作指南)
- [配置说明](#配置说明)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

## 🎯 系统概述

BigDataOps集群监控系统是一个基于Prometheus的大数据集群监控解决方案，提供实时监控、健康检查、资源管理和可视化展示功能。

### 设计目标
- **实时监控**: 提供集群节点和大数据组件的实时状态监控
- **健康管理**: 自动检测系统健康状况，及时发现潜在问题
- **资源优化**: 监控资源使用情况，辅助资源调优决策
- **故障预警**: 基于监控数据提供智能告警和故障预警
- **可视化展示**: 直观的图表和仪表盘展示监控数据

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API   │    │   Prometheus    │
│                 │    │                 │    │                 │
│ - 监控仪表盘    │◄───┤ - 数据聚合      │◄───┤ - 指标收集      │
│ - 集群总览      │    │ - API 服务      │    │ - 数据存储      │
│ - 组件监控      │    │ - 健康检查      │    │ - 规则引擎      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                    ┌─────────────────┐
                    │ Cluster Nodes   │
                    │                 │
                    │ - Node Exporter │
                    │ - JMX Exporter  │
                    │ - 自定义指标    │
                    └─────────────────┘
```

### 核心组件

#### 1. 前端监控界面 (Web Frontend)
- **技术栈**: Vue3 + Element Plus + ECharts
- **职责**: 数据可视化、用户交互、实时更新
- **特点**: 响应式设计、组件化架构、实时数据刷新

#### 2. 后端API服务 (Backend API)
- **技术栈**: FastAPI + SQLAlchemy
- **职责**: 数据聚合、API服务、健康检查
- **特点**: 异步处理、缓存机制、错误处理

#### 3. Prometheus监控系统
- **职责**: 指标收集、数据存储、查询服务
- **特点**: 时序数据库、高效查询、规则引擎

#### 4. 节点监控代理
- **Node Exporter**: 系统级指标收集
- **JMX Exporter**: Java应用指标收集
- **自定义Exporter**: 业务指标收集

### 数据流设计

#### 监控数据流
```
1. 节点指标收集 → 2. Prometheus存储 → 3. API查询聚合 → 4. 前端展示
```

#### 健康检查流
```
1. 定期检查 → 2. 状态评估 → 3. 结果缓存 → 4. 界面更新
```

## ⚙️ 核心功能

### 1. 监控仪表盘

#### 系统健康状态
- **整体健康评估**: 基于多维度指标的综合评估
- **关键指标摘要**: CPU、内存、磁盘使用率总览
- **快速导航**: 便捷访问各监控模块
- **实时更新**: 自动刷新监控数据

#### 仪表盘布局
```
┌─────────────────────────────────────────┐
│ 标题栏：系统健康状态 + 全局刷新按钮      │
├─────────────────────────────────────────┤
│ 关键指标摘要：                          │
│ [集群健康] [CPU使用率] [内存使用率] [组件健康] │
├─────────────────────────────────────────┤
│ 快速导航：                              │
│ [集群总览] [组件监控] [告警管理]        │
├─────────────────────────────────────────┤
│ 系统状态概览：                          │
│ [节点状态分布] [组件状态列表]           │
└─────────────────────────────────────────┘
```

### 2. 集群总览

#### 节点管理
- **节点列表**: 显示所有集群节点的基本信息
- **状态筛选**: 支持按节点状态筛选
- **资源监控**: 实时监控各节点资源使用情况
- **角色分布**: 展示节点角色和服务分布

#### 节点信息字段
- 主机名和IP地址
- 服务角色 (NameNode, DataNode, ResourceManager等)
- 资源使用率 (CPU, 内存, 磁盘)
- 在线状态和运行时间
- 网络流量和负载情况

#### 状态分类
- **健康节点**: 在线且资源使用正常
- **异常节点**: 离线或资源使用异常
- **警告节点**: 资源使用接近阈值

### 3. 组件监控

#### 支持的组件
- **HDFS**: 分布式文件系统
- **YARN**: 资源管理器
- **Spark**: 计算引擎
- **Hive**: 数据仓库
- **Kafka**: 消息队列
- **ZooKeeper**: 协调服务
- **Flink**: 流处理引擎

#### 状态分类
- **健康**: 所有实例正常运行
- **警告**: 部分实例异常
- **异常**: 大部分或全部实例异常
- **未知**: 无法获取状态信息

#### 监控指标
- **服务状态**: 实例运行状态
- **性能指标**: 响应时间、吞吐量
- **资源使用**: CPU、内存、磁盘
- **业务指标**: 任务数量、成功率

### 4. 基于port_status的服务角色查询

#### 功能说明
- 节点的服务角色基于`port_status`指标查询
- 自动解析运行在每个节点上的具体服务组件
- 支持健康状态检查（只显示status=1的服务）

#### port_status指标格式
```prometheus
port_status{group="bigdata-exporter", instance="192.168.7.20:9333", job="bigdata-exporter-new", name="Ranger-admin_bd-prod-lyj-master02", port="6080", role="bigdata-exporter"}
```

#### 支持的服务识别
- **Ranger**: Ranger Admin (6080), Ranger UserSync (5151)
- **HDFS**: NameNode (9870), DataNode (9864), JournalNode (8485)
- **YARN**: ResourceManager (8088), NodeManager (8042)
- **Hive**: HiveServer2 (10000), Hive MetaStore (9083)
- **Spark**: Spark History Server (18080/18081)
- **DolphinScheduler**: DS-Master (5678), DS-ApiServer (12345)
- **ZooKeeper**: ZooKeeper (2181)
- **其他**: LDAP (389), Kafka (9092), Elasticsearch (9200), Grafana (3000), Prometheus (9090)

## 📖 操作指南

### 1. 访问监控仪表盘

#### 基本操作
1. 登录BigDataOps系统
2. 在左侧导航栏点击"监控"
3. 选择"监控仪表盘"
4. 系统显示监控主页面

#### 仪表盘功能
- **全局刷新**: 点击右上角刷新按钮更新所有监控数据
- **快速导航**: 点击导航卡片快速跳转到对应功能模块
- **状态查看**: 在状态概览区域查看详细的系统状态信息

### 2. 集群总览使用

#### 节点监控
1. **查看节点列表**: 显示所有集群节点的基本信息
2. **状态筛选**: 支持按节点状态筛选
   - 全部节点
   - 健康节点 (在线且资源使用正常)
   - 异常节点 (离线或资源使用异常)
3. **资源阈值**:
   - CPU 使用率: 70% 警告, 90% 危险
   - 内存使用率: 80% 警告, 95% 危险
   - 磁盘使用率: 85% 警告, 95% 危险

#### 筛选参数说明
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

### 3. 组件监控使用

#### 组件状态查看
1. 进入"组件监控"页面
2. 查看各组件状态概览
3. 点击组件名称查看详细信息
4. 查看组件实例状态和指标

#### 组件详情页面
- **基本信息**: 组件名称、版本、状态
- **实例列表**: 各实例的详细状态
- **监控指标**: 关键性能指标
- **告警信息**: 相关告警规则

### 4. 健康检查

#### 健康检查接口
```http
GET /api/cluster/health
```

#### 检查内容
- 节点在线状态
- 服务运行状态
- 资源使用情况
- 网络连通性

## ⚙️ 配置说明

### 环境变量配置

#### Prometheus配置
```bash
# Prometheus连接
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_TIMEOUT=30
```

#### 监控配置
```bash
# 监控间隔
MONITORING_INTERVAL=30  # 秒

# 健康检查超时
HEALTH_CHECK_TIMEOUT=10  # 秒

# 缓存时间
CACHE_DURATION=60  # 秒
```

### 监控指标配置

#### 系统资源指标
```yaml
# CPU 使用率
node_cpu_utilization:
  description: "节点 CPU 使用率百分比"
  unit: "percent"
  range: "0-100"
  thresholds:
    warning: 70
    critical: 90

# 内存使用率  
node_memory_utilization:
  description: "节点内存使用率百分比"
  unit: "percent" 
  range: "0-100"
  thresholds:
    warning: 80
    critical: 95

# 磁盘使用率
node_disk_utilization:
  description: "节点磁盘使用率百分比"
  unit: "percent"
  range: "0-100" 
  thresholds:
    warning: 85
    critical: 95
```

### 前端配置

#### 自动刷新配置
```javascript
// 监控数据自动刷新间隔
const REFRESH_INTERVAL = 30000; // 30秒

// 健康检查刷新间隔
const HEALTH_CHECK_INTERVAL = 60000; // 60秒
```

#### 图表配置
```javascript
// ECharts图表配置
const chartOptions = {
  // 图表主题
  theme: 'light',
  
  // 响应式配置
  responsive: true,
  
  // 动画配置
  animation: true,
  animationDuration: 1000
};
```

## 🔧 故障排查

### 常见问题

#### 1. 监控数据不更新
**症状**: 监控界面显示数据过时或无数据

**排查步骤**:
1. 检查 Prometheus 服务状态
   ```bash
   systemctl status prometheus
   ```

2. 检查 Node Exporter 状态
   ```bash
   systemctl status node_exporter
   curl http://localhost:9100/metrics
   ```

3. 检查网络连通性
   ```bash
   curl http://prometheus-server:9090/api/v1/query?query=up
   ```

#### 2. 节点显示离线
**症状**: 节点在监控界面显示为离线状态

**排查步骤**:
1. 检查目标节点 Node Exporter
   ```bash
   systemctl status node_exporter
   netstat -tlnp | grep 9100
   ```

2. 检查网络连通性
   ```bash
   curl http://target-node:9100/metrics
   ```

3. 检查防火墙设置
   ```bash
   iptables -L | grep 9100
   ```

#### 3. 组件状态异常
**症状**: 组件显示为异常状态

**排查步骤**:
1. 检查组件服务状态
   ```bash
   systemctl status hdfs-namenode
   systemctl status yarn-resourcemanager
   ```

2. 检查端口监听
   ```bash
   netstat -tlnp | grep 9870  # HDFS NameNode
   netstat -tlnp | grep 8088  # YARN ResourceManager
   ```

3. 查看组件日志
   ```bash
   tail -f /var/log/hadoop/hdfs-namenode.log
   tail -f /var/log/hadoop/yarn-resourcemanager.log
   ```

### 调试工具

#### Prometheus查询
```bash
# 查询节点状态
curl "http://localhost:9090/api/v1/query?query=up"

# 查询CPU使用率
curl "http://localhost:9090/api/v1/query?query=100%20-%20(avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m]))%20*%20100)"

# 查询内存使用率
curl "http://localhost:9090/api/v1/query?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100"
```

#### API接口测试
```bash
# 健康检查
curl http://localhost:8000/api/cluster/health

# 获取集群概览
curl http://localhost:8000/api/cluster/overview

# 获取节点列表
curl http://localhost:8000/api/cluster/nodes
```

## 🎯 最佳实践

### 1. 监控配置

#### 合理设置采集频率
```yaml
# prometheus.yml
global:
  scrape_interval: 15s      # 全局采集间隔
  evaluation_interval: 15s  # 规则评估间隔

scrape_configs:
  - job_name: 'node-exporter'
    scrape_interval: 15s    # 节点指标采集间隔
    static_configs:
      - targets: ['node1:9100', 'node2:9100']
```

#### 配置合理的告警阈值
```yaml
# 根据业务场景调整阈值
groups:
  - name: node-alerts
    rules:
      - alert: HighCpuUsage
        expr: node_cpu_utilization > 85
        for: 5m
        
      - alert: HighMemoryUsage  
        expr: node_memory_utilization > 90
        for: 3m
```

### 2. 性能优化

#### 前端优化
- 合理设置自动刷新间隔 (建议 30-60 秒)
- 使用分页减少单次数据量
- 启用数据缓存减少 API 调用

#### 后端优化  
- 使用连接池管理数据库连接
- 实现查询结果缓存
- 异步处理长时间查询

### 3. 监控策略

#### 分层监控
- **基础设施层**: 硬件、网络、操作系统
- **平台层**: 大数据组件、中间件
- **应用层**: 业务应用、服务接口

#### 关键指标监控
- **可用性指标**: 服务状态、响应时间
- **性能指标**: 吞吐量、延迟、队列长度
- **资源指标**: CPU、内存、磁盘、网络
- **业务指标**: 任务数量、成功率、错误率

### 4. 安全建议

#### 访问控制
- 启用用户认证和授权
- 限制监控接口访问权限
- 使用 HTTPS 传输数据

#### 数据保护
- 敏感指标数据脱敏
- 定期备份配置文件
- 监控系统自身的安全状态

### 5. 运维建议

#### 定期维护
- 清理历史监控数据
- 优化数据库索引
- 更新监控规则配置

#### 容量规划
- 监控存储空间使用
- 评估查询性能
- 规划扩展方案

---

**版本**: v2.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps开发团队

如有问题或建议，请联系开发团队或提交Issue。 