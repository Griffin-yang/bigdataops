#!/usr/bin/env python3
"""
测试修复后的业务监控API
"""

import asyncio
import aiohttp
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

async def test_fixed_business_apis():
    """测试修复后的业务监控API"""
    
    print("=" * 60)
    print("测试修复后的业务监控API")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 测试集群列表
        print("\n1. 测试集群列表")
        try:
            async with session.get(f"{BASE_URL}/business/clusters") as response:
                if response.status == 200:
                    data = await response.json()
                    clusters = data.get('data', [])
                    print(f"✅ 获取到 {len(clusters)} 个集群")
                    for cluster in clusters:
                        print(f"   - {cluster['name']} ({cluster['id']}): {', '.join(cluster['schedulers'])}")
                else:
                    print(f"❌ 获取集群列表失败: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"❌ 集群列表异常: {e}")
            return
        
        # 2. 测试CDH集群（使用实际有数据的日期）
        test_date = "2025-06-06"  # 基于用户提供的数据
        print(f"\n2. 测试CDH集群 (日期: {test_date})")
        
        params = {
            "cluster_name": "cdh",
            "start_date": test_date,
            "end_date": test_date
        }
        
        # 2.1 业务概览
        try:
            async with session.get(f"{BASE_URL}/business/overview", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('data', {})
                    print(f"   业务概览: 总任务{overview.get('total_jobs', 0)}")
                    
                    # 检查调度器统计
                    schedulers_stats = overview.get('schedulers_stats', {})
                    if 'azkaban' in schedulers_stats:
                        print(f"   Azkaban: {schedulers_stats['azkaban'].get('total_jobs', 0)}个任务")
                    if 'dolphinscheduler' in schedulers_stats:
                        print(f"   DolphinScheduler: {schedulers_stats['dolphinscheduler'].get('total_jobs', 0)}个任务")
                else:
                    print(f"   ❌ 业务概览失败: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ 业务概览异常: {e}")
        
        # 2.2 失败任务
        try:
            async with session.get(f"{BASE_URL}/business/failed-jobs", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    failed_jobs = data.get('data', {})
                    print(f"   失败任务: {failed_jobs.get('total', 0)}个")
                else:
                    print(f"   ❌ 失败任务失败: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ 失败任务异常: {e}")
        
        # 3. 测试Apache集群
        print(f"\n3. 测试Apache集群 (日期: {test_date})")
        
        apache_params = {
            "cluster_name": "apache",
            "start_date": test_date,
            "end_date": test_date
        }
        
        try:
            async with session.get(f"{BASE_URL}/business/overview", params=apache_params) as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('data', {})
                    print(f"   业务概览: 总任务{overview.get('total_jobs', 0)}")
                else:
                    print(f"   ❌ Apache集群失败: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Apache集群异常: {e}")

async def main():
    """主函数"""
    await test_fixed_business_apis()
    
    print("\n" + "=" * 60)
    print("API测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 