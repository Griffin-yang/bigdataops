from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    项目全局配置，仅保留数据库、Prometheus、定时任务、服务启动等参数。
    下游告警相关参数（如邮箱、企业微信、HTTP等）应由前端配置并存数据库模板，config.py仅作兜底或本地调试用。
    """
    # LDAP 配置（如需本地调试可保留）
    ldap_server: str = "ldap://192.168.132.42:1389"
    ldap_user: str = "cn=admin,dc=dp,dc=leyoujia,dc=com"
    ldap_password: str = "AaaaBbbb@123"
    ldap_base_dn: str = "ou=People,dc=dp,dc=leyoujia,dc=com"
    ldap_group_dn: str = "ou=Group,dc=dp,dc=leyoujia,dc=com"

    # Prometheus配置
    prometheus_url: str = "http://172.16.3.233:9090/"

    # MySQL配置
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "alert"

    # APScheduler定时任务配置
    alert_engine_interval: int = 30  # 秒

    # 服务启动配置
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    uvicorn_reload: bool = True

    # ========== 业务监控配置 ==========
    
    # CDH集群配置 - Azkaban调度器
    azkaban_host: str = "172.16.3.233"
    azkaban_port: int = 34006
    azkaban_web_port: int = 34006  # Azkaban Web端口，用于构建查看链接
    azkaban_username: str = "zengan"
    azkaban_password: str = "za123"
    azkaban_web_url: str = "https://172.16.3.233:34006"  # Azkaban Web界面地址
    
    # CDH集群配置 - Azkaban数据库
    azkaban_db_host: str = "192.168.132.4"  # Azkaban数据库主机
    azkaban_db_port: int = 3306  # MySQL端口
    azkaban_db_database: str = "azkaban"  # Azkaban数据库名
    azkaban_db_username: str = "root"  # 数据库用户名
    azkaban_db_password: str = "cloudera9910"  # 数据库密码
    
    # CDH集群配置 - DolphinScheduler调度器数据库
    cdh_ds_host: str = "192.168.132.4"
    cdh_ds_port: int = 3306  # MySQL端口
    cdh_ds_database: str = "dolphinscheduler"
    cdh_ds_username: str = "root"
    cdh_ds_password: str = "cloudera9910"
    cdh_ds_web_url: str = "http://172.16.3.233:34152/dolphinscheduler"  # DS Web界面地址
    
    # Apache开源集群配置 - DolphinScheduler调度器数据库
    apache_ds_host: str = "192.168.132.41"
    apache_ds_port: int = 3306  # MySQL端口  
    apache_ds_database: str = "lyj_dolphinscheduler"
    apache_ds_username: str = "lyj_bd_wr"
    apache_ds_password: str = "kT1dF0aQ1a"
    apache_ds_web_url: str = "http://172.16.3.233:22345/dolphinscheduler"  # Apache DS Web界面地址
    
    # 业务监控通用配置
    business_monitoring_enabled: bool = True  # 是否启用业务监控
    default_query_days: int = 1  # 默认查询天数
    max_failed_jobs_display: int = 100  # 最大失败任务显示数量
    max_duration_jobs_display: int = 50  # 最大执行时间排行显示数量

    class Config:
        env_file = ".env"  # 仍支持.env，但本地调试可直接用默认值

@lru_cache
def get_settings():
    return Settings()

# 导出settings实例供其他模块使用
settings = get_settings() 