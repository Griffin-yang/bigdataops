#!/usr/bin/env python3
"""
测试Apache集群DolphinScheduler数据库连接
"""

import asyncio
import aiomysql
from app.config import settings
from app.utils.logger import logger

async def test_apache_connection():
    """测试Apache集群DolphinScheduler数据库连接"""
    print("=" * 60)
    print("测试Apache集群DolphinScheduler数据库连接")
    print("=" * 60)
    
    # 连接参数
    config = {
        "host": settings.apache_ds_host,
        "port": settings.apache_ds_port,
        "database": settings.apache_ds_database,
        "username": settings.apache_ds_username,
        "password": settings.apache_ds_password
    }
    
    print(f"连接参数:")
    print(f"  主机: {config['host']}")
    print(f"  端口: {config['port']}")
    print(f"  数据库: {config['database']}")
    print(f"  用户名: {config['username']}")
    print(f"  密码: {'*' * len(config['password'])}")
    print()
    
    try:
        # 尝试连接
        print("正在连接数据库...")
        connection = await aiomysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["username"],
            password=config["password"],
            db=config["database"],
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 数据库连接成功!")
        
        # 测试查询
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
            key_fields = ['id', 'name', 'start_time', 'end_time', 'state']
            for col in columns:
                if col[0] in key_fields:
                    print(f"  ✅ {col[0]} - {col[1]}")
            
            # 3. 查看总记录数
            await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
            total_count = await cursor.fetchone()
            print(f"\n总记录数: {total_count[0]}")
            
            # 4. 测试业务查询
            print("\n测试业务查询...")
            
            # 统计数据查询
            query = """
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN state = 7 THEN 1 ELSE 0 END) as success_jobs,
                SUM(CASE WHEN state IN (6, 9, 10) THEN 1 ELSE 0 END) as failed_jobs
            FROM t_ds_process_instance 
            WHERE DATE(start_time) >= '2025-07-13' AND DATE(start_time) <= '2025-07-14'
            """
            
            await cursor.execute(query)
            result = await cursor.fetchone()
            print(f"统计数据查询结果: {result}")
            
            # 失败任务查询
            failed_query = """
            SELECT 
                pi.id,
                pi.name,
                pi.start_time,
                pi.end_time,
                pi.state
            FROM t_ds_process_instance pi
            WHERE pi.state IN (6, 9, 10)
            AND DATE(pi.start_time) >= '2025-07-13' AND DATE(pi.start_time) <= '2025-07-14'
            ORDER BY pi.start_time DESC
            LIMIT 5
            """
            
            await cursor.execute(failed_query)
            failed_results = await cursor.fetchall()
            print(f"失败任务查询结果: {len(failed_results)} 条记录")
            for row in failed_results:
                print(f"  ID: {row[0]}, 名称: {row[1][:30] if row[1] else 'None'}, 状态: {row[4]}")
            
            # 5. 查看最新记录
            await cursor.execute("""
                SELECT id, name, start_time, end_time, state
                FROM t_ds_process_instance 
                ORDER BY start_time DESC 
                LIMIT 3
            """)
            latest_records = await cursor.fetchall()
            print("\n最新3条记录:")
            for record in latest_records:
                print(f"  ID: {record[0]}, 名称: {record[1][:30] if record[1] else 'None'}, 时间: {record[2]}, 状态: {record[4]}")
        
        await connection.close()
        print("\n✅ 所有测试通过!")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        
        # 尝试更详细的错误信息
        if hasattr(e, 'args'):
            print(f"错误参数: {e.args}")
        
        # 检查是否是网络连接问题
        if "Connection refused" in str(e):
            print("可能的原因: 数据库服务未启动或端口不正确")
        elif "Access denied" in str(e):
            print("可能的原因: 用户名或密码错误")
        elif "Unknown database" in str(e):
            print("可能的原因: 数据库名称不存在")
        elif "timeout" in str(e).lower():
            print("可能的原因: 连接超时，网络问题或防火墙阻止")

async def test_business_service():
    """测试业务服务"""
    print("\n" + "=" * 60)
    print("测试业务服务")
    print("=" * 60)
    
    try:
        from app.business.services.business_service import BusinessService
        
        service = BusinessService()
        
        # 测试获取集群列表
        clusters = await service.get_available_clusters()
        print(f"可用集群: {clusters}")
        
        # 测试Apache集群概览
        if any(cluster['id'] == 'apache' for cluster in clusters):
            print("\n测试Apache集群概览...")
            overview = await service.get_business_overview('apache', '2025-07-13', '2025-07-14')
            print(f"概览结果: {overview}")
        else:
            print("❌ 未找到Apache集群配置")
            
    except Exception as e:
        print(f"❌ 业务服务测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_apache_connection())
    print("\n" + "=" * 60)
    print("开始测试业务服务...")
    print("=" * 60)
    asyncio.run(test_business_service()) 