import aiomysql
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from app.config import settings
from app.utils.logger import logger

class BusinessService:
    """业务监控服务"""
    
    def __init__(self):
        # 集群配置
        self.clusters_config = {
            "cdh": {
                "name": "CDH集群",
                "type": "cdh",
                "schedulers": ["azkaban"],
                "azkaban_config": {
                    "host": settings.azkaban_host,
                    "port": settings.azkaban_port,
                    "username": settings.azkaban_username,
                    "password": settings.azkaban_password,
                    "web_url": settings.azkaban_web_url,
                    "db_host": settings.azkaban_db_host,
                    "db_port": settings.azkaban_db_port,
                    "db_database": settings.azkaban_db_database,
                    "db_username": settings.azkaban_db_username,
                    "db_password": settings.azkaban_db_password
                }
            },
            "apache": {
                "name": "Apache开源集群",
                "type": "apache",
                "schedulers": ["dolphinscheduler"],
                "ds_config": {
                    "host": settings.apache_ds_host,
                    "port": settings.apache_ds_port,
                    "database": settings.apache_ds_database,
                    "username": settings.apache_ds_username,
                    "password": settings.apache_ds_password,
                    "web_url": settings.apache_ds_web_url
                }
            }
        }

    async def get_available_clusters(self) -> List[Dict[str, Any]]:
        """获取可用的集群列表"""
        clusters = []
        for cluster_id, config in self.clusters_config.items():
            clusters.append({
                "id": cluster_id,
                "name": config["name"],
                "type": config["type"],
                "schedulers": config["schedulers"]
            })
        return clusters

    async def get_business_overview(self, cluster_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取业务监控概览数据"""
        cluster_config = self.clusters_config.get(cluster_name)
        if not cluster_config:
            raise ValueError(f"未找到集群配置: {cluster_name}")

        # 初始化结果
        overview = {
            "cluster_name": cluster_config["name"],
            "date_range": f"{start_date} 至 {end_date}",
            "total_jobs": 0,
            "success_jobs": 0,
            "failed_jobs": 0,
            "success_rate": 0.0,
            "schedulers_stats": {}
        }

        try:
            # 根据集群类型获取数据
            if cluster_name == "cdh":
                # CDH集群：查询Azkaban
                azkaban_stats = await self._get_azkaban_stats(cluster_config["azkaban_config"], start_date, end_date)
                overview["schedulers_stats"]["azkaban"] = azkaban_stats
                overview["total_jobs"] = azkaban_stats["total_jobs"]
                overview["success_jobs"] = azkaban_stats["success_jobs"]
                overview["failed_jobs"] = azkaban_stats["failed_jobs"]
                
            elif cluster_name == "apache":
                # Apache集群：查询DolphinScheduler
                ds_stats = await self._get_dolphinscheduler_stats(cluster_config["ds_config"], start_date, end_date)
                overview["schedulers_stats"]["dolphinscheduler"] = ds_stats
                overview["total_jobs"] = ds_stats["total_jobs"]
                overview["success_jobs"] = ds_stats["success_jobs"]
                overview["failed_jobs"] = ds_stats["failed_jobs"]

            # 计算成功率
            if overview["total_jobs"] > 0:
                overview["success_rate"] = round((overview["success_jobs"] / overview["total_jobs"]) * 100, 2)

        except Exception as e:
            logger.error(f"获取业务概览失败: {e}")

        return overview

    async def get_failed_jobs(self, cluster_name: str, start_date: str, end_date: str, page: int, size: int) -> Dict[str, Any]:
        """获取失败任务列表"""
        cluster_config = self.clusters_config.get(cluster_name)
        if not cluster_config:
            raise ValueError(f"未找到集群配置: {cluster_name}")

        failed_jobs = []
        total = 0

        try:
            if cluster_name == "cdh":
                # CDH集群：查询Azkaban失败任务
                failed_jobs = await self._get_azkaban_failed_jobs(cluster_config["azkaban_config"], start_date, end_date)
                
            elif cluster_name == "apache":
                # Apache集群：查询DolphinScheduler失败任务
                failed_jobs = await self._get_dolphinscheduler_failed_jobs(cluster_config["ds_config"], start_date, end_date)

            # 排序并分页
            failed_jobs.sort(key=lambda x: x.get("execution_time", ""), reverse=True)
            total = len(failed_jobs)
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            failed_jobs = failed_jobs[start_idx:end_idx]

        except Exception as e:
            logger.error(f"获取失败任务列表失败: {e}")

        return {
            "items": failed_jobs,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    async def get_top_duration_jobs(self, cluster_name: str, start_date: str, end_date: str, limit: int) -> List[Dict[str, Any]]:
        """获取执行时间最长的任务排行榜"""
        cluster_config = self.clusters_config.get(cluster_name)
        if not cluster_config:
            raise ValueError(f"未找到集群配置: {cluster_name}")

        top_jobs = []

        try:
            if cluster_name == "cdh":
                # CDH集群：查询Azkaban任务
                top_jobs = await self._get_azkaban_duration_jobs(cluster_config["azkaban_config"], start_date, end_date)
                
            elif cluster_name == "apache":
                # Apache集群：查询DolphinScheduler任务
                top_jobs = await self._get_dolphinscheduler_duration_jobs(cluster_config["ds_config"], start_date, end_date)

            # 按执行时间排序并取前N个
            top_jobs.sort(key=lambda x: x.get("duration", 0), reverse=True)
            top_jobs = top_jobs[:limit]

        except Exception as e:
            logger.error(f"获取任务执行时间排行失败: {e}")

        return top_jobs

    async def get_statistics(self, cluster_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取统计数据"""
        cluster_config = self.clusters_config.get(cluster_name)
        if not cluster_config:
            raise ValueError(f"未找到集群配置: {cluster_name}")

        # 获取每日统计
        daily_stats = await self._get_daily_statistics(cluster_name, start_date, end_date)
        
        # 获取调度器分布
        scheduler_distribution = await self._get_scheduler_distribution(cluster_name, start_date, end_date)
        
        # 获取项目分布
        project_distribution = await self._get_project_distribution(cluster_name, start_date, end_date)

        return {
            "daily_statistics": daily_stats,
            "scheduler_distribution": scheduler_distribution,
            "project_distribution": project_distribution
        }

    # 数据库连接方法
    async def _get_ds_connection(self, config: Dict) -> Optional[aiomysql.Connection]:
        """获取DolphinScheduler数据库连接"""
        try:
            connection = await aiomysql.connect(
                host=config["host"],
                port=config["port"],
                user=config["username"],
                password=config["password"],
                db=config["database"],
                charset='utf8mb4',
                connect_timeout=10
            )
            return connection
        except Exception as e:
            logger.error(f"连接DolphinScheduler数据库失败: {e}")
            return None

    async def _get_azkaban_connection(self, config: Dict) -> Optional[aiomysql.Connection]:
        """获取Azkaban数据库连接"""
        try:
            connection = await aiomysql.connect(
                host=config["db_host"],
                port=config["db_port"],
                user=config["db_username"],
                password=config["db_password"],
                db=config["db_database"],
                charset='utf8mb4',
                connect_timeout=10
            )
            return connection
        except Exception as e:
            logger.error(f"连接Azkaban数据库失败: {e}")
            return None

    # Azkaban相关方法
    async def _get_azkaban_stats(self, config: Dict, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取Azkaban统计数据"""
        try:
            connection = await self._get_azkaban_connection(config)
            if not connection:
                return {"total_jobs": 0, "success_jobs": 0, "failed_jobs": 0, "source": "azkaban"}
            
            # 查询时间范围内的工作流执行统计
            query = """
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN status = 50 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN status IN (60, 70, 80) THEN 1 ELSE 0 END) as failed_jobs
            FROM execution_flows 
            WHERE start_time >= %s AND start_time <= %s
            AND start_time IS NOT NULL
            """
            
            # 转换日期为时间戳（毫秒）
            try:
                start_timestamp = int(datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
                end_timestamp = int(datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            except Exception as date_error:
                logger.error(f"Azkaban日期转换失败: {date_error}")
                connection.close()
                return {"total_jobs": 0, "success_jobs": 0, "failed_jobs": 0, "source": "azkaban"}
            
            async with connection.cursor() as cursor:
                await cursor.execute(query, (start_timestamp, end_timestamp))
                result = await cursor.fetchone()
                
                total_jobs = result[0] if result and result[0] else 0
                success_jobs = result[1] if result and result[1] else 0
                failed_jobs = result[2] if result and result[2] else 0
                
            connection.close()
            
            logger.info(f"获取Azkaban统计数据: 总任务{total_jobs}, 成功{success_jobs}, 失败{failed_jobs}")
            
            return {
                "total_jobs": total_jobs,
                "success_jobs": success_jobs,
                "failed_jobs": failed_jobs,
                "source": "azkaban"
            }
            
        except Exception as e:
            logger.error(f"获取Azkaban统计数据失败: {e}")
            return {"total_jobs": 0, "success_jobs": 0, "failed_jobs": 0, "source": "azkaban"}

    async def _get_azkaban_failed_jobs(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取Azkaban失败任务"""
        try:
            connection = await self._get_azkaban_connection(config)
            if not connection:
                return []
            
            # 查询失败的工作流执行记录
            query = """
            SELECT 
                ef.exec_id,
                ef.flow_id,
                p.name as project_name,
                ef.start_time,
                ef.end_time,
                ef.status,
                ef.submit_user
            FROM execution_flows ef
            JOIN projects p ON ef.project_id = p.id
            WHERE ef.status IN (60, 70, 80)  -- FAILED, KILLED, CANCELLED
            AND ef.start_time >= %s AND ef.start_time <= %s
            ORDER BY ef.start_time DESC
            LIMIT 200
            """
            
            # 转换日期为时间戳
            start_timestamp = int(datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            
            async with connection.cursor() as cursor:
                await cursor.execute(query, (start_timestamp, end_timestamp))
                results = await cursor.fetchall()
                
                failed_jobs = []
                for result in results:
                    exec_id, flow_id, project_name, start_time, end_time, status, submit_user = result
                    
                    # 计算执行时间
                    duration = 0
                    if end_time and start_time:
                        duration = int((end_time - start_time) / 1000)
                    
                    # 状态映射
                    status_map = {60: "FAILED", 70: "KILLED", 80: "CANCELLED"}
                    status_str = status_map.get(status, "UNKNOWN")
                    
                    # 转换时间戳为可读时间
                    start_time_readable = datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    
                    failed_jobs.append({
                        "job_id": str(exec_id),
                        "job_name": flow_id,
                        "project_name": project_name or "未知项目",
                        "execution_time": start_time_readable,
                        "duration": duration,
                        "status": status_str,
                        "submit_user": submit_user or "未知用户",
                        "error_message": f"工作流执行{status_str}",
                        "scheduler": "azkaban",
                        "scheduler_type": "Azkaban",
                        "view_url": f"{config['web_url']}/executor?execid={exec_id}"
                    })
                
            connection.close()
            return failed_jobs
            
        except Exception as e:
            logger.error(f"获取Azkaban失败任务失败: {e}")
            return []

    async def _get_azkaban_duration_jobs(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取Azkaban任务执行时间数据"""
        try:
            connection = await self._get_azkaban_connection(config)
            if not connection:
                return []
            
            # 查询成功的工作流执行记录，按执行时间排序
            query = """
            SELECT 
                ef.exec_id,
                ef.flow_id,
                p.name as project_name,
                ef.start_time,
                ef.end_time,
                ef.status,
                ef.submit_user
            FROM execution_flows ef
            JOIN projects p ON ef.project_id = p.id
            WHERE ef.status = 50  -- SUCCEEDED
            AND ef.start_time >= %s AND ef.start_time <= %s
            AND ef.end_time IS NOT NULL
            AND ef.end_time > ef.start_time
            ORDER BY (ef.end_time - ef.start_time) DESC
            LIMIT 100
            """
            
            # 转换日期为时间戳
            start_timestamp = int(datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            
            async with connection.cursor() as cursor:
                await cursor.execute(query, (start_timestamp, end_timestamp))
                results = await cursor.fetchall()
                
                duration_jobs = []
                for result in results:
                    exec_id, flow_id, project_name, start_time, end_time, status, submit_user = result
                    
                    # 计算执行时间
                    duration = 0
                    if end_time and start_time:
                        duration = int((end_time - start_time) / 1000)
                    
                    if duration > 0:
                        # 转换时间戳为可读时间
                        start_time_readable = datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
                        
                        duration_jobs.append({
                            "job_id": str(exec_id),
                            "job_name": flow_id,
                            "project_name": project_name or "未知项目",
                            "execution_time": start_time_readable,
                            "duration": duration,
                            "status": "SUCCEEDED",
                            "submit_user": submit_user or "未知用户",
                            "scheduler": "azkaban",
                            "scheduler_type": "Azkaban",
                            "view_url": f"{config['web_url']}/executor?execid={exec_id}"
                        })
                
            connection.close()
            return duration_jobs
            
        except Exception as e:
            logger.error(f"获取Azkaban执行时间数据失败: {e}")
            return []

    # DolphinScheduler相关方法
    async def _get_dolphinscheduler_stats(self, config: Dict, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取DolphinScheduler统计数据"""
        try:
            connection = await self._get_ds_connection(config)
            if not connection:
                return {"total_jobs": 0, "success_jobs": 0, "failed_jobs": 0, "source": "dolphinscheduler"}
            
            # 简化查询，不依赖关联表
            query = """
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_jobs
            FROM t_ds_process_instance 
            WHERE DATE(start_time) >= %s AND DATE(start_time) <= %s
            """
            
            async with connection.cursor() as cursor:
                logger.info(f"DolphinScheduler查询日期范围: {start_date} 到 {end_date}")
                await cursor.execute(query, (start_date, end_date))
                result = await cursor.fetchone()
                
                total_jobs = result[0] if result and result[0] else 0
                success_jobs = result[1] if result and result[1] else 0
                failed_jobs = result[2] if result and result[2] else 0
                
            connection.close()
            
            logger.info(f"获取DolphinScheduler统计数据({config.get('database', 'unknown')}): 总任务{total_jobs}, 成功{success_jobs}, 失败{failed_jobs}")
            
            return {
                "total_jobs": total_jobs,
                "success_jobs": success_jobs,
                "failed_jobs": failed_jobs,
                "source": "dolphinscheduler"
            }
            
        except Exception as e:
            logger.error(f"获取DolphinScheduler统计数据失败: {e}")
            return {"total_jobs": 0, "success_jobs": 0, "failed_jobs": 0, "source": "dolphinscheduler"}

    async def _get_dolphinscheduler_failed_jobs(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取DolphinScheduler失败任务"""
        try:
            connection = await self._get_ds_connection(config)
            if not connection:
                return []
            
            # 简化查询，不依赖关联表
            query = """
            SELECT 
                pi.id,
                pi.name,
                pi.start_time,
                pi.end_time,
                pi.state
            FROM t_ds_process_instance pi
            WHERE pi.state IN (6, 9, 10)  -- FAILURE, KILL, STOP
            AND DATE(pi.start_time) >= %s AND DATE(pi.start_time) <= %s
            ORDER BY pi.start_time DESC
            LIMIT 200
            """
            
            async with connection.cursor() as cursor:
                logger.info(f"DolphinScheduler查询失败任务，日期范围: {start_date} 到 {end_date}")
                await cursor.execute(query, (start_date, end_date))
                results = await cursor.fetchall()
                
                failed_jobs = []
                for result in results:
                    instance_id, name, start_time, end_time, state = result
                    
                    # 计算执行时间
                    duration = 0
                    if end_time and start_time:
                        duration = int((end_time - start_time).total_seconds())
                    
                    # 状态映射
                    status_map = {6: "FAILURE", 9: "KILL", 10: "STOP"}
                    status = status_map.get(state, "UNKNOWN")
                    
                    # 安全地格式化时间
                    execution_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "未知"
                    
                    failed_jobs.append({
                        "job_id": str(instance_id),
                        "job_name": name or f"任务_{instance_id}",
                        "project_name": "DolphinScheduler项目",
                        "execution_time": execution_time_str,
                        "duration": duration,
                        "status": status,
                        "error_message": f"工作流执行{status}",
                        "scheduler": "dolphinscheduler",
                        "scheduler_type": "DolphinScheduler",
                        "view_url": f"{config['web_url']}/projects/0/process-instances/{instance_id}"
                    })
                
            connection.close()
            logger.info(f"DolphinScheduler找到 {len(failed_jobs)} 个失败任务")
            return failed_jobs
            
        except Exception as e:
            logger.error(f"获取DolphinScheduler失败任务失败: {e}")
            return []

    async def _get_dolphinscheduler_duration_jobs(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取DolphinScheduler任务执行时间数据"""
        try:
            connection = await self._get_ds_connection(config)
            if not connection:
                return []
            
            # 简化查询，不依赖关联表
            query = """
            SELECT 
                pi.id,
                pi.name,
                pi.start_time,
                pi.end_time,
                pi.state,
                TIMESTAMPDIFF(SECOND, pi.start_time, pi.end_time) as duration_seconds
            FROM t_ds_process_instance pi
            WHERE pi.state = 7  -- SUCCESS
            AND DATE(pi.start_time) >= %s AND DATE(pi.start_time) <= %s
            AND pi.end_time IS NOT NULL
            AND pi.start_time IS NOT NULL
            AND pi.end_time > pi.start_time
            ORDER BY duration_seconds DESC
            LIMIT 100
            """
            
            async with connection.cursor() as cursor:
                logger.info(f"DolphinScheduler查询执行时间排行，日期范围: {start_date} 到 {end_date}")
                await cursor.execute(query, (start_date, end_date))
                results = await cursor.fetchall()
                
                duration_jobs = []
                for result in results:
                    instance_id, name, start_time, end_time, state, duration_seconds = result
                    
                    # 使用数据库计算的执行时间
                    duration = duration_seconds if duration_seconds and duration_seconds > 0 else 0
                    
                    # 安全地格式化时间
                    execution_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "未知"
                    
                    duration_jobs.append({
                        "job_id": str(instance_id),
                        "job_name": name or f"任务_{instance_id}",
                        "project_name": "DolphinScheduler项目",
                        "execution_time": execution_time_str,
                        "duration": duration,
                        "status": "SUCCESS",
                        "scheduler": "dolphinscheduler",
                        "scheduler_type": "DolphinScheduler",
                        "view_url": f"{config['web_url']}/projects/0/process-instances/{instance_id}"
                    })
                
            connection.close()
            logger.info(f"DolphinScheduler找到 {len(duration_jobs)} 个执行时间排行任务")
            return duration_jobs
            
        except Exception as e:
            logger.error(f"获取DolphinScheduler执行时间数据失败: {e}")
            return []

    async def _get_daily_statistics(self, cluster_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取每日统计数据"""
        try:
            cluster_config = self.clusters_config.get(cluster_name)
            daily_stats = []
            
            # 生成日期范围
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            current_date = start_dt
            
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y-%m-%d")
                
                total_jobs = 0
                success_jobs = 0
                failed_jobs = 0
                
                # 获取当日数据
                if cluster_name == "cdh":
                    # CDH集群：查询Azkaban
                    azkaban_stats = await self._get_azkaban_stats(cluster_config["azkaban_config"], date_str, date_str)
                    total_jobs = azkaban_stats["total_jobs"]
                    success_jobs = azkaban_stats["success_jobs"]
                    failed_jobs = azkaban_stats["failed_jobs"]
                    
                elif cluster_name == "apache":
                    # Apache集群：查询DolphinScheduler
                    ds_stats = await self._get_dolphinscheduler_stats(cluster_config["ds_config"], date_str, date_str)
                    total_jobs = ds_stats["total_jobs"]
                    success_jobs = ds_stats["success_jobs"]
                    failed_jobs = ds_stats["failed_jobs"]
                
                success_rate = round((success_jobs / total_jobs) * 100, 2) if total_jobs > 0 else 0
                
                daily_stats.append({
                    "date": date_str,
                    "total_jobs": total_jobs,
                    "success_jobs": success_jobs,
                    "failed_jobs": failed_jobs,
                    "success_rate": success_rate
                })
                
                current_date += timedelta(days=1)
            
            return daily_stats
            
        except Exception as e:
            logger.error(f"获取每日统计数据失败: {e}")
            return []

    async def _get_scheduler_distribution(self, cluster_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取调度器分布统计"""
        try:
            cluster_config = self.clusters_config.get(cluster_name)
            
            if cluster_name == "cdh":
                # CDH集群：查询Azkaban
                azkaban_stats = await self._get_azkaban_stats(cluster_config["azkaban_config"], start_date, end_date)
                
                if azkaban_stats["total_jobs"] > 0:
                    return [
                        {
                            "scheduler": "azkaban",
                            "scheduler_name": "Azkaban",
                            "job_count": azkaban_stats["total_jobs"],
                            "percentage": 100.0
                        }
                    ]
                    
            elif cluster_name == "apache":
                # Apache集群：查询DolphinScheduler
                ds_stats = await self._get_dolphinscheduler_stats(cluster_config["ds_config"], start_date, end_date)
                
                if ds_stats["total_jobs"] > 0:
                    return [
                        {
                            "scheduler": "dolphinscheduler",
                            "scheduler_name": "DolphinScheduler",
                            "job_count": ds_stats["total_jobs"],
                            "percentage": 100.0
                        }
                    ]
            
            return []
            
        except Exception as e:
            logger.error(f"获取调度器分布统计失败: {e}")
            return []

    async def _get_project_distribution(self, cluster_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取项目分布数据"""
        try:
            cluster_config = self.clusters_config.get(cluster_name)
            if not cluster_config:
                return []
            
            distribution = []
            
            if cluster_name == "cdh":
                # CDH集群：获取Azkaban项目分布
                azkaban_distribution = await self._get_azkaban_project_distribution(cluster_config["azkaban_config"], start_date, end_date)
                distribution.extend(azkaban_distribution)
                
            elif cluster_name == "apache":
                # Apache集群：获取DolphinScheduler项目分布
                ds_distribution = await self._get_ds_project_distribution(cluster_config["ds_config"], start_date, end_date)
                distribution.extend(ds_distribution)
            
            return distribution
            
        except Exception as e:
            logger.error(f"获取项目分布数据失败: {e}")
            return []

    async def _get_azkaban_project_distribution(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取Azkaban项目分布数据"""
        try:
            connection = await self._get_azkaban_connection(config)
            if not connection:
                return []
            
            query = """
            SELECT 
                p.name as project_name,
                COUNT(*) as total_jobs,
                SUM(CASE WHEN ef.status = 50 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN ef.status IN (60, 70, 80) THEN 1 ELSE 0 END) as failed_jobs
            FROM execution_flows ef
            JOIN projects p ON ef.project_id = p.id
            WHERE ef.start_time >= %s AND ef.start_time <= %s
            GROUP BY p.id, p.name
            ORDER BY total_jobs DESC
            LIMIT 10
            """
            
            # 转换日期为时间戳
            start_timestamp = int(datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            end_timestamp = int(datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            
            async with connection.cursor() as cursor:
                await cursor.execute(query, (start_timestamp, end_timestamp))
                results = await cursor.fetchall()
                
                distribution = []
                for result in results:
                    project_name, total_jobs, success_jobs, failed_jobs = result
                    distribution.append({
                        "name": project_name,
                        "value": total_jobs,
                        "success": success_jobs,
                        "failed": failed_jobs,
                        "scheduler": "Azkaban"
                    })
                
            connection.close()
            return distribution
            
        except Exception as e:
            logger.error(f"获取Azkaban项目分布数据失败: {e}")
            return []

    async def _get_ds_project_distribution(self, config: Dict, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取DolphinScheduler项目分布数据"""
        try:
            connection = await self._get_ds_connection(config)
            if not connection:
                return []
            
            # 简化查询，不依赖关联表
            query = """
            SELECT 
                'DolphinScheduler项目' as project_name,
                COUNT(*) as total_jobs,
                SUM(CASE WHEN pi.state = 7 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN pi.state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_jobs
            FROM t_ds_process_instance pi
            WHERE DATE(pi.start_time) >= %s AND DATE(pi.start_time) <= %s
            """
            
            async with connection.cursor() as cursor:
                logger.info(f"DolphinScheduler查询项目分布，日期范围: {start_date} 到 {end_date}")
                await cursor.execute(query, (start_date, end_date))
                results = await cursor.fetchall()
                
                distribution = []
                for result in results:
                    project_name, total_jobs, success_jobs, failed_jobs = result
                    if total_jobs > 0:  # 只有有数据时才添加
                        distribution.append({
                            "name": project_name or "未知项目",
                            "value": total_jobs,
                            "success": success_jobs,
                            "failed": failed_jobs,
                            "scheduler": "DolphinScheduler"
                        })
                
            connection.close()
            logger.info(f"DolphinScheduler找到 {len(distribution)} 个项目分布")
            return distribution
            
        except Exception as e:
            logger.error(f"获取DolphinScheduler项目分布数据失败: {e}")
            return [] 