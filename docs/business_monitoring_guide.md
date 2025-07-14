# 业务监控模块使用指南

## 概述

业务监控模块是BigDataOps平台的核心功能之一，专门用于监控大数据任务调度系统的执行情况。支持监控CDH集群（Azkaban + DolphinScheduler）和Apache开源集群（DolphinScheduler）的任务执行状态。

## 功能特性

### 支持的调度系统
- **Azkaban**: LinkedIn开源的工作流调度系统
- **DolphinScheduler**: Apache顶级项目，可视化工作流调度系统

### 支持的集群类型
- **CDH集群**: 混合调度环境，同时支持Azkaban和DolphinScheduler
- **Apache开源集群**: 纯DolphinScheduler调度环境

### 核心功能
1. **实时统计**: 任务总数、成功数、失败数、成功率
2. **失败任务分析**: 详细的失败任务列表和错误信息
3. **性能排行**: 执行时间最长的任务排行榜
4. **调度器分布**: 多调度器环境下的任务分布统计
5. **时间范围查询**: 支持自定义时间范围的数据查询

## 使用指南

### 访问业务监控

1. 登录BigDataOps系统
2. 在左侧导航栏点击"业务监控"
3. 系统将显示业务监控主页面

### 基本操作流程

#### 1. 选择监控集群
- 在页面顶部的"选择集群"下拉菜单中选择要监控的集群
- 系统支持CDH集群和Apache开源集群
- 选择集群后，页面会自动清空之前的数据

#### 2. 设置查询时间范围
- 使用日期选择器设置查询的开始日期和结束日期
- 默认显示昨天的数据
- 支持任意时间范围的查询

#### 3. 查询数据
- 点击"查询"按钮获取数据
- 系统会并行加载概览统计、失败任务列表和执行时间排行
- 查询完成后会显示数据更新时间

### 功能详解

#### 业务概览统计

显示选定时间范围内的关键指标：

**主要指标卡片**:
- **总任务数**: 执行的任务总数量
- **成功任务**: 执行成功的任务数量
- **失败任务**: 执行失败的任务数量  
- **成功率**: 成功任务占总任务的百分比

**调度器分布** (仅CDH集群显示):
- Azkaban调度的任务统计
- DolphinScheduler调度的任务统计
- 各调度器的任务分布情况

#### 失败任务列表

提供详细的失败任务信息：

**列表字段**:
- **任务名称**: 失败任务的名称和所属调度器
- **项目名称**: 任务所属的项目
- **执行时间**: 任务的执行开始时间
- **错误信息**: 详细的错误描述
- **查看详情**: 链接到调度系统的任务详情页面

**功能特性**:
- 支持分页浏览
- 点击"查看详情"可跳转到原调度系统查看完整日志
- 错误信息支持悬停查看完整内容

#### 执行时间排行榜

显示执行时间最长的任务：

**排行信息**:
- **排名**: 按执行时长的排序位置
- **任务名称**: 任务名称和调度器类型
- **项目名称**: 所属项目
- **执行时间**: 任务开始执行的时间
- **执行时长**: 任务运行的总时间（彩色标签显示）
- **状态**: 任务执行的最终状态

**时长颜色标识**:
- 🟢 绿色: 30分钟以内
- 🟡 黄色: 30分钟-1小时
- 🔴 红色: 超过1小时

## 配置说明

### 后端配置

业务监控模块的配置通过环境变量或配置文件设置：

#### CDH集群配置
```bash
# Azkaban配置
AZKABAN_HOST=your-azkaban-host
AZKABAN_PORT=8443
AZKABAN_USERNAME=admin
AZKABAN_PASSWORD=admin

# CDH集群DolphinScheduler配置
CDH_DS_HOST=your-ds-host
CDH_DS_PORT=3306
CDH_DS_DATABASE=dolphinscheduler
CDH_DS_USERNAME=ds
CDH_DS_PASSWORD=ds123
```

#### Apache集群配置
```bash
# Apache集群DolphinScheduler配置
APACHE_DS_HOST=your-ds-host
APACHE_DS_PORT=3306
APACHE_DS_DATABASE=dolphinscheduler
APACHE_DS_USERNAME=ds
APACHE_DS_PASSWORD=ds123
```

### API 接口

业务监控提供以下REST API接口：

#### 获取集群列表
```http
GET /api/business/clusters
```

