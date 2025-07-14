#!/usr/bin/env python3
"""
Azkaban数据库查询测试脚本
"""
import asyncio
import aiomysql
from datetime import datetime, timedelta

async def test_azkaban_db():
    """测试Azkaban数据库查询"""
    print("Azkaban数据库查询测试")
    print("=" * 60)
    
    # 数据库配置
    db_config = {
        "host": "172.16.3.233",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "db": "azkaban",
        "charset": "utf8mb4"
    }
    
    try:
        # 连接数据库
        print("1. 连接Azkaban数据库...")
        connection = await aiomysql.connect(**db_config)
        print("   ✅ 数据库连接成功")
        
        # 设置时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        start_datetime = start_date.strftime("%Y-%m-%d 00:00:00")
        end_datetime = end_date.strftime("%Y-%m-%d 23:59:59")
        
        print(f"\n2. 查询时间范围: {start_datetime} 到 {end_datetime}")
        
        # 测试1: 查看表结构
        print(f"\n3. 查看表结构...")
        async with connection.cursor() as cursor:
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            print(f"   数据库表: {[table[0] for table in tables]}")
            
            # 查看execution_flows表结构
            await cursor.execute("DESCRIBE execution_flows")
            columns = await cursor.fetchall()
            print(f"   execution_flows表结构:")
            for col in columns:
                print(f"     {col[0]}: {col[1]}")
        
        # 测试2: 查询统计数据
        print(f"\n4. 查询统计数据...")
        stats_query = """
        SELECT 
            COUNT(*) as total_jobs,
            SUM(CASE WHEN status = 50 THEN 1 ELSE 0 END) as success_jobs,
            SUM(CASE WHEN status IN (60, 70, 80) THEN 1 ELSE 0 END) as failed_jobs
        FROM execution_flows 
        WHERE start_time >= %s AND start_time <= %s
        """
        
        async with connection.cursor() as cursor:
            await cursor.execute(stats_query, (start_datetime, end_datetime))
            result = await cursor.fetchone()
            
            total_jobs = result[0] if result[0] else 0
            success_jobs = result[1] if result[1] else 0
            failed_jobs = result[2] if result[2] else 0
            
            print(f"   总任务: {total_jobs}")
            print(f"   成功任务: {success_jobs}")
            print(f"   失败任务: {failed_jobs}")
        
        # 测试3: 查询失败任务
        print(f"\n5. 查询失败任务...")
        failed_query = """
        SELECT 
            ef.exec_id,
            ef.flow_id,
            p.name as project_name,
            ef.start_time,
            ef.end_time,
            ef.status,
            ef.submit_user
        FROM execution_flows ef
        JOIN projects p ON ef.project_id = p.id
        WHERE ef.status IN (60, 70, 80)  -- FAILED, KILLED, CANCELLED
        AND ef.start_time >= %s AND ef.start_time <= %s
        ORDER BY ef.start_time DESC
        LIMIT 5
        """
        
        async with connection.cursor() as cursor:
            await cursor.execute(failed_query, (start_datetime, end_datetime))
            results = await cursor.fetchall()
            
            print(f"   失败任务数量: {len(results)}")
            for i, result in enumerate(results):
                exec_id, flow_id, project_name, start_time, end_time, status, submit_user = result
                print(f"   失败任务{i+1}: {project_name}.{flow_id} (ID: {exec_id}, 状态: {status})")
        
        # 测试4: 查询执行时间排行
        print(f"\n6. 查询执行时间排行...")
        duration_query = """
        SELECT 
            ef.exec_id,
            ef.flow_id,
            p.name as project_name,
            ef.start_time,
            ef.end_time,
            ef.status,
            ef.submit_user
        FROM execution_flows ef
        JOIN projects p ON ef.project_id = p.id
        WHERE ef.status = 50  -- SUCCEEDED
        AND ef.start_time >= %s AND ef.start_time <= %s
        AND ef.end_time IS NOT NULL
        ORDER BY (ef.end_time - ef.start_time) DESC
        LIMIT 5
        """
        
        async with connection.cursor() as cursor:
            await cursor.execute(duration_query, (start_datetime, end_datetime))
            results = await cursor.fetchall()
            
            print(f"   长时间任务数量: {len(results)}")
            for i, result in enumerate(results):
                exec_id, flow_id, project_name, start_time, end_time, status, submit_user = result
                duration = int((end_time - start_time).total_seconds()) if end_time and start_time else 0
                print(f"   长时间任务{i+1}: {project_name}.{flow_id} (ID: {exec_id}, 执行时间: {duration}秒)")
        
        # 测试5: 查看状态码含义
        print(f"\n7. 查看状态码分布...")
        status_query = """
        SELECT status, COUNT(*) as count
        FROM execution_flows 
        WHERE start_time >= %s AND start_time <= %s
        GROUP BY status
        ORDER BY count DESC
        """
        
        async with connection.cursor() as cursor:
            await cursor.execute(status_query, (start_datetime, end_datetime))
            results = await cursor.fetchall()
            
            print(f"   状态码分布:")
            for status, count in results:
                status_map = {
                    10: "PREPARING",
                    20: "RUNNING", 
                    30: "PAUSED",
                    40: "SUCCEEDED",
                    50: "SUCCEEDED",
                    60: "FAILED",
                    70: "KILLED",
                    80: "CANCELLED"
                }
                status_name = status_map.get(status, f"UNKNOWN({status})")
                print(f"     {status}: {status_name} - {count}个")
        
        await connection.close()
        print(f"\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_azkaban_db()) 