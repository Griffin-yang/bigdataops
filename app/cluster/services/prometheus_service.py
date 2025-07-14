import aiohttp
import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.config import get_settings
from app.cluster.config.metrics_config import HOST_METRICS
from app.utils.logger import logger

class PrometheusService:
    """Prometheus查询服务"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.prometheus_url = get_settings().prometheus_url
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def query_instant(self, query: str) -> Dict:
        """执行即时查询"""
        try:
            session = await self._get_session()
            url = f"{self.prometheus_url}/api/v1/query"
            params = {'query': query}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Prometheus查询失败: {response.status} - {await response.text()}")
                    return {"status": "error", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Prometheus查询异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def query_range(self, query: str, start: str, end: str, step: str = "15s") -> Dict:
        """执行范围查询"""
        try:
            session = await self._get_session()
            url = f"{self.prometheus_url}/api/v1/query_range"
            params = {
                'query': query,
                'start': start,
                'end': end,
                'step': step
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Prometheus范围查询失败: {response.status}")
                    return {"status": "error", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Prometheus范围查询异常: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_host_metrics(self, service_filter: Optional[str] = None,
                              job_filter: Optional[str] = None,
                              role_filter: Optional[str] = None) -> List[Dict]:
        """获取主机指标"""
        try:
            hosts = []
            
            # 构建节点基础信息查询的筛选条件
            # 注意：node_uname_info主要在consul-node中，不直接支持bigdata job筛选
            node_filters = {}
            if service_filter:
                node_filters['service'] = service_filter
            if role_filter:
                node_filters['role'] = role_filter
            
            # 对于consul-node以外的job，不在node_uname_info查询中使用job筛选
            # 我们稍后会通过该job的实际服务状态来筛选节点
            if job_filter == "consul-node":
                node_filters['job'] = job_filter
            
            # 构建node_uname_info查询以获取节点基础信息（总是基于consul-node）
            node_info_query = self._build_query_with_filters('node_uname_info', node_filters)
            
            # 获取节点基础信息
            node_info_result = await self.query_instant(node_info_query)
            instances = {}
            
            # 先从node_uname_info获取节点详细信息
            if node_info_result.get('status') == 'success':
                node_info_data = node_info_result.get('data', {}).get('result', [])
                for item in node_info_data:
                    metric = item.get('metric', {})
                    instance = metric.get('instance', '')
                    if instance:
                        instances[instance] = {
                            'instance': instance,
                            'job': metric.get('job', 'unknown'),
                            'service': metric.get('service', 'unknown'),
                            'role': metric.get('role', 'unknown'),
                            'hostname': metric.get('hostname', instance.split(':')[0] if ':' in instance else instance),
                            'location': metric.get('location', 'unknown'),
                            'rack': metric.get('rack', 'unknown'),
                            'env': metric.get('env', 'unknown'),
                            'deviceType': metric.get('deviceType', 'unknown'),
                            'status': 'unknown'
                        }
            
            # 如果用户选择了特定的bigdata job，则根据该job的实际服务状态筛选节点
            if job_filter and job_filter != "consul-node":
                logger.info(f"正在根据job '{job_filter}' 筛选节点...")
                
                # 查询目标job的up状态
                job_up_query = f'up{{job="{job_filter}"}}'
                job_up_result = await self.query_instant(job_up_query)
                
                if job_up_result.get('status') == 'success':
                    job_up_data = job_up_result.get('data', {}).get('result', [])
                    active_ips = set()
                    
                    # 收集该job中状态为up的服务对应的IP地址
                    for item in job_up_data:
                        metric = item.get('metric', {})
                        instance = metric.get('instance', '')
                        value = float(item.get('value', [None, '0'])[1])
                        
                        if value > 0 and instance:  # 服务状态为up
                            ip = instance.split(':')[0]  # 提取IP地址
                            active_ips.add(ip)
                    
                    logger.info(f"Job '{job_filter}' 中有活跃服务的IP地址: {active_ips}")
                    
                    # 筛选节点：只保留在目标job中有活跃服务的节点
                    filtered_instances = {}
                    for instance_key, instance_data in instances.items():
                        node_ip = instance_key.split(':')[0]  # 提取节点IP
                        if node_ip in active_ips:
                            filtered_instances[instance_key] = instance_data
                    
                    instances = filtered_instances
                    logger.info(f"根据job '{job_filter}' 筛选后保留 {len(instances)} 个节点")
                else:
                    logger.warning(f"无法查询job '{job_filter}' 的状态")
                    instances = {}  # 查询失败时返回空结果
            
            # 如果没有找到任何节点，返回空列表
            if not instances:
                logger.warning(f"没有找到匹配筛选条件的节点: {node_filters}, job_filter: {job_filter}")
                return []
            
            # 构建指标查询的筛选条件
            # 对于特定job筛选，我们已经筛选了节点，指标查询使用基础筛选条件
            metric_filters = {}
            if service_filter:
                metric_filters['service'] = service_filter
            if role_filter:
                metric_filters['role'] = role_filter
            # 注意：不在这里添加job筛选，因为指标查询仍然基于consul-node
            
            # 获取UP状态信息
            up_query = self._build_query_with_filters('up', metric_filters)
            up_result = await self.query_instant(up_query)
            if up_result.get('status') == 'success':
                up_data = up_result.get('data', {}).get('result', [])
                for item in up_data:
                    metric = item.get('metric', {})
                    instance = metric.get('instance', '')
                    if instance in instances:
                        instances[instance]['status'] = 'up' if float(item.get('value', [None, '0'])[1]) > 0 else 'down'
            
            # 并发查询所有指标
            tasks = []
            for metric_name, config in HOST_METRICS.items():
                query_with_filters = self._build_query_with_filters(config['query'], metric_filters)
                task = self._query_host_metric(metric_name, query_with_filters)
                tasks.append(task)
            
            metric_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并指标数据
            for i, (metric_name, config) in enumerate(HOST_METRICS.items()):
                result = metric_results[i]
                if isinstance(result, Exception):
                    logger.error(f"查询指标{metric_name}失败: {result}")
                    continue
                
                if result.get('status') == 'success':
                    data = result.get('data', {}).get('result', [])
                    for item in data:
                        metric = item.get('metric', {})
                        instance = metric.get('instance', '')
                        if instance in instances:
                            value = float(item.get('value', [None, '0'])[1])
                            instances[instance][metric_name] = round(value, 2)
            
            # 转换为列表格式并设置默认值
            for instance_data in instances.values():
                # 设置默认值
                for metric_name in HOST_METRICS.keys():
                    instance_data.setdefault(metric_name, 0)
                
                # 兼容字段映射
                instance_data.setdefault('load_1m', instance_data.get('load_5m', 0))
                instance_data.setdefault('network_bytes_recv', instance_data.get('network_recv_rate', 0))
                instance_data.setdefault('network_bytes_sent', instance_data.get('network_send_rate', 0))
                instance_data.setdefault('uptime', instance_data.get('uptime_days', 0) * 86400)
                
                # 格式化显示
                uptime_days = instance_data.get('uptime_days', 0)
                if uptime_days > 0:
                    instance_data['uptime_formatted'] = f"{int(uptime_days)}天"
                else:
                    instance_data['uptime_formatted'] = "未知"
                instance_data['last_seen'] = datetime.now().isoformat()
                
                hosts.append(instance_data)
            
            logger.info(f"获取到 {len(hosts)} 个节点的指标数据（筛选条件: {node_filters}）")
            return hosts
            
        except Exception as e:
            logger.error(f"获取主机指标失败: {e}")
            return []
    
    async def _query_host_metric(self, metric_name: str, query: str) -> Dict:
        """查询单个主机指标"""
        return await self.query_instant(query)
    
    def _build_query_with_filters(self, base_query: str, filters: Dict[str, str]) -> str:
        """构建带筛选条件的Prometheus查询"""
        try:
            if not filters:
                return base_query
            
            # 构建筛选条件字符串
            filter_parts = []
            for key, value in filters.items():
                filter_parts.append(f'{key}="{value}"')
            filter_str = ','.join(filter_parts)
            
            # 使用正则表达式匹配和替换node_开头的指标
            def replace_node_metric(match):
                metric_name = match.group(1)
                existing_labels = match.group(2) or ''
                time_range = match.group(3) or ''
                
                if existing_labels:
                    # 移除现有标签的大括号并合并筛选条件
                    labels_content = existing_labels[1:-1]  # 去掉{}
                    if labels_content.strip():
                        new_labels = f"{{{labels_content},{filter_str}}}"
                    else:
                        new_labels = f"{{{filter_str}}}"
                else:
                    # 没有现有标签，直接添加筛选条件
                    new_labels = f"{{{filter_str}}}"
                
                return f"{metric_name}{new_labels}{time_range}"
            
            # 匹配node_开头的指标名称
            node_pattern = r'\b(node_[a-zA-Z_][a-zA-Z0-9_]*)\s*(\{[^}]*\})?\s*(\[[^\]]*\])?'
            filtered_query = re.sub(node_pattern, replace_node_metric, base_query)
            
            # 特殊处理up指标
            if base_query.strip() == 'up':
                filtered_query = f"up{{{filter_str}}}"
            elif base_query.startswith('up{'):
                # up已有标签的情况
                existing_content = base_query[3:-1]  # 去掉up{和}
                if existing_content.strip():
                    filtered_query = f"up{{{existing_content},{filter_str}}}"
                else:
                    filtered_query = f"up{{{filter_str}}}"
            
            # 特殊处理port_status指标
            elif 'port_status' in base_query:
                if base_query.strip() == 'port_status':
                    filtered_query = f"port_status{{{filter_str}}}"
                elif base_query.startswith('port_status{'):
                    # port_status已有标签的情况
                    existing_content = base_query[12:-1]  # 去掉port_status{和}
                    if existing_content.strip():
                        filtered_query = f"port_status{{{existing_content},{filter_str}}}"
                    else:
                        filtered_query = f"port_status{{{filter_str}}}"
            
            logger.debug(f"原查询: {base_query}")
            logger.debug(f"筛选后: {filtered_query}")
            
            return filtered_query
            
        except Exception as e:
            logger.error(f"构建筛选查询失败: {e}, 使用原查询: {base_query}")
            return base_query
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """格式化运行时间"""
        try:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                return f"{days}天{hours}小时"
            elif hours > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{minutes}分钟"
        except:
            return "未知"
    
    async def get_component_metrics(self, component_name: str, metrics_config: Dict) -> Dict:
        """获取组件指标"""
        try:
            results = {}
            
            tasks = []
            for metric_name, config in metrics_config.items():
                task = self.query_instant(config['query'])
                tasks.append((metric_name, task))
            
            for metric_name, task in tasks:
                try:
                    result = await task
                    results[metric_name] = result
                except Exception as e:
                    logger.error(f"查询组件{component_name}指标{metric_name}失败: {e}")
                    results[metric_name] = {"status": "error", "error": str(e)}
            
            return results
            
        except Exception as e:
            logger.error(f"获取组件{component_name}指标失败: {e}")
            return {}

# 创建全局实例
prometheus_service = PrometheusService()