#!/usr/bin/env python3
"""
测试业务服务的数据库连接方法
"""

import asyncio
from app.business.services.business_service import BusinessService

async def test_business_connection():
    """测试业务服务的数据库连接"""
    print("=" * 60)
    print("测试业务服务数据库连接")
    print("=" * 60)
    
    try:
        service = BusinessService()
        
        # 获取Apache集群配置
        apache_config = service.clusters_config.get("apache")
        if not apache_config:
            print("❌ 未找到Apache集群配置")
            return
        
        ds_config = apache_config["ds_config"]
        print(f"Apache集群DS配置: {ds_config}")
        
        # 测试连接方法
        print("\n测试_get_ds_connection方法...")
        connection = await service._get_ds_connection(ds_config)
        
        if connection:
            print("✅ _get_ds_connection方法返回了连接对象")
            
            # 测试查询
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM t_ds_process_instance")
                result = await cursor.fetchone()
                print(f"查询结果: {result[0]}")
            
            await connection.close()
            print("✅ 连接已关闭")
        else:
            print("❌ _get_ds_connection方法返回了None")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_business_connection()) 