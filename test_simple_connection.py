#!/usr/bin/env python3
"""
简单的Apache集群DolphinScheduler数据库连接测试
"""

import asyncio
import aiomysql
from app.config import settings

async def test_simple_connection():
    """简单的数据库连接测试"""
    print("=" * 60)
    print("简单数据库连接测试")
    print("=" * 60)
    
    try:
        print("正在连接数据库...")
        connection = await aiomysql.connect(
            host=settings.apache_ds_host,
            port=settings.apache_ds_port,
            user=settings.apache_ds_username,
            password=settings.apache_ds_password,
            db=settings.apache_ds_database,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 数据库连接成功!")
        
        # 简单查询
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            result = await cursor.fetchone()
            print(f"总记录数: {result[0]}")
        
        # 关闭连接
        connection.close()
        print("✅ 连接已关闭")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_simple_connection()) 