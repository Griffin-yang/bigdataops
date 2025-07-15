"""
配置管理器
简化版本，只支持从config.env文件加载配置
"""

import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "config.env"
        self._config_cache = None
    
    def load_config(self) -> Dict[str, str]:
        """加载配置文件"""
        if self._config_cache is not None:
            return self._config_cache
        
        config = {}
        
        # 如果配置文件存在，加载配置
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
        
        self._config_cache = config
        return config
    
    def get_config(self, key: str, default: str = "") -> str:
        """获取配置值"""
        config = self.load_config()
        return config.get(key, default)
    
    def get_current_config(self) -> Dict[str, str]:
        """获取当前配置"""
        return self.load_config()
    
    def validate_config(self, config: Dict[str, str]) -> bool:
        """验证配置完整性"""
        required_keys = [
            'ENVIRONMENT',
            'LDAP_SERVER',
            'PROMETHEUS_URL',
            'MYSQL_HOST',
            'MYSQL_DB'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in config or not config[key]:
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing_keys)}")
        
        return True


# 创建全局配置管理器实例
config_manager = ConfigManager() 