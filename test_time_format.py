#!/usr/bin/env python3
"""
测试时间格式和数据库查询
"""

import asyncio
import aiomysql
from datetime import datetime
from app.config import settings

async def test_ds_time_format():
    """测试DolphinScheduler时间格式和查询"""
    
    print("=" * 60)
    print("测试DolphinScheduler时间格式和查询")
    print("=" * 60)
    
    # 测试CDH集群的DolphinScheduler
    print("\n1. 测试CDH集群DolphinScheduler数据库连接和时间查询")
    try:
        # CDH DS连接
        cdh_connection = await aiomysql.connect(
            host=settings.cdh_ds_host,
            port=settings.cdh_ds_port,
            user=settings.cdh_ds_username,
            password=settings.cdh_ds_password,
            db=settings.cdh_ds_database,
            charset='utf8mb4'
        )
        
        print(f"✅ CDH DolphinScheduler数据库连接成功")
        print(f"   数据库: {settings.cdh_ds_host}:{settings.cdh_ds_port}/{settings.cdh_ds_database}")
        
        # 测试数据存在性
        async with cdh_connection.cursor() as cursor:
            # 1. 查看表中有多少数据
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            total_count = await cursor.fetchone()
            print(f"   表中总记录数: {total_count[0]}")
            
            # 2. 查看最新的几条记录及其时间
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state 
                FROM t_ds_process_instance 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print(f"   最新5条记录:")
            for record in latest_records:
                print(f"     ID: {record[0]}, 名称: {record[1]}, 开始时间: {record[2]}, 状态: {record[4]}")
            
            # 3. 查看时间范围
            await cursor.execute("""
                SELECT 
                    MIN(start_time) as earliest_time,
                    MAX(start_time) as latest_time
                FROM t_ds_process_instance
            """)
            time_range = await cursor.fetchone()
            print(f"   数据时间范围: {time_range[0]} 到 {time_range[1]}")
            
            # 4. 按日期统计数据量
            await cursor.execute("""
                SELECT 
                    DATE(start_time) as date,
                    COUNT(*) as count,
                    SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_count
                FROM t_ds_process_instance 
                GROUP BY DATE(start_time)
                ORDER BY date DESC
                LIMIT 10
            """)
            daily_stats = await cursor.fetchall()
            print(f"   按日期统计:")
            for stat in daily_stats:
                print(f"     {stat[0]}: 总数{stat[1]}, 成功{stat[2]}, 失败{stat[3]}")
        
        await cdh_connection.close()
        
    except Exception as e:
        print(f"❌ CDH DolphinScheduler测试失败: {e}")
    
    # 测试Apache集群的DolphinScheduler
    print("\n2. 测试Apache集群DolphinScheduler数据库连接和时间查询")
    try:
        # Apache DS连接
        apache_connection = await aiomysql.connect(
            host=settings.apache_ds_host,
            port=settings.apache_ds_port,
            user=settings.apache_ds_username,
            password=settings.apache_ds_password,
            db=settings.apache_ds_database,
            charset='utf8mb4'
        )
        
        print(f"✅ Apache DolphinScheduler数据库连接成功")
        print(f"   数据库: {settings.apache_ds_host}:{settings.apache_ds_port}/{settings.apache_ds_database}")
        
        # 测试数据存在性
        async with apache_connection.cursor() as cursor:
            # 1. 查看表中有多少数据
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            total_count = await cursor.fetchone()
            print(f"   表中总记录数: {total_count[0]}")
            
            # 2. 查看最新的几条记录及其时间
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state 
                FROM t_ds_process_instance 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print(f"   最新5条记录:")
            for record in latest_records:
                print(f"     ID: {record[0]}, 名称: {record[1]}, 开始时间: {record[2]}, 状态: {record[4]}")
            
            # 3. 查看时间范围
            await cursor.execute("""
                SELECT 
                    MIN(start_time) as earliest_time,
                    MAX(start_time) as latest_time
                FROM t_ds_process_instance
            """)
            time_range = await cursor.fetchone()
            print(f"   数据时间范围: {time_range[0]} 到 {time_range[1]}")
            
            # 4. 按日期统计数据量
            await cursor.execute("""
                SELECT 
                    DATE(start_time) as date,
                    COUNT(*) as count,
                    SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_count
                FROM t_ds_process_instance 
                GROUP BY DATE(start_time)
                ORDER BY date DESC
                LIMIT 10
            """)
            daily_stats = await cursor.fetchall()
            print(f"   按日期统计:")
            for stat in daily_stats:
                print(f"     {stat[0]}: 总数{stat[1]}, 成功{stat[2]}, 失败{stat[3]}")
        
        await apache_connection.close()
        
    except Exception as e:
        print(f"❌ Apache DolphinScheduler测试失败: {e}")

