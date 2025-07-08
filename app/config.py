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
    prometheus_url: str = "http://localhost:9090"

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

    class Config:
        env_file = ".env"  # 仍支持.env，但本地调试可直接用默认值

@lru_cache
def get_settings():
    return Settings() 