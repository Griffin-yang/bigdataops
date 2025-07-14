#!/usr/bin/env python3
"""
测试优化后的业务监控接口
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# 后端服务地址
BASE_URL = "http://localhost:8000"

async def test_business_apis():
    """测试业务监控相关接口"""
    
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("测试优化后的业务监控接口")
        print("=" * 60)
        
        # 1. 测试获取集群列表
        print("\n1. 测试获取集群列表")
        try:
            async with session.get(f"{BASE_URL}/business/clusters") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 成功获取集群列表: {len(data.get('data', []))} 个集群")
                    for cluster in data.get('data', []):
                        print(f"   - {cluster['name']} ({cluster['type']})")
                else:
                    print(f"❌ 获取集群列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 获取集群列表异常: {e}")
        
        # 2. 测试业务概览
        print("\n2. 测试业务概览")
        try:
            params = {
                "cluster_name": "cdh",
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }
            async with session.get(f"{BASE_URL}/business/overview", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('data', {})
                    print(f"✅ 成功获取业务概览:")
                    print(f"   - 集群: {overview.get('cluster_name')}")
                    print(f"   - 总任务数: {overview.get('total_jobs')}")
                    print(f"   - 成功任务: {overview.get('success_jobs')}")
                    print(f"   - 失败任务: {overview.get('failed_jobs')}")
                    print(f"   - 成功率: {overview.get('success_rate')}%")
                else:
                    print(f"❌ 获取业务概览失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
        except Exception as e:
            print(f"❌ 获取业务概览异常: {e}")
        
        # 3. 测试失败任务列表
        print("\n3. 测试失败任务列表")
        try:
            params = {
                "cluster_name": "cdh",
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "page": 1,
                "size": 10
            }
            async with session.get(f"{BASE_URL}/business/failed-jobs", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    failed_jobs = data.get('data', {})
                    print(f"✅ 成功获取失败任务列表:")
                    print(f"   - 总数: {failed_jobs.get('total')}")
                    print(f"   - 当前页: {failed_jobs.get('page')}")
                    print(f"   - 每页数量: {failed_jobs.get('size')}")
                    print(f"   - 总页数: {failed_jobs.get('pages')}")
                    
                    # 显示前3个失败任务
                    items = failed_jobs.get('items', [])
                    for i, job in enumerate(items[:3]):
                        print(f"   - 任务{i+1}: {job.get('job_name')} ({job.get('scheduler_type')})")
                else:
                    print(f"❌ 获取失败任务列表失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
        except Exception as e:
            print(f"❌ 获取失败任务列表异常: {e}")
        
        # 4. 测试执行时间排行榜
        print("\n4. 测试执行时间排行榜")
        try:
            params = {
                "cluster_name": "cdh",
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "limit": 10
            }
            async with session.get(f"{BASE_URL}/business/top-duration-jobs", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    top_jobs = data.get('data', [])
                    print(f"✅ 成功获取执行时间排行榜: {len(top_jobs)} 个任务")
                    
                    # 显示前3个最耗时任务
                    for i, job in enumerate(top_jobs[:3]):
                        print(f"   - 第{i+1}名: {job.get('job_name')} ({job.get('duration')}秒)")
                else:
                    print(f"❌ 获取执行时间排行榜失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
        except Exception as e:
            print(f"❌ 获取执行时间排行榜异常: {e}")
        
        # 5. 测试统计数据
        print("\n5. 测试统计数据")
        try:
            params = {
                "cluster_name": "cdh",
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }
            async with session.get(f"{BASE_URL}/business/statistics", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('data', {})
                    print(f"✅ 成功获取统计数据:")
                    
                    daily_stats = stats.get('daily_statistics', [])
                    print(f"   - 每日统计: {len(daily_stats)} 天")
                    
                    scheduler_dist = stats.get('scheduler_distribution', [])
                    print(f"   - 调度器分布: {len(scheduler_dist)} 个调度器")
                    for dist in scheduler_dist:
                        print(f"     * {dist.get('scheduler_name')}: {dist.get('job_count')} 任务")
                    
                    project_dist = stats.get('project_distribution', [])
                    print(f"   - 项目分布: {len(project_dist)} 个项目")
                    for dist in project_dist[:3]:  # 只显示前3个
                        print(f"     * {dist.get('name')}: {dist.get('value')} 任务")
                else:
                    print(f"❌ 获取统计数据失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
        except Exception as e:
            print(f"❌ 获取统计数据异常: {e}")
        
        # 6. 测试项目分布
        print("\n6. 测试项目分布")
        try:
            params = {
                "cluster_name": "cdh",
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }
            async with session.get(f"{BASE_URL}/business/project-distribution", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    project_dist = data.get('data', [])
                    print(f"✅ 成功获取项目分布: {len(project_dist)} 个项目")
                    
                    # 显示前5个项目
                    for i, project in enumerate(project_dist[:5]):
                        print(f"   - {project.get('name')}: {project.get('value')} 任务 (成功: {project.get('success')}, 失败: {project.get('failed')})")
                else:
                    print(f"❌ 获取项目分布失败: {response.status}")
                    error_text = await response.text()
                    print(f"   错误信息: {error_text}")
        except Exception as e:
            print(f"❌ 获取项目分布异常: {e}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_business_apis()) 