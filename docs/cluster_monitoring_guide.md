# 集群监控系统详细指南

## 目录
- [概述](#概述)
- [系统架构](#系统架构)
- [功能特性](#功能特性)
- [使用指南](#使用指南)
- [监控指标说明](#监控指标说明)
- [API 接口说明](#api-接口说明)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

## 概述

BigDataOps 集群监控系统是一个基于 Prometheus 的大数据集群监控解决方案，提供实时监控、健康检查、资源管理和告警功能。

### 核心目标
- **实时监控**: 提供集群节点和大数据组件的实时状态监控
- **健康管理**: 自动检测系统健康状况，及时发现潜在问题
- **资源优化**: 监控资源使用情况，辅助资源调优决策
- **故障预警**: 基于监控数据提供智能告警和故障预警

## 系统架构

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

### 组件说明
- **Web Frontend**: Vue3 + Element Plus 构建的监控界面
- **Backend API**: FastAPI 提供的 RESTful 服务
- **Prometheus**: 时序数据库和监控系统
- **Node Exporter**: 节点级别的系统指标收集器
- **JMX Exporter**: Java 应用的 JMX 指标导出器

## 功能特性

### 1. 监控仪表盘
- **系统健康状态**: 整体系统健康评估
- **关键指标摘要**: CPU、内存、磁盘使用率总览
- **快速导航**: 便捷访问各监控模块
- **实时更新**: 自动刷新监控数据

### 2. 集群总览
- **节点管理**: 显示所有集群节点状态
- **资源监控**: 实时监控各节点资源使用情况
- **角色分布**: 展示节点角色和服务分布
- **健康评估**: 综合评估集群健康状况

### 3. 组件监控
- **服务状态**: 监控 HDFS、YARN、Spark 等大数据组件
- **实例监控**: 跟踪各组件实例的运行状态
- **健康率**: 计算组件健康率和可用性
- **详细指标**: 提供组件级别的详细监控指标

### 4. 告警集成
- **规则管理**: 集成告警规则配置
- **历史查询**: 支持告警历史记录查询
- **通知管理**: 灵活的告警通知配置

### 5. 业务监控
- **任务调度监控**: 支持Azkaban和DolphinScheduler任务监控
- **执行统计**: 任务总数、成功率、失败率统计
- **失败分析**: 详细的失败任务列表和错误信息
- **性能分析**: 执行时间排行榜和性能优化建议

## 使用指南

### 监控仪表盘使用

#### 访问仪表盘
1. 登录系统后，默认进入监控仪表盘
2. 或通过导航菜单选择"监控" → "监控仪表盘"

#### 主要功能
```
仪表盘界面布局：
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

#### 操作说明
- **全局刷新**: 点击右上角刷新按钮更新所有监控数据
- **快速导航**: 点击导航卡片快速跳转到对应功能模块
- **状态查看**: 在状态概览区域查看详细的系统状态信息

### 集群总览使用

#### 节点监控
1. **节点列表**: 显示所有集群节点的基本信息
   - 主机名和 IP 地址
   - 服务角色 (NameNode, DataNode, ResourceManager 等)
   - 资源使用率 (CPU, 内存, 磁盘)
   - 在线状态和运行时间

2. **状态筛选**: 支持按节点状态筛选
   - 全部节点
   - 健康节点 (在线且资源使用正常)
   - 异常节点 (离线或资源使用异常)

3. **资源阈值**:
   - CPU 使用率: 70% 警告, 90% 危险
   - 内存使用率: 80% 警告, 95% 危险
   - 磁盘使用率: 85% 警告, 95% 危险

### 组件监控使用

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

### 业务监控使用

#### 支持的调度系统
- **Azkaban**: LinkedIn开源的工作流调度系统
- **DolphinScheduler**: Apache顶级项目，可视化工作流调度系统

#### 监控功能
1. **集群选择**: 支持CDH集群和Apache开源集群
2. **时间范围查询**: 自定义查询时间段
3. **实时统计**: 任务总数、成功数、失败数、成功率
4. **失败任务分析**: 失败任务列表、错误信息、详情链接
5. **性能排行**: 执行时间最长的任务TOP 50

## 监控指标说明

### 节点级别指标

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

## API 接口说明

### 集群概览接口

#### 获取集群健康状态
```http
GET /api/cluster/health
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "status": "healthy",
    "message": "集群运行正常",
    "details": {
      "total_nodes": 5,
      "healthy_nodes": 4,
      "unhealthy_nodes": 1,
      "avg_cpu_usage": 65.2,
      "avg_memory_usage": 72.8
    }
  }
}
```

#### 获取组件状态
```http
GET /api/cluster/components
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "components": {
      "hdfs": {
        "status": "healthy",
        "total_instances": 3,
        "healthy_instances": 3
      }
    }
  }
}
```

### 业务监控接口

#### 获取集群列表
```http
GET /api/business/clusters
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "cdh",
      "name": "CDH集群",
      "type": "cdh",
      "schedulers": ["azkaban", "dolphinscheduler"]
    },
    {
      "id": "apache",
      "name": "Apache开源集群", 
      "type": "apache",
      "schedulers": ["dolphinscheduler"]
    }
  ]
}
```

#### 获取业务概览
```http
GET /api/business/overview?cluster_name=cdh&start_date=2024-01-15&end_date=2024-01-15
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "cluster_name": "CDH集群",
    "date_range": "2024-01-15 至 2024-01-15",
    "total_jobs": 350,
    "success_jobs": 315,
    "failed_jobs": 35,
    "success_rate": 90.0,
    "schedulers_stats": {
      "azkaban": {
        "total_jobs": 150,
        "success_jobs": 135,
        "failed_jobs": 15
      },
      "dolphinscheduler": {
        "total_jobs": 200,
        "success_jobs": 180,
        "failed_jobs": 20
      }
    }
  }
}
```

## 故障排查

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

## 最佳实践

### 监控配置

#### 1. 合理设置采集频率
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

#### 2. 配置合理的告警阈值
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

### 性能优化

#### 1. 前端优化
- 合理设置自动刷新间隔 (建议 30-60 秒)
- 使用分页减少单次数据量
- 启用数据缓存减少 API 调用

#### 2. 后端优化  
- 使用连接池管理数据库连接
- 实现查询结果缓存
- 异步处理长时间查询

### 安全建议

#### 1. 访问控制
- 启用用户认证和授权
- 限制监控接口访问权限
- 使用 HTTPS 传输数据

#### 2. 数据保护
- 敏感指标数据脱敏
- 定期备份配置文件
- 监控系统自身的安全状态

---

**版本**: v1.0  
**更新时间**: 2024-01-15  
**维护团队**: BigDataOps 开发团队  

如有问题或建议，请联系开发团队或提交 Issue。 