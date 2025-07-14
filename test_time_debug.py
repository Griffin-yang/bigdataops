#!/usr/bin/env python3
import asyncio
import aiomysql
from datetime import datetime
from app.config import settings

async def test_specific_date():
    """测试特定日期的数据查询"""
    
    print("测试2025-06-06的数据查询...")
    
    try:
        # 连接CDH DolphinScheduler
        connection = await aiomysql.connect(
            host=settings.cdh_ds_host,
            port=settings.cdh_ds_port,
            user=settings.cdh_ds_username,
            password=settings.cdh_ds_password,
            db=settings.cdh_ds_database,
            charset='utf8mb4'
        )
        
        print(f"✅ 连接成功: {settings.cdh_ds_host}:{settings.cdh_ds_port}")
        
        async with connection.cursor() as cursor:
            # 1. 查看表结构
            await cursor.execute("DESCRIBE t_ds_process_instance")
            columns = await cursor.fetchall()
            print("表结构:")
            for col in columns:
                if 'time' in col[0].lower():
                    print(f"  时间字段: {col[0]} - {col[1]}")
            
            # 2. 查看2025-06-06的数据
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state 
                FROM t_ds_process_instance 
                WHERE DATE(start_time) = '2025-06-06'
                LIMIT 5
            """)
            records = await cursor.fetchall()
            print(f"\n2025-06-06的数据({len(records)}条):")
            for record in records:
                print(f"  ID:{record[0]}, 名称:{record[1][:20]}, 开始:{record[2]}, 状态:{record[4]}")
            
            # 3. 测试我们的查询逻辑
            start_datetime = "2025-06-06 00:00:00"
            end_datetime = "2025-06-06 23:59:59"
            
            await cursor.execute("""
                SELECT COUNT(*) FROM t_ds_process_instance 
                WHERE start_time >= %s AND start_time <= %s
            """, (start_datetime, end_datetime))
            count = await cursor.fetchone()
            print(f"\n使用我们的查询逻辑: 找到 {count[0]} 条记录")
        
        await connection.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_date()) 