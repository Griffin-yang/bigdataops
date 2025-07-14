#!/usr/bin/env python3
"""
测试CDH集群业务监控接口调用
验证前端选择CDH集群后的接口是否正确
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

async def test_cdh_cluster_specific():
    """专门测试CDH集群的接口调用"""
    
    print("=" * 60)
    print("测试CDH集群业务监控接口调用")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 首先获取集群列表，确认CDH集群存在
        print("\n1. 验证CDH集群配置")
        try:
            async with session.get(f"{BASE_URL}/business/clusters") as response:
                if response.status == 200:
                    data = await response.json()
                    clusters = data.get('data', [])
                    
                    # 查找CDH集群
                    cdh_cluster = None
                    for cluster in clusters:
                        if cluster['id'] == 'cdh':
                            cdh_cluster = cluster
                            break
                    
                    if cdh_cluster:
                        print(f"✅ 找到CDH集群: {cdh_cluster['name']}")
                        print(f"   调度器: {', '.join(cdh_cluster['schedulers'])}")
                        print(f"   类型: {cdh_cluster['type']}")
                        
                        # 验证调度器配置
                        if 'azkaban' in cdh_cluster['schedulers'] and 'dolphinscheduler' in cdh_cluster['schedulers']:
                            print("✅ CDH集群配置正确：支持Azkaban + DolphinScheduler")
                        else:
                            print("❌ CDH集群配置错误：应该支持Azkaban + DolphinScheduler")
                            return
                    else:
                        print("❌ 未找到CDH集群配置")
                        return
                else:
                    print(f"❌ 获取集群列表失败: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"❌ 获取集群列表异常: {e}")
            return
        
        # 2. 测试CDH集群的所有接口
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = yesterday.strftime("%Y-%m-%d")
        
        print(f"\n2. 测试CDH集群接口 (查询日期: {start_date})")
        
        # 构建查询参数
        params = {
            "cluster_name": "cdh",
            "start_date": start_date,
            "end_date": end_date
        }
        
        # 2.1 测试业务概览
        print("\n  2.1 测试业务概览接口")
        await test_api_endpoint(session, "/business/overview", params, "业务概览")
        
        # 2.2 测试失败任务列表
        print("\n  2.2 测试失败任务列表接口")
        failed_params = params.copy()
        failed_params.update({"page": 1, "size": 10})
        await test_api_endpoint(session, "/business/failed-jobs", failed_params, "失败任务列表")
        
        # 2.3 测试执行时间排行
        print("\n  2.3 测试执行时间排行接口")
        duration_params = params.copy()
        duration_params["limit"] = 20
        await test_api_endpoint(session, "/business/top-duration-jobs", duration_params, "执行时间排行")
        
        # 2.4 测试统计数据
        print("\n  2.4 测试统计数据接口")
        await test_api_endpoint(session, "/business/statistics", params, "统计数据")

async def test_api_endpoint(session, endpoint, params, description):
    """测试单个API端点"""
    try:
        async with session.get(f"{BASE_URL}{endpoint}", params=params) as response:
            print(f"    请求URL: {response.url}")
            
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 0:
                    result_data = data.get('data', {})
                    
                    # 根据不同接口显示不同的信息
                    if endpoint == "/business/overview":
                        print(f"    ✅ {description}成功:")
                        print(f"       总任务: {result_data.get('total_jobs', 0)}")
                        print(f"       成功任务: {result_data.get('success_jobs', 0)}")
                        print(f"       失败任务: {result_data.get('failed_jobs', 0)}")
                        print(f"       成功率: {result_data.get('success_rate', 0)}%")
                        
                        # 检查调度器统计
                        schedulers_stats = result_data.get('schedulers_stats', {})
                        if 'azkaban' in schedulers_stats and 'dolphinscheduler' in schedulers_stats:
                            print("       ✅ 包含Azkaban和DolphinScheduler数据")
                            print(f"       Azkaban任务: {schedulers_stats['azkaban'].get('total_jobs', 0)}")
                            print(f"       DolphinScheduler任务: {schedulers_stats['dolphinscheduler'].get('total_jobs', 0)}")
                        else:
                            print("       ❌ 缺少调度器统计数据")
                    
                    elif endpoint == "/business/failed-jobs":
                        items = result_data.get('items', [])
                        total = result_data.get('total', 0)
                        print(f"    ✅ {description}成功: 共{total}个失败任务，返回{len(items)}个")
                        
                        # 检查是否包含不同调度器的任务
                        azkaban_count = sum(1 for item in items if item.get('scheduler_type') == 'Azkaban')
                        ds_count = sum(1 for item in items if item.get('scheduler_type') == 'DolphinScheduler')
                        print(f"       Azkaban失败任务: {azkaban_count}个")
                        print(f"       DolphinScheduler失败任务: {ds_count}个")
                    
                    elif endpoint == "/business/top-duration-jobs":
                        job_count = len(result_data) if isinstance(result_data, list) else 0
                        print(f"    ✅ {description}成功: 返回{job_count}个任务")
                        
                        if job_count > 0:
                            # 检查调度器分布
                            azkaban_count = sum(1 for job in result_data if job.get('scheduler_type') == 'Azkaban')
                            ds_count = sum(1 for job in result_data if job.get('scheduler_type') == 'DolphinScheduler')
                            print(f"       Azkaban任务: {azkaban_count}个")
                            print(f"       DolphinScheduler任务: {ds_count}个")
                    
                    elif endpoint == "/business/statistics":
                        daily_stats = result_data.get('daily_statistics', [])
                        scheduler_dist = result_data.get('scheduler_distribution', [])
                        project_dist = result_data.get('project_distribution', [])
                        print(f"    ✅ {description}成功:")
                        print(f"       每日统计: {len(daily_stats)}天")
                        print(f"       调度器分布: {len(scheduler_dist)}个")
                        print(f"       项目分布: {len(project_dist)}个")
                
                else:
                    print(f"    ❌ {description}业务错误: {data.get('msg', '未知错误')}")
            else:
                error_text = await response.text()
                print(f"    ❌ {description}HTTP错误: {response.status}")
                print(f"       错误信息: {error_text}")
    except Exception as e:
        print(f"    ❌ {description}异常: {e}")

async def test_database_connectivity():
    """测试数据库连接性"""
    print("\n3. 测试数据库连接")
    try:
        from app.business.services.business_service import BusinessService
        
        service = BusinessService()
        
        # 测试CDH Azkaban数据库
        print("  3.1 测试CDH Azkaban数据库连接")
        try:
            azkaban_config = service.clusters_config["cdh"]["azkaban_config"]
            connection = await service._get_azkaban_connection(azkaban_config)
            
            # 执行简单查询
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM execution_flows LIMIT 1")
                result = await cursor.fetchone()
                print(f"    ✅ Azkaban数据库连接成功，execution_flows表可访问")
            
            await connection.close()
        except Exception as e:
            print(f"    ❌ Azkaban数据库连接失败: {e}")
        
        # 测试CDH DolphinScheduler数据库
        print("  3.2 测试CDH DolphinScheduler数据库连接")
        try:
            ds_config = service.clusters_config["cdh"]["ds_config"]
            connection = await service._get_ds_connection(ds_config)
            
            # 执行简单查询
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance LIMIT 1")
                result = await cursor.fetchone()
                print(f"    ✅ CDH DolphinScheduler数据库连接成功，t_ds_process_instance表可访问")
            
            await connection.close()
        except Exception as e:
            print(f"    ❌ CDH DolphinScheduler数据库连接失败: {e}")
            
    except Exception as e:
        print(f"  ❌ 数据库连接测试异常: {e}")

async def main():
    """主函数"""
    await test_cdh_cluster_specific()
    await test_database_connectivity()
    
    print("\n" + "=" * 60)
    print("CDH集群接口测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 