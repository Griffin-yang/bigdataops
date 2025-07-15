from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional
from .config_manager import config_manager


class Settings(BaseSettings):
    """
    项目全局配置，支持从config.env文件加载配置。
    配置加载优先级：环境变量 > 配置文件 > 默认值
    """
    
    # 环境标识
    environment: str = "development"
    
    # LDAP 配置
    ldap_server: str = "ldap://localhost:389"
    ldap_user: str = "cn=admin,dc=example,dc=com"
    ldap_password: str = "admin123"
    ldap_base_dn: str = "ou=People,dc=example,dc=com"
    ldap_group_dn: str = "ou=Group,dc=example,dc=com"

    # Prometheus配置
    prometheus_url: str = "http://localhost:9090/"

    # MySQL配置
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "bigdataops"

    # APScheduler定时任务配置
    alert_engine_interval: int = 30  # 秒

    # 服务启动配置
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    uvicorn_reload: bool = True

    # ========== 业务监控配置 ==========
    
    # CDH集群配置 - Azkaban调度器
    azkaban_host: str = "localhost"
    azkaban_port: int = 8081
    azkaban_web_port: int = 8081
    azkaban_username: str = "azkaban"
    azkaban_password: str = "azkaban"
    azkaban_web_url: str = "http://localhost:8081"
    
    # CDH集群配置 - Azkaban数据库
    azkaban_db_host: str = "localhost"
    azkaban_db_port: int = 3306
    azkaban_db_database: str = "azkaban"
    azkaban_db_username: str = "root"
    azkaban_db_password: str = "123456"
    
    # CDH集群配置 - DolphinScheduler调度器数据库
    cdh_ds_host: str = "localhost"
    cdh_ds_port: int = 3306
    cdh_ds_database: str = "dolphinscheduler"
    cdh_ds_username: str = "root"
    cdh_ds_password: str = "123456"
    cdh_ds_web_url: str = "http://localhost:12345/dolphinscheduler"
    
    # Apache开源集群配置 - DolphinScheduler调度器数据库
    apache_ds_host: str = "localhost"
    apache_ds_port: int = 3306
    apache_ds_database: str = "dolphinscheduler_apache"
    apache_ds_username: str = "root"
    apache_ds_password: str = "123456"
    apache_ds_web_url: str = "http://localhost:22345/dolphinscheduler"
    
    # 业务监控通用配置
    business_monitoring_enabled: bool = True
    default_query_days: int = 1
    max_failed_jobs_display: int = 100
    max_duration_jobs_display: int = 50

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_from_config_file()
    
    def _load_from_config_file(self):
        """从配置文件加载配置"""
        try:
            # 获取配置文件中的值
            config_data = config_manager.get_current_config()
            
            # 将配置文件中的值应用到实例属性
            for key, value in config_data.items():
                if hasattr(self, key.lower()):
                    # 处理布尔值
                    if value.lower() in ('true', 'false'):
                        setattr(self, key.lower(), value.lower() == 'true')
                    # 处理整数值
                    elif value.isdigit():
                        setattr(self, key.lower(), int(value))
                    # 处理字符串值
                    else:
                        setattr(self, key.lower(), value)
                        
        except Exception as e:
            # 如果配置文件加载失败，使用默认值
            print(f"警告: 配置文件加载失败，使用默认配置: {e}")

    class Config:
        env_file = ".env"  # 仍支持.env文件作为备用
        case_sensitive = False  # 不区分大小写


@lru_cache
def get_settings():
    return Settings()

# 导出settings实例供其他模块使用
settings = get_settings() 