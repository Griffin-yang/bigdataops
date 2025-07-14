from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from app.business.services.business_service import BusinessService
from app.utils.logger import logger

router = APIRouter(prefix="/business", tags=["business"])

business_service = BusinessService()

@router.get("/clusters")
async def get_clusters():
    """获取可用的集群列表"""
    try:
        clusters = await business_service.get_available_clusters()
        return {
            "code": 0,
            "msg": "success",
            "data": clusters
        }
    except Exception as e:
        logger.error(f"获取集群列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_business_overview(
    cluster_name: str = Query(..., description="集群名称"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """获取业务监控概览数据"""
    try:
        # 默认查询昨天的数据
        if not start_date or not end_date:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = yesterday.strftime("%Y-%m-%d")
        
        overview = await business_service.get_business_overview(
            cluster_name, start_date, end_date
        )
        return {
            "code": 0,
            "msg": "success",
            "data": overview
        }
    except Exception as e:
        logger.error(f"获取业务概览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/failed-jobs")
async def get_failed_jobs(
    cluster_name: str = Query(..., description="集群名称"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, description="页码"),
    size: int = Query(20, description="每页数量")
):
    """获取失败任务列表"""
    try:
        # 默认查询昨天的数据
        if not start_date or not end_date:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = yesterday.strftime("%Y-%m-%d")
            
        failed_jobs = await business_service.get_failed_jobs(
            cluster_name, start_date, end_date, page, size
        )
        return {
            "code": 0,
            "msg": "success",
            "data": failed_jobs
        }
    except Exception as e:
        logger.error(f"获取失败任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-duration-jobs")
async def get_top_duration_jobs(
    cluster_name: str = Query(..., description="集群名称"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取执行时间最长的任务排行榜"""
    try:
        # 默认查询昨天的数据
        if not start_date or not end_date:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = yesterday.strftime("%Y-%m-%d")
            
        top_jobs = await business_service.get_top_duration_jobs(
            cluster_name, start_date, end_date, limit
        )
        return {
            "code": 0,
            "msg": "success",
            "data": top_jobs
        }
    except Exception as e:
        logger.error(f"获取任务执行时间排行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics(
    cluster_name: str = Query(..., description="集群名称"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """获取业务统计数据"""
    try:
        # 默认查询昨天的数据
        if not start_date or not end_date:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = yesterday.strftime("%Y-%m-%d")
            
        stats = await business_service.get_statistics(
            cluster_name, start_date, end_date
        )
        return {
            "code": 0,
            "msg": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

 