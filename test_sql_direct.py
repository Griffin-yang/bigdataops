#!/usr/bin/env python3
"""
直接SQL查询测试脚本
验证各个数据库中是否有数据，字段是否正确
"""

import asyncio
import aiomysql
from datetime import datetime, timedelta
from app.config import settings

async def test_azkaban_database():
    """测试Azkaban数据库"""
    print("=" * 60)
    print("测试Azkaban数据库")
    print("=" * 60)
    
    try:
        print(f"连接参数: {settings.azkaban_db_host}:{settings.azkaban_db_port}/{settings.azkaban_db_database}")
        print(f"用户: {settings.azkaban_db_username}")
        
        connection = await aiomysql.connect(
            host=settings.azkaban_db_host,
            port=settings.azkaban_db_port,
            user=settings.azkaban_db_username,
            password=settings.azkaban_db_password,
            db=settings.azkaban_db_database,
            charset='utf8mb4'
        )
        
        print("✅ Azkaban数据库连接成功")
        
        async with connection.cursor() as cursor:
            # 1. 检查表是否存在
            await cursor.execute("SHOW TABLES LIKE 'execution_flows'")
            table_exists = await cursor.fetchone()
            if table_exists:
                print("✅ execution_flows 表存在")
            else:
                print("❌ execution_flows 表不存在")
                await connection.close()
                return
            
            # 2. 检查表结构
            await cursor.execute("DESCRIBE execution_flows")
            columns = await cursor.fetchall()
            print("\n表结构:")
            for col in columns:
                print(f"  {col[0]} - {col[1]}")
            
            # 3. 查看总记录数
            await cursor.execute("SELECT COUNT(*) FROM execution_flows")
            total_count = await cursor.fetchone()
            print(f"\n总记录数: {total_count[0]}")
            
            # 4. 查看最新记录
            await cursor.execute("""
                SELECT exec_id, flow_id, start_time, end_time, status, submit_user
                FROM execution_flows 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print("\n最新5条记录:")
            for record in latest_records:
                start_time = datetime.fromtimestamp(record[2] / 1000).strftime("%Y-%m-%d %H:%M:%S") if record[2] else "None"
                print(f"  ID: {record[0]}, Flow: {record[1]}, 时间: {start_time}, 状态: {record[4]}")
            
            # 5. 测试时间范围查询
            yesterday = datetime.now() - timedelta(days=1)
            start_timestamp = int(yesterday.replace(hour=0, minute=0, second=0).timestamp() * 1000)
            end_timestamp = int(datetime.now().timestamp() * 1000)
            
            await cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 50 THEN 1 ELSE 0 END) as success,
                       SUM(CASE WHEN status IN (60, 70, 80) THEN 1 ELSE 0 END) as failed
                FROM execution_flows 
                WHERE start_time >= %s AND start_time <= %s
            """, (start_timestamp, end_timestamp))
            
            stats = await cursor.fetchone()
            print(f"\n昨天到今天的统计:")
            print(f"  总任务: {stats[0]}")
            print(f"  成功: {stats[1]}")
            print(f"  失败: {stats[2]}")
            
        await connection.close()
        
    except Exception as e:
        print(f"❌ Azkaban数据库测试失败: {e}")

