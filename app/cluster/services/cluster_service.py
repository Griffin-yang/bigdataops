import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.cluster.services.prometheus_service import prometheus_service
from app.cluster.config.metrics_config import HOST_METRICS, ALL_COMPONENT_METRICS, COMPONENT_ROLES
from app.utils.logger import logger

class ClusterService:
    """集群监控服务"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 30  # 缓存30秒
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self.cache:
            return False
        cache_time = self.cache[key].get('timestamp', datetime.min)
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _get_cache(self, key: str) -> Any:
        """获取缓存数据"""
        return self.cache[key]['data'] if key in self.cache else None
    
    async def get_cluster_overview(self, service_filter: Optional[str] = None, 
                                  job_filter: Optional[str] = None, 
                                  role_filter: Optional[str] = None) -> Dict:
        """获取集群总览信息"""
        cache_key = f"cluster_overview_{service_filter}_{job_filter}_{role_filter}"
        if self._is_cache_valid(cache_key):
            return self._get_cache(cache_key)
        
        try:
            # 获取主机指标，应用筛选条件
            host_metrics = await prometheus_service.get_host_metrics(
                service_filter=service_filter,
                job_filter=job_filter,
                role_filter=role_filter
            )
            
            total_nodes = len(host_metrics)
            healthy_nodes = sum(1 for node in host_metrics if node.get('status') == 'up')
            unhealthy_nodes = total_nodes - healthy_nodes
            
            # 计算平均资源使用率
            avg_cpu = sum(node.get('cpu_usage', 0) for node in host_metrics) / max(total_nodes, 1)
            avg_memory = sum(node.get('memory_usage', 0) for node in host_metrics) / max(total_nodes, 1)
            avg_disk = sum(node.get('disk_usage', 0) for node in host_metrics) / max(total_nodes, 1)
            
            # 获取服务状态统计
            components = await self.get_components_overview()
            services_status = {}
            for name, component in components.items():
                services_status[name] = {
                    'healthy': component.get('healthy_instances', 0),
                    'total': component.get('total_instances', 0)
                }
            
            # 按service分组统计
            service_distribution = {}
            if host_metrics:
                for node in host_metrics:
                    service = node.get('service', 'unknown')
                    if service not in service_distribution:
                        service_distribution[service] = {'total': 0, 'healthy': 0}
                    service_distribution[service]['total'] += 1
                    if node.get('status') == 'up':
                        service_distribution[service]['healthy'] += 1
            
            overview = {
                'total_nodes': total_nodes,
                'healthy_nodes': healthy_nodes,
                'unhealthy_nodes': unhealthy_nodes,
                'avg_cpu_usage': round(avg_cpu, 2),
                'avg_memory_usage': round(avg_memory, 2),
                'avg_disk_usage': round(avg_disk, 2),
                'services_status': services_status,
                'service_distribution': service_distribution,
                'filter_applied': {
                    'service': service_filter,
                    'job': job_filter,
                    'role': role_filter
                },
                'update_time': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, overview)
            return overview
            
        except Exception as e:
            logger.error(f"获取集群概览失败: {e}")
            return {
                'total_nodes': 0,
                'healthy_nodes': 0,
                'unhealthy_nodes': 0,
                'avg_cpu_usage': 0,
                'avg_memory_usage': 0,
                'avg_disk_usage': 0,
                'services_status': {},
                'service_distribution': {},
                'error': str(e)
            }
    
    async def get_nodes_list(self, status_filter: Optional[str] = None,
                            service_filter: Optional[str] = None,
                            job_filter: Optional[str] = None,
                            role_filter: Optional[str] = None) -> List[Dict]:
        """获取节点列表"""
        try:
            host_metrics = await prometheus_service.get_host_metrics(
                service_filter=service_filter,
                job_filter=job_filter,
                role_filter=role_filter
            )
            
            # 过滤节点状态
            if status_filter:
                if status_filter == 'healthy':
                    host_metrics = [node for node in host_metrics if node.get('status') == 'up']
                elif status_filter == 'unhealthy':
                    host_metrics = [node for node in host_metrics if node.get('status') != 'up']
            
            # 添加角色信息
            for node in host_metrics:
                node['roles'] = await self._get_node_roles(node.get('instance', ''))
            
            return host_metrics
            
        except Exception as e:
            logger.error(f"获取节点列表失败: {e}")
            return []
    
    async def _get_node_roles(self, instance: str) -> List[str]:
        """获取节点角色，基于port_status指标和nodename匹配"""
        roles = []
        try:
            # 先获取当前节点的nodename
            node_info_query = f'node_uname_info{{instance="{instance}"}}'
            node_result = await prometheus_service.query_instant(node_info_query)
            
            current_nodename = None
            if node_result.get('status') == 'success':
                node_data = node_result.get('data', {}).get('result', [])
                if node_data:
                    current_nodename = node_data[0].get('metric', {}).get('nodename', '')
            
            if not current_nodename:
                logger.debug(f"无法获取节点 {instance} 的nodename")
                return ['Unknown']
            
            # 从nodename提取主机名部分 (例如: bd-prod-lyj-master01.leyoujia.com -> bd-prod-lyj-master01)
            hostname_part = self._extract_hostname_from_nodename(current_nodename)
            if not hostname_part:
                logger.debug(f"无法从nodename {current_nodename} 提取主机名")
                return ['Unknown']
            
            # 查询所有port_status数据
            port_status_query = 'port_status'
            result = await prometheus_service.query_instant(port_status_query)
            
            if result.get('status') == 'success':
                data = result.get('data', {}).get('result', [])
                role_names = set()
                
                for item in data:
                    metric = item.get('metric', {})
                    value = float(item.get('value', [None, '0'])[1])
                    
                    # 只处理健康的服务（value=1）
                    if value == 1:
                        name = metric.get('name', '')
                        port = metric.get('port', '')
                        
                        # 灵活匹配策略
                        if self._is_service_match_node(hostname_part, name, current_nodename):
                            # 从name字段解析服务角色
                            role = self._parse_service_role_from_name(name, port)
                            if role:
                                role_names.add(role)
                
                roles = list(role_names)
                
                # 记录找到的角色
                if roles:
                    logger.debug(f"节点 {hostname_part} ({instance}) 的角色: {roles}")
                else:
                    logger.debug(f"节点 {hostname_part} ({instance}) 未找到匹配的服务角色")
                
        except Exception as e:
            logger.error(f"获取节点角色失败: {e}")
        
        return roles if roles else ['Unknown']
    
    def _extract_hostname_from_nodename(self, nodename: str) -> str:
        """从nodename提取主机名部分"""
        if not nodename:
            return None
            
        # 去掉域名部分
        if '.' in nodename:
            hostname_part = nodename.split('.')[0]
        else:
            hostname_part = nodename
            
        # 处理不同的命名格式
        # 格式1: bd-prod-lyj-master01 
        if hostname_part.startswith('bd-prod-lyj-'):
            return hostname_part
            
        # 格式2: bigdata-storage-node1 -> 需要映射到bd-prod格式
        # 我们需要获取对应的真实主机名
        return self._map_consul_hostname_to_bigdata_hostname(hostname_part)
    
    def _map_consul_hostname_to_bigdata_hostname(self, consul_hostname: str) -> str:
        """将consul节点名映射到大数据主机名"""
        # 这里需要建立映射关系，由于实际环境中的映射关系复杂，
        # 我们采用更灵活的匹配策略：直接返回原主机名，在匹配时使用模糊匹配
        return consul_hostname
    
    def _is_service_match_node(self, hostname_part: str, service_name: str, full_nodename: str) -> bool:
        """判断服务是否属于当前节点"""
        if not hostname_part or not service_name:
            return False
        
        # 只处理bd-lyj开头的主机名，其他主机直接返回False
        if not full_nodename or 'bd-prod-lyj-' not in full_nodename.lower():
            return False
        
        service_lower = service_name.lower()
        
        # 从完整nodename提取真正的主机名进行匹配
        # 例如: bd-prod-lyj-master01.leyoujia.com -> bd-prod-lyj-master01
        real_hostname = full_nodename.split('.')[0] if '.' in full_nodename else full_nodename
        
        # 精确匹配 - 检查service_name中是否包含真正的主机名
        if real_hostname.lower() in service_lower:
            return True
        
        return False
    
    def _extract_machine_name_from_service_name(self, service_name: str) -> str:
        """从port_status的name字段提取机器名"""
        if not service_name:
            return None
            
        # 服务名格式通常是: ServiceName_machine-name
        # 例如: Ranger-admin_bd-prod-lyj-master02
        if '_' in service_name:
            parts = service_name.split('_')
            if len(parts) >= 2:
                return parts[-1]  # 取最后一部分作为机器名
        
        return None
    

    
    def _parse_service_role_from_name(self, name: str, port: str) -> str:
        """从port_status的name字段解析服务角色"""
        if not name:
            return None
            
        # 常见服务名称到角色的映射
        service_mappings = {
            'Ranger-admin': 'Ranger Admin',
            'RangerUserSync': 'Ranger UserSync',
            'JournalNode': 'HDFS JournalNode',
            'DS-ApiServer': 'DolphinScheduler API',
            'DS-Master': 'DolphinScheduler Master',
            'zk': 'ZooKeeper',
            'LDAP': 'LDAP Server',
            'Spark-History': 'Spark History Server',
            'NameNode': 'HDFS NameNode',
            'DataNode': 'HDFS DataNode',
            'ResourceManager': 'YARN ResourceManager',
            'NodeManager': 'YARN NodeManager',
            'HiveMetaStore': 'Hive MetaStore',
            'HiveServer2': 'HiveServer2',
            'Kafka': 'Kafka Broker',
            'Elasticsearch': 'Elasticsearch',
            'Kibana': 'Kibana',
            'Grafana': 'Grafana',
            'Prometheus': 'Prometheus'
        }
        
        # 尝试从name字段匹配服务
        for service_key, role_name in service_mappings.items():
            if service_key.lower() in name.lower():
                return role_name
        
        # 如果没有匹配到，尝试根据端口号推断
        port_mappings = {
            '2181': 'ZooKeeper',
            '8485': 'HDFS JournalNode',
            '9870': 'HDFS NameNode',
            '9864': 'HDFS DataNode',
            '8088': 'YARN ResourceManager',
            '8042': 'YARN NodeManager',
            '10000': 'HiveServer2',
            '9083': 'Hive MetaStore',
            '18081': 'Spark History Server',
            '18080': 'Spark History Server',
            '6080': 'Ranger Admin',
            '5151': 'Ranger UserSync',
            '12345': 'DolphinScheduler API',
            '5678': 'DolphinScheduler Master',
            '389': 'LDAP Server',
            '9092': 'Kafka Broker',
            '9200': 'Elasticsearch',
            '5601': 'Kibana',
            '3000': 'Grafana',
            '9090': 'Prometheus'
        }
        
        if port in port_mappings:
            return port_mappings[port]
        
        # 最后尝试直接使用name的前缀
        if '_' in name:
            prefix = name.split('_')[0]
            return prefix.replace('-', ' ').title()
        
        return None
    
    async def get_components_overview(self) -> Dict:
        """获取组件概览"""
        cache_key = "components_overview"
        if self._is_cache_valid(cache_key):
            return self._get_cache(cache_key)
        
        try:
            components = {}
            
            for component_name, metrics in ALL_COMPONENT_METRICS.items():
                component_data = await self._get_component_status(component_name, metrics)
                components[component_name] = component_data
            
            self._set_cache(cache_key, components)
            return components
            
        except Exception as e:
            logger.error(f"获取组件概览失败: {e}")
            return {}
    
    async def _get_component_status(self, component_name: str, metrics: Dict) -> Dict:
        """获取单个组件状态"""
        try:
            services = []
            total_instances = 0
            healthy_instances = 0
            
            for service_name, config in metrics.items():
                service_data = await self._get_service_status(service_name, config)
                services.append(service_data)
                
                instances = service_data.get('instances', [])
                total_instances += len(instances)
                healthy_instances += sum(1 for inst in instances if inst.get('status') == 'up')
            
            # 确定整体状态
            if total_instances == 0:
                status = 'unknown'
            elif healthy_instances == total_instances:
                status = 'healthy'
            elif healthy_instances > 0:
                status = 'warning'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'total_instances': total_instances,
                'healthy_instances': healthy_instances,
                'services': services,
                'update_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取组件{component_name}状态失败: {e}")
            return {
                'status': 'error',
                'total_instances': 0,
                'healthy_instances': 0,
                'services': [],
                'error': str(e)
            }
    
    async def _get_service_status(self, service_name: str, config: Dict) -> Dict:
        """获取服务状态"""
        try:
            query = config.get('query', '')
            result = await prometheus_service.query_instant(query)
            
            instances = []
            if result.get('status') == 'success':
                data = result.get('data', {}).get('result', [])
                for item in data:
                    metric = item.get('metric', {})
                    value = item.get('value', [None, '0'])[1]
                    
                    instance_data = {
                        'instance': metric.get('instance', 'unknown'),
                        'job': metric.get('job', 'unknown'),
                        'status': 'up' if float(value) > 0 else 'down',
                        'value': float(value),
                        'metric': metric
                    }
                    instances.append(instance_data)
            
            return {
                'name': service_name,
                'display_name': COMPONENT_ROLES.get(f"unknown-{service_name}", service_name),
                'query': query,
                'instances': instances,
                'total_instances': len(instances),
                'healthy_instances': sum(1 for inst in instances if inst['status'] == 'up')
            }
            
        except Exception as e:
            logger.error(f"获取服务{service_name}状态失败: {e}")
            return {
                'name': service_name,
                'display_name': service_name,
                'instances': [],
                'error': str(e)
            }
    
    async def get_component_detail(self, component_name: str) -> Dict:
        """获取组件详情"""
        try:
            if component_name not in ALL_COMPONENT_METRICS:
                return {'error': f'不支持的组件: {component_name}'}
            
            metrics = ALL_COMPONENT_METRICS[component_name]
            component_data = await self._get_component_status(component_name, metrics)
            
            # 添加详细的指标数据
            detailed_metrics = {}
            for service_name, config in metrics.items():
                if service_name != 'status':  # status是基础状态查询
                    query = config.get('query', '')
                    result = await prometheus_service.query_instant(query)
                    detailed_metrics[service_name] = {
                        'description': config.get('description', ''),
                        'query': query,
                        'result': result
                    }
            
            component_data['detailed_metrics'] = detailed_metrics
            return component_data
            
        except Exception as e:
            logger.error(f"获取组件{component_name}详情失败: {e}")
            return {'error': str(e)}
    
    async def get_realtime_metrics(self, nodes: Optional[List[str]] = None, 
                                 metrics: Optional[List[str]] = None) -> Dict:
        """获取实时指标"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'nodes': {},
                'components': {}
            }
            
            # 获取主机指标
            if not metrics or 'host' in metrics:
                host_metrics = await prometheus_service.get_host_metrics()
                if nodes:
                    host_metrics = [node for node in host_metrics 
                                  if any(node_filter in node.get('instance', '') for node_filter in nodes)]
                data['nodes'] = host_metrics
            
            # 获取组件指标
            if not metrics or 'components' in metrics:
                components = await self.get_components_overview()
                data['components'] = components
            
            return data
            
        except Exception as e:
            logger.error(f"获取实时指标失败: {e}")
            return {'error': str(e)}

# 创建全局实例
cluster_service = ClusterService()