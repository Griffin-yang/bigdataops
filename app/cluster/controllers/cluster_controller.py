from fastapi import APIRouter, Query
from typing import List, Optional
from app.cluster.services.cluster_service import cluster_service
from app.models.alert_schemas import CommonResponse
from app.utils.logger import logger

router = APIRouter()

@router.get("/cluster/overview", response_model=CommonResponse[dict])
async def get_cluster_overview():
    """获取集群总览信息"""
    try:
        overview = await cluster_service.get_cluster_overview()
        return {
            "code": 0,
            "data": overview,
            "msg": "查询成功"
        }
    except Exception as e:
        logger.error(f"获取集群总览失败: {e}")
        return {
            "code": 1,
            "data": None,
            "msg": f"查询失败: {str(e)}"
        }

@router.get("/cluster/nodes", response_model=CommonResponse[dict])
async def get_cluster_nodes(
    status: Optional[str] = Query(None, description="节点状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """获取集群节点列表"""
    try:
        all_nodes = await cluster_service.get_nodes_list(status)
        
        total = len(all_nodes)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        nodes = all_nodes[start_idx:end_idx]
        
        return {
            "code": 0,
            "data": {
                "items": nodes,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "msg": "查询成功"
        }
    except Exception as e:
        logger.error(f"获取集群节点失败: {e}")
        return {
            "code": 1,
            "data": None,
            "msg": f"查询失败: {str(e)}"
        }

@router.get("/cluster/components", response_model=CommonResponse[dict])
async def get_cluster_components():
    """获取所有大数据组件概览"""
    try:
        components = await cluster_service.get_components_overview()
        return {
            "code": 0,
            "data": {"components": components},
            "msg": "查询成功"
        }
    except Exception as e:
        logger.error(f"获取组件概览失败: {e}")
        return {
            "code": 1,
            "data": None,
            "msg": f"查询失败: {str(e)}"
        }

@router.get("/cluster/components/{component_name}", response_model=CommonResponse[dict])
async def get_component_detail(component_name: str):
    """获取特定组件的详细信息"""
    try:
        component_detail = await cluster_service.get_component_detail(component_name)
        
        if "error" in component_detail:
            return {
                "code": 1,
                "data": None,
                "msg": component_detail["error"]
            }
            
        return {
            "code": 0,
            "data": component_detail,
            "msg": "查询成功"
        }
    except Exception as e:
        logger.error(f"获取组件详情失败: {e}")
        return {
            "code": 1,
            "data": None,
            "msg": f"查询失败: {str(e)}"
        }

@router.get("/cluster/health")
async def cluster_health_check():
    """集群健康检查接口"""
    try:
        overview = await cluster_service.get_cluster_overview()
        
        total_nodes = overview.get("total_nodes", 0)
        healthy_nodes = overview.get("healthy_nodes", 0)
        
        if total_nodes == 0:
            status = "unknown"
            message = "无法获取节点信息"
        elif healthy_nodes == total_nodes:
            status = "healthy"
            message = "集群状态良好"
        elif healthy_nodes > total_nodes * 0.8:
            status = "warning" 
            message = "部分节点异常"
        else:
            status = "critical"
            message = "集群状态异常"
            
        return {
            "code": 0,
            "data": {
                "status": status,
                "message": message,
                "details": {
                    "total_nodes": total_nodes,
                    "healthy_nodes": healthy_nodes,
                    "unhealthy_nodes": overview.get("unhealthy_nodes", 0),
                    "avg_cpu_usage": overview.get("avg_cpu_usage", 0),
                    "avg_memory_usage": overview.get("avg_memory_usage", 0)
                }
            },
            "msg": "健康检查完成"
        }
    except Exception as e:
        logger.error(f"集群健康检查失败: {e}")
        return {
            "code": 1,
            "data": {
                "status": "error",
                "message": f"健康检查失败: {str(e)}"
            },
            "msg": "健康检查失败"
        }