async def test_cdh_dolphinscheduler_database():
    """测试CDH DolphinScheduler数据库"""
    print("\n" + "=" * 60)
    print("测试CDH DolphinScheduler数据库")
    print("=" * 60)
    
    try:
        print(f"连接参数: {settings.cdh_ds_host}:{settings.cdh_ds_port}/{settings.cdh_ds_database}")
        print(f"用户: {settings.cdh_ds_username}")
        
        connection = await aiomysql.connect(
            host=settings.cdh_ds_host,
            port=settings.cdh_ds_port,
            user=settings.cdh_ds_username,
            password=settings.cdh_ds_password,
            db=settings.cdh_ds_database,
            charset='utf8mb4'
        )
        
        print("✅ CDH DolphinScheduler数据库连接成功")
        
        async with connection.cursor() as cursor:
            # 1. 检查表是否存在
            await cursor.execute("SHOW TABLES LIKE 't_ds_process_instance'")
            table_exists = await cursor.fetchone()
            if table_exists:
                print("✅ t_ds_process_instance 表存在")
            else:
                print("❌ t_ds_process_instance 表不存在")
                await connection.close()
                return
            
            # 2. 检查表结构
            await cursor.execute("DESCRIBE t_ds_process_instance")
            columns = await cursor.fetchall()
            print("\n表结构 (关键字段):")
            key_fields = ['id', 'name', 'start_time', 'end_time', 'state', 'process_definition_id']
            for col in columns:
                if col[0] in key_fields:
                    print(f"  ✅ {col[0]} - {col[1]}")
            
            # 3. 查看总记录数
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            total_count = await cursor.fetchone()
            print(f"\n总记录数: {total_count[0]}")
            
            # 4. 查看最新记录
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state
                FROM t_ds_process_instance 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print("\n最新5条记录:")
            for record in latest_records:
                print(f"  ID: {record[0]}, 名称: {record[1][:30]}, 时间: {record[2]}, 状态: {record[4]}")
            
            # 5. 检查关联表
            await cursor.execute("SHOW TABLES LIKE 't_ds_process_definition'")
            pd_exists = await cursor.fetchone()
            
            await cursor.execute("SHOW TABLES LIKE 't_ds_project'")
            proj_exists = await cursor.fetchone()
            
            print(f"\n关联表检查:")
            print(f"  t_ds_process_definition: {'✅ 存在' if pd_exists else '❌ 不存在'}")
            print(f"  t_ds_project: {'✅ 存在' if proj_exists else '❌ 不存在'}")
            
            # 6. 测试JOIN查询
            if pd_exists and proj_exists:
                try:
                    await cursor.execute("""
                        SELECT COUNT(*) 
                        FROM t_ds_process_instance pi
                        JOIN t_ds_process_definition pd ON pi.process_definition_id = pd.id
                        JOIN t_ds_project p ON pd.project_id = p.id
                        LIMIT 1
                    """)
                    join_result = await cursor.fetchone()
                    print("  ✅ JOIN查询成功")
                except Exception as join_error:
                    print(f"  ❌ JOIN查询失败: {join_error}")
            
            # 7. 测试时间范围查询
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            await cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success,
                       SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed
                FROM t_ds_process_instance 
                WHERE DATE(start_time) >= %s AND DATE(start_time) <= %s
            """, (start_date, end_date))
            
            stats = await cursor.fetchone()
            print(f"\n昨天到今天的统计:")
            print(f"  总任务: {stats[0]}")
            print(f"  成功: {stats[1]}")
            print(f"  失败: {stats[2]}")
            
        await connection.close()
        
    except Exception as e:
        print(f"❌ CDH DolphinScheduler数据库测试失败: {e}")

async def test_apache_dolphinscheduler_database():
    """测试Apache DolphinScheduler数据库"""
    print("\n" + "=" * 60)
    print("测试Apache DolphinScheduler数据库")
    print("=" * 60)
    
    try:
        print(f"连接参数: {settings.apache_ds_host}:{settings.apache_ds_port}/{settings.apache_ds_database}")
        print(f"用户: {settings.apache_ds_username}")
        
        connection = await aiomysql.connect(
            host=settings.apache_ds_host,
            port=settings.apache_ds_port,
            user=settings.apache_ds_username,
            password=settings.apache_ds_password,
            db=settings.apache_ds_database,
            charset='utf8mb4'
        )
        
        print("✅ Apache DolphinScheduler数据库连接成功")
        
        async with connection.cursor() as cursor:
            # 1. 检查表是否存在
            await cursor.execute("SHOW TABLES LIKE 't_ds_process_instance'")
            table_exists = await cursor.fetchone()
            if table_exists:
                print("✅ t_ds_process_instance 表存在")
            else:
                print("❌ t_ds_process_instance 表不存在")
                await connection.close()
                return
            
            # 2. 检查表结构
            await cursor.execute("DESCRIBE t_ds_process_instance")
            columns = await cursor.fetchall()
            print("\n表结构 (关键字段):")
            key_fields = ['id', 'name', 'start_time', 'end_time', 'state', 'process_definition_id']
            for col in columns:
                if col[0] in key_fields:
                    print(f"  ✅ {col[0]} - {col[1]}")
            
            # 3. 查看总记录数
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            total_count = await cursor.fetchone()
            print(f"\n总记录数: {total_count[0]}")
            
            # 4. 查看最新记录
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state
                FROM t_ds_process_instance 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print("\n最新5条记录:")
            for record in latest_records:
                print(f"  ID: {record[0]}, 名称: {record[1][:30] if record[1] else 'None'}, 时间: {record[2]}, 状态: {record[4]}")
            
            # 5. 检查关联表
            await cursor.execute("SHOW TABLES LIKE 't_ds_process_definition'")
            pd_exists = await cursor.fetchone()
            
            await cursor.execute("SHOW TABLES LIKE 't_ds_project'")
            proj_exists = await cursor.fetchone()
            
            print(f"\n关联表检查:")
            print(f"  t_ds_process_definition: {'✅ 存在' if pd_exists else '❌ 不存在'}")
            print(f"  t_ds_project: {'✅ 存在' if proj_exists else '❌ 不存在'}")
            
            # 6. 测试JOIN查询
            if pd_exists and proj_exists:
                try:
                    await cursor.execute("""
                        SELECT COUNT(*) 
                        FROM t_ds_process_instance pi
                        JOIN t_ds_process_definition pd ON pi.process_definition_id = pd.id
                        JOIN t_ds_project p ON pd.project_id = p.id
                        LIMIT 1
                    """)
                    join_result = await cursor.fetchone()
                    print("  ✅ JOIN查询成功")
                except Exception as join_error:
                    print(f"  ❌ JOIN查询失败: {join_error}")
                    print("  将使用简化查询模式")
            
            # 7. 测试时间范围查询
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            await cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success,
                       SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed
                FROM t_ds_process_instance 
                WHERE DATE(start_time) >= %s AND DATE(start_time) <= %s
            """, (start_date, end_date))
            
            stats = await cursor.fetchone()
            print(f"\n昨天到今天的统计:")
            print(f"  总任务: {stats[0]}")
            print(f"  成功: {stats[1]}")
            print(f"  失败: {stats[2]}")
            
            # 8. 测试具体日期查询
            test_date = "2025-06-06"
            await cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success,
                       SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed
                FROM t_ds_process_instance 
                WHERE DATE(start_time) = %s
            """, (test_date,))
            
            test_stats = await cursor.fetchone()
            print(f"\n{test_date}的统计:")
            print(f"  总任务: {test_stats[0]}")
            print(f"  成功: {test_stats[1]}")
            print(f"  失败: {test_stats[2]}")
            
        await connection.close()
        
    except Exception as e:
        print(f"❌ Apache DolphinScheduler数据库测试失败: {e}")

async def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("测试API端点连通性")
    print("=" * 60)
    
    import aiohttp
    
    base_url = "http://localhost:8000/api"
    
    async with aiohttp.ClientSession() as session:
        # 测试集群列表
        try:
            async with session.get(f"{base_url}/business/clusters") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 集群列表API正常")
                    print(f"   集群数量: {len(data.get('data', []))}")
                else:
                    print(f"❌ 集群列表API失败: HTTP {response.status}")
        except Exception as e:
            print(f"❌ 集群列表API异常: {e}")
        
        # 测试CDH概览
        params = {
            "cluster_name": "cdh",
            "start_date": "2025-06-06",
            "end_date": "2025-06-06"
        }
        
        try:
            async with session.get(f"{base_url}/business/overview", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('data', {})
                    print(f"✅ CDH概览API正常: 总任务{overview.get('total_jobs', 0)}")
                else:
                    text = await response.text()
                    print(f"❌ CDH概览API失败: HTTP {response.status}")
                    print(f"   错误: {text[:200]}")
        except Exception as e:
            print(f"❌ CDH概览API异常: {e}")
        
        # 测试Apache概览
        params["cluster_name"] = "apache"
        
        try:
            async with session.get(f"{base_url}/business/overview", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('data', {})
                    print(f"✅ Apache概览API正常: 总任务{overview.get('total_jobs', 0)}")
                else:
                    text = await response.text()
                    print(f"❌ Apache概览API失败: HTTP {response.status}")
                    print(f"   错误: {text[:200]}")
        except Exception as e:
            print(f"❌ Apache概览API异常: {e}")

async def main():
    """主函数"""
    print("BigDataOps 业务监控 - 数据库和API完整测试")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 测试所有数据库
    await test_azkaban_database()
    await test_cdh_dolphinscheduler_database() 
    await test_apache_dolphinscheduler_database()
    
    # 测试API端点
    await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 