async def test_azkaban_time_format():
    """测试Azkaban时间格式和查询"""
    
    print("\n3. 测试Azkaban时间格式和查询")
    try:
        # Azkaban连接
        azkaban_connection = await aiomysql.connect(
            host=settings.azkaban_db_host,
            port=settings.azkaban_db_port,
            user=settings.azkaban_db_username,
            password=settings.azkaban_db_password,
            db=settings.azkaban_db_database,
            charset='utf8mb4'
        )
        
        print(f"✅ Azkaban数据库连接成功")
        print(f"   数据库: {settings.azkaban_db_host}:{settings.azkaban_db_port}/{settings.azkaban_db_database}")
        
        # 测试数据存在性
        async with azkaban_connection.cursor() as cursor:
            # 1. 查看表中有多少数据
            await cursor.execute("SELECT COUNT(*) FROM execution_flows")
            total_count = await cursor.fetchone()
            print(f"   execution_flows表中总记录数: {total_count[0]}")
            
            # 2. 查看最新的几条记录及其时间（时间戳格式）
            await cursor.execute("""
                SELECT exec_id, flow_id, start_time, end_time, status
                FROM execution_flows 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            latest_records = await cursor.fetchall()
            print(f"   最新5条记录:")
            for record in latest_records:
                start_time_readable = datetime.fromtimestamp(record[2] / 1000).strftime("%Y-%m-%d %H:%M:%S") if record[2] else "None"
                print(f"     ID: {record[0]}, Flow: {record[1]}, 开始时间: {start_time_readable} (时间戳: {record[2]}), 状态: {record[4]}")
            
            # 3. 查看时间范围
            await cursor.execute("""
                SELECT 
                    MIN(start_time) as earliest_time,
                    MAX(start_time) as latest_time
                FROM execution_flows
                WHERE start_time IS NOT NULL
            """)
            time_range = await cursor.fetchone()
            if time_range[0] and time_range[1]:
                earliest_readable = datetime.fromtimestamp(time_range[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                latest_readable = datetime.fromtimestamp(time_range[1] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                print(f"   数据时间范围: {earliest_readable} 到 {latest_readable}")
            
            # 4. 按日期统计数据量（需要转换时间戳）
            await cursor.execute("""
                SELECT 
                    DATE(FROM_UNIXTIME(start_time/1000)) as date,
                    COUNT(*) as count,
                    SUM(CASE WHEN status = 50 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status IN (60, 70, 80) THEN 1 ELSE 0 END) as failed_count
                FROM execution_flows 
                WHERE start_time IS NOT NULL
                GROUP BY DATE(FROM_UNIXTIME(start_time/1000))
                ORDER BY date DESC
                LIMIT 10
            """)
            daily_stats = await cursor.fetchall()
            print(f"   按日期统计:")
            for stat in daily_stats:
                print(f"     {stat[0]}: 总数{stat[1]}, 成功{stat[2]}, 失败{stat[3]}")
        
        await azkaban_connection.close()
        
    except Exception as e:
        print(f"❌ Azkaban测试失败: {e}")

async def test_time_query_logic():
    """测试具体的时间查询逻辑"""
    
    print("\n4. 测试时间查询逻辑")
    
    # 根据用户提供的数据，测试2025-06-06的查询
    test_date = "2025-06-06"
    
    print(f"测试查询日期: {test_date}")
    
    # 测试DolphinScheduler查询
    try:
        connection = await aiomysql.connect(
            host=settings.cdh_ds_host,
            port=settings.cdh_ds_port,
            user=settings.cdh_ds_username,
            password=settings.cdh_ds_password,
            db=settings.cdh_ds_database,
            charset='utf8mb4'
        )
        
        # 模拟我们的查询逻辑
        start_datetime = f"{test_date} 00:00:00"
        end_datetime = f"{test_date} 23:59:59"
        
        print(f"查询时间范围: {start_datetime} 到 {end_datetime}")
        
        async with connection.cursor() as cursor:
            # 统计查询
            query = """
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_jobs
            FROM t_ds_process_instance 
            WHERE start_time >= %s AND start_time <= %s
            """
            
            await cursor.execute(query, (start_datetime, end_datetime))
            result = await cursor.fetchone()
            
            print(f"DolphinScheduler {test_date} 统计结果:")
            print(f"  总任务: {result[0]}")
            print(f"  成功任务: {result[1]}")
            print(f"  失败任务: {result[2]}")
            
            # 详细记录查询
            detail_query = """
            SELECT id, name, start_time, end_time, state
            FROM t_ds_process_instance 
            WHERE start_time >= %s AND start_time <= %s
            ORDER BY start_time DESC
            LIMIT 10
            """
            
            await cursor.execute(detail_query, (start_datetime, end_datetime))
            details = await cursor.fetchall()
            
            print(f"  详细记录({len(details)}条):")
            for detail in details:
                print(f"    ID: {detail[0]}, 名称: {detail[1]}, 开始: {detail[2]}, 状态: {detail[4]}")
        
        await connection.close()
        
    except Exception as e:
        print(f"❌ DolphinScheduler查询测试失败: {e}")

async def main():
    """主函数"""
    await test_ds_time_format()
    await test_azkaban_time_format()
    await test_time_query_logic()
    
    print("\n" + "=" * 60)
    print("时间格式测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 