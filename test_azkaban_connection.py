#!/usr/bin/env python3
"""
Azkaban连接测试脚本
用于诊断和调试Azkaban API连接问题
"""
import asyncio
import aiohttp
import ssl
import json
from urllib.parse import urljoin

class AzkabanTester:
    def __init__(self):
        self.base_url = "https://172.16.3.233:34006"
        self.username = "zhengan"
        self.password = "za123"
        
        # 创建SSL上下文以处理自签名证书
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def test_connection(self):
        """测试基本连接"""
        print("=" * 60)
        print("1. 测试基本连接...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, ssl=self.ssl_context) as response:
                    print(f"   状态码: {response.status}")
                    print(f"   响应头: {dict(response.headers)}")
                    if response.status == 200:
                        content = await response.text()
                        print(f"   响应长度: {len(content)} 字符")
                        print("   ✅ 基本连接成功")
                    else:
                        print("   ❌ 基本连接失败")
            except Exception as e:
                print(f"   ❌ 连接错误: {e}")
    
    async def test_login_methods(self):
        """测试多种登录方法"""
        print("\n" + "=" * 60)
        print("2. 测试不同的登录方法...")
        
        # 方法1: POST表单数据
        await self._test_login_form_data()
        
        # 方法2: POST JSON数据
        await self._test_login_json()
        
        # 方法3: GET请求（某些Azkaban版本支持）
        await self._test_login_get()
    
    async def _test_login_form_data(self):
        """方法1: POST表单数据"""
        print("\n   方法1: POST表单数据")
        
        url = urljoin(self.base_url, "/")
        data = {
            'action': 'login',
            'username': self.username,
            'password': self.password
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, ssl=self.ssl_context) as response:
                    print(f"   状态码: {response.status}")
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    
                    content = await response.text()
                    print(f"   响应长度: {len(content)} 字符")
                    
                    # 尝试解析JSON
                    try:
                        json_data = json.loads(content)
                        print(f"   JSON响应: {json_data}")
                        if 'session.id' in json_data:
                            print("   ✅ 登录成功 - 获得session.id")
                        elif 'error' in json_data:
                            print(f"   ❌ 登录失败 - 错误: {json_data['error']}")
                    except json.JSONDecodeError:
                        print("   响应不是JSON格式")
                        if "login" in content.lower() and "password" in content.lower():
                            print("   可能返回了登录页面HTML")
                        
            except Exception as e:
                print(f"   ❌ 请求错误: {e}")
    
    async def _test_login_json(self):
        """方法2: POST JSON数据"""
        print("\n   方法2: POST JSON数据")
        
        url = urljoin(self.base_url, "/")
        data = {
            'action': 'login',
            'username': self.username,
            'password': self.password
        }
        headers = {'Content-Type': 'application/json'}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, headers=headers, ssl=self.ssl_context) as response:
                    print(f"   状态码: {response.status}")
                    content = await response.text()
                    print(f"   响应长度: {len(content)} 字符")
                    
                    try:
                        json_data = json.loads(content)
                        print(f"   JSON响应: {json_data}")
                    except json.JSONDecodeError:
                        print("   响应不是JSON格式")
                        
            except Exception as e:
                print(f"   ❌ 请求错误: {e}")
    
    async def _test_login_get(self):
        """方法3: GET请求"""
        print("\n   方法3: GET请求")
        
        url = urljoin(self.base_url, "/")
        params = {
            'action': 'login',
            'username': self.username,
            'password': self.password
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, ssl=self.ssl_context) as response:
                    print(f"   状态码: {response.status}")
                    content = await response.text()
                    print(f"   响应长度: {len(content)} 字符")
                    
                    try:
                        json_data = json.loads(content)
                        print(f"   JSON响应: {json_data}")
                    except json.JSONDecodeError:
                        print("   响应不是JSON格式")
                        
            except Exception as e:
                print(f"   ❌ 请求错误: {e}")
    
    async def test_alternative_credentials(self):
        """测试其他可能的凭据"""
        print("\n" + "=" * 60)
        print("3. 测试其他可能的凭据...")
        
        # 常见的默认凭据
        credentials = [
            ("admin", "admin"),
            ("azkaban", "azkaban"),
            ("zhengan", "123456"),
            ("zhengan", "password"),
            ("zhengan", "zhengan"),
        ]
        
        for username, password in credentials:
            print(f"\n   测试凭据: {username}/{password}")
            await self._test_single_credential(username, password)
    
    async def _test_single_credential(self, username, password):
        """测试单个凭据"""
        url = urljoin(self.base_url, "/")
        data = {
            'action': 'login',
            'username': username,
            'password': password
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, ssl=self.ssl_context) as response:
                    content = await response.text()
                    
                    try:
                        json_data = json.loads(content)
                        if 'session.id' in json_data:
                            print(f"   ✅ 成功! session.id: {json_data['session.id']}")
                            return True
                        elif 'error' in json_data:
                            print(f"   ❌ 失败: {json_data['error']}")
                    except json.JSONDecodeError:
                        print(f"   ❌ 响应格式异常")
                        
            except Exception as e:
                print(f"   ❌ 请求错误: {e}")
        
        return False
    
    def print_manual_curl_commands(self):
        """打印手动测试的curl命令"""
        print("\n" + "=" * 60)
        print("4. 手动测试命令（在终端中执行）:")
        print("\n   # 方法1: POST表单数据")
        print(f'   curl -k -X POST "{self.base_url}/" \\')
        print(f'        -d "action=login&username={self.username}&password={self.password}" \\')
        print('        -H "Content-Type: application/x-www-form-urlencoded"')
        
        print("\n   # 方法2: GET请求")
        print(f'   curl -k "{self.base_url}/?action=login&username={self.username}&password={self.password}"')
        
        print("\n   # 方法3: 检查Azkaban版本和API文档")
        print(f'   curl -k "{self.base_url}/help"')
        print(f'   curl -k "{self.base_url}/api"')

async def main():
    print("Azkaban连接诊断工具")
    print("当前配置:")
    print(f"  URL: https://172.16.3.233:34006")
    print(f"  用户名: zhengan")
    print(f"  密码: za123")
    
    tester = AzkabanTester()
    
    # 执行所有测试
    await tester.test_connection()
    await tester.test_login_methods()
    await tester.test_alternative_credentials()
    
    # 打印手动命令
    tester.print_manual_curl_commands()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("\n建议下一步:")
    print("1. 如果所有自动测试都失败，请尝试手动curl命令")
    print("2. 检查Azkaban Web界面是否可以正常登录")
    print("3. 联系Azkaban管理员确认正确的用户名和密码")
    print("4. 检查Azkaban服务器日志以获取更多信息")

if __name__ == "__main__":
    asyncio.run(main()) 