#### 获取业务概览
```http
GET /api/business/overview?cluster_name=cdh&start_date=2024-01-15&end_date=2024-01-15
```

#### 获取失败任务列表
```http
GET /api/business/failed-jobs?cluster_name=cdh&start_date=2024-01-15&end_date=2024-01-15&page=1&size=20
```

#### 获取执行时间排行
```http
GET /api/business/top-duration-jobs?cluster_name=cdh&start_date=2024-01-15&end_date=2024-01-15&limit=50
```

## 数据源集成

### Azkaban集成

**数据来源方式**:
1. **API方式**: 通过Azkaban REST API获取执行数据
2. **数据库方式**: 直接查询Azkaban MySQL数据库

**主要数据表**:
- `execution_flows`: 工作流执行记录
- `execution_jobs`: 任务执行记录
- `projects`: 项目信息

### DolphinScheduler集成

**数据来源方式**:
1. **API方式**: 通过DolphinScheduler REST API获取数据
2. **数据库方式**: 直接查询DolphinScheduler MySQL/PostgreSQL数据库

**主要数据表**:
- `t_ds_process_instance`: 工作流实例表
- `t_ds_task_instance`: 任务实例表
- `t_ds_project`: 项目信息表

## 扩展开发

### 添加新的调度系统

要支持新的调度系统，需要：

1. **扩展BusinessService类**:
```python
async def _get_new_scheduler_stats(self, config: Dict, start_date: str, end_date: str):
    # 实现新调度系统的统计数据获取
    pass
```

2. **更新集群配置**:
```python
self.clusters_config["new_cluster"] = {
    "name": "新集群",
    "type": "custom",
    "schedulers": ["new_scheduler"],
    "new_scheduler_config": {
        # 新调度系统的配置
    }
}
```

3. **实现数据获取方法**:
- `_get_new_scheduler_failed_jobs()`
- `_get_new_scheduler_duration_jobs()`

### 自定义监控指标

可以扩展监控指标，例如：

```python
# 添加新的统计维度
overview["custom_metrics"] = {
    "avg_duration": avg_task_duration,
    "peak_hour": peak_execution_hour,
    "resource_usage": resource_usage_stats
}
```

## 故障排查

### 常见问题

#### 1. 数据无法加载
**症状**: 页面显示"查询数据失败"

**可能原因**:
- 调度系统连接配置错误
- 网络连接问题
- 数据库权限不足

**解决方案**:
1. 检查配置文件中的连接参数
2. 验证网络连通性
3. 确认数据库用户权限

#### 2. 数据显示不完整
**症状**: 部分调度器的数据缺失

**可能原因**:
- 调度系统API不可用
- 数据库查询超时
- 权限限制

**解决方案**:
1. 检查调度系统服务状态
2. 优化数据库查询性能
3. 确认API调用权限

#### 3. 性能问题
**症状**: 数据加载缓慢

**优化建议**:
1. 启用数据库连接池
2. 实现查询结果缓存
3. 优化数据库索引
4. 限制查询时间范围

### 日志分析

**后端日志位置**:
```bash
tail -f /var/log/bigdataops/business.log
```

**关键日志信息**:
- 数据库连接状态
- API调用响应时间
- 错误堆栈信息

## 最佳实践

### 性能优化

1. **合理设置查询时间范围**
   - 避免查询过长时间范围的数据
   - 建议单次查询不超过30天

2. **启用数据缓存**
   - 对频繁查询的数据启用缓存
   - 设置合理的缓存过期时间

3. **数据库优化**
   - 在执行时间字段上创建索引
   - 定期清理历史数据

### 监控建议

1. **设置告警规则**
   - 失败率超过阈值时发送告警
   - 长时间运行任务的告警

2. **定期检查**
   - 每日检查失败任务情况
   - 关注执行时间异常的任务

3. **容量规划**
   - 根据任务执行趋势进行资源规划
   - 监控集群资源使用情况

## 更新日志

### v1.0.0 (2024-01-15)
- ✅ 支持CDH集群和Apache集群监控
- ✅ 集成Azkaban和DolphinScheduler
- ✅ 实现业务概览统计
- ✅ 失败任务列表和详情链接
- ✅ 执行时间排行榜
- ✅ 时间范围查询功能
- ✅ 响应式界面设计

---

**维护团队**: BigDataOps开发团队  
**文档版本**: v1.0  
**最后更新**: 2024-01-15

如有问题或建议，请联系开发团队或提交Issue。 