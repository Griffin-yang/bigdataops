#!/usr/bin/env python3
"""
业务监控功能测试脚本
测试各个接口的连通性和功能
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

async def test_business_monitoring():
    """测试业务监控所有接口"""
    
    print("开始测试业务监控功能...")
    
    async with aiohttp.ClientSession() as session:
        # 1. 测试获取集群列表
        print("\n1. 测试获取集群列表")
        try:
            async with session.get(f"{BASE_URL}/business/clusters") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 获取集群列表成功: {data}")
                    clusters = data.get('data', [])
                    
                    if not clusters:
                        print("❌ 没有可用的集群")
                        return
                    
                    # 测试每个集群
                    for cluster in clusters:
                        cluster_id = cluster['id']
                        cluster_name = cluster['name']
                        schedulers = cluster['schedulers']
                        
                        print(f"\n测试集群: {cluster_name} (ID: {cluster_id})")
                        print(f"调度器: {', '.join(schedulers)}")
                        
                        # 设置测试时间范围（昨天）
                        yesterday = datetime.now() - timedelta(days=1)
                        start_date = yesterday.strftime("%Y-%m-%d")
                        end_date = yesterday.strftime("%Y-%m-%d")
                        
                        await test_cluster_apis(session, cluster_id, start_date, end_date)
                else:
                    print(f"❌ 获取集群列表失败: HTTP {response.status}")
        except Exception as e:
            print(f"❌ 获取集群列表异常: {e}")

async def test_cluster_apis(session, cluster_id, start_date, end_date):
    """测试特定集群的所有API"""
    
    params = {
        "cluster_name": cluster_id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    # 2. 测试业务概览
    print(f"  2. 测试业务概览")
    try:
        async with session.get(f"{BASE_URL}/business/overview", params=params) as response:
            if response.status == 200:
                data = await response.json()
                overview = data.get('data', {})
                print(f"  ✅ 业务概览: 总任务{overview.get('total_jobs', 0)}, "
                      f"成功{overview.get('success_jobs', 0)}, "
                      f"失败{overview.get('failed_jobs', 0)}")
            else:
                text = await response.text()
                print(f"  ❌ 业务概览失败: HTTP {response.status}, {text}")
    except Exception as e:
        print(f"  ❌ 业务概览异常: {e}")
    
    # 3. 测试失败任务列表
    print(f"  3. 测试失败任务列表")
    try:
        async with session.get(f"{BASE_URL}/business/failed-jobs", params=params) as response:
            if response.status == 200:
                data = await response.json()
                failed_jobs = data.get('data', {})
                print(f"  ✅ 失败任务: 共{failed_jobs.get('total', 0)}个")
            else:
                text = await response.text()
                print(f"  ❌ 失败任务失败: HTTP {response.status}, {text}")
    except Exception as e:
        print(f"  ❌ 失败任务异常: {e}")
    
    # 4. 测试执行时间排行
    print(f"  4. 测试执行时间排行")
    try:
        async with session.get(f"{BASE_URL}/business/top-duration-jobs", params=params) as response:
            if response.status == 200:
                data = await response.json()
                top_jobs = data.get('data', [])
                print(f"  ✅ 执行时间排行: 共{len(top_jobs)}个任务")
            else:
                text = await response.text()
                print(f"  ❌ 执行时间排行失败: HTTP {response.status}, {text}")
    except Exception as e:
        print(f"  ❌ 执行时间排行异常: {e}")
    
    # 5. 测试统计数据
    print(f"  5. 测试统计数据")
    try:
        async with session.get(f"{BASE_URL}/business/statistics", params=params) as response:
            if response.status == 200:
                data = await response.json()
                stats = data.get('data', {})
                daily_stats = stats.get('daily_statistics', [])
                scheduler_dist = stats.get('scheduler_distribution', [])
                print(f"  ✅ 统计数据: 每日统计{len(daily_stats)}天, "
                      f"调度器分布{len(scheduler_dist)}个")
            else:
                text = await response.text()
                print(f"  ❌ 统计数据失败: HTTP {response.status}, {text}")
    except Exception as e:
        print(f"  ❌ 统计数据异常: {e}")

async def test_database_connections():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        from app.config import settings
        from app.business.services.business_service import BusinessService
        
        service = BusinessService()
        
        # 测试CDH集群的Azkaban数据库连接
        print("  测试CDH集群Azkaban数据库连接...")
        try:
            connection = await service._get_azkaban_connection(service.clusters_config["cdh"]["azkaban_config"])
            await connection.close()
            print("  ✅ CDH Azkaban数据库连接成功")
        except Exception as e:
            print(f"  ❌ CDH Azkaban数据库连接失败: {e}")
        
        # 测试CDH集群的DolphinScheduler数据库连接
        print("  测试CDH集群DolphinScheduler数据库连接...")
        try:
            connection = await service._get_ds_connection(service.clusters_config["cdh"]["ds_config"])
            await connection.close()
            print("  ✅ CDH DolphinScheduler数据库连接成功")
        except Exception as e:
            print(f"  ❌ CDH DolphinScheduler数据库连接失败: {e}")
        
        # 测试Apache集群的DolphinScheduler数据库连接
        print("  测试Apache集群DolphinScheduler数据库连接...")
        try:
            connection = await service._get_ds_connection(service.clusters_config["apache"]["ds_config"])
            await connection.close()
            print("  ✅ Apache DolphinScheduler数据库连接成功")
        except Exception as e:
            print(f"  ❌ Apache DolphinScheduler数据库连接失败: {e}")
            
    except Exception as e:
        print(f"  ❌ 数据库连接测试异常: {e}")

async def main():
    """主函数"""
    print("=" * 60)
    print("业务监控功能完整测试")
    print("=" * 60)
    
    # 首先测试数据库连接
    await test_database_connections()
    
    # 然后测试API接口
    await test_business_monitoring()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 