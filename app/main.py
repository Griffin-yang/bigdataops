from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.alert.controllers import rule_controller, notify_template_controller, history_controller, alert_controller
from app.ldap.controllers import ldap_controller
from app.alert.services.engine_service import start_alert_engine, stop_alert_engine
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("BigDataOps 应用启动中...")
    try:
        # 启动告警引擎
        start_alert_engine()
        logger.info("告警引擎已自动启动")
    except Exception as e:
        logger.error(f"启动告警引擎失败: {e}")
    
    logger.info("BigDataOps 应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("BigDataOps 应用正在关闭...")
    try:
        # 停止告警引擎
        stop_alert_engine()
        logger.info("告警引擎已停止")
    except Exception as e:
        logger.error(f"停止告警引擎失败: {e}")
    logger.info("BigDataOps 应用关闭完成")

app = FastAPI(
    title="BigDataOps API",
    description="大数据运维管理平台 API",
    version="1.0.0",
    lifespan=lifespan
)

# 注册路由
app.include_router(rule_controller.router, prefix="/api", tags=["告警规则"])
app.include_router(notify_template_controller.router, prefix="/api", tags=["通知模板"])
app.include_router(history_controller.router, prefix="/api", tags=["告警历史"])
app.include_router(alert_controller.router, prefix="/api", tags=["告警引擎"])
app.include_router(ldap_controller.router, prefix="/api", tags=["LDAP管理"])

# 集群监控路由
from app.cluster.controllers.cluster_controller import router as cluster_router
app.include_router(cluster_router, prefix="/api", tags=["集群监控"])

# 业务监控路由
from app.business.controllers.business_controller import router as business_router
app.include_router(business_router, prefix="/api", tags=["业务监控"])

@app.get("/")
async def root():
    return {"message": "BigDataOps API 运行正常"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "BigDataOps"} 