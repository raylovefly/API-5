# -*- coding: utf-8 -*-

'''
统一配置管理模块

功能说明：
- 集中管理所有API配置
- 自动加载环境变量
- 提供配置验证功能
'''

import os
from dotenv import load_dotenv

class APIConfig:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 验证必要的环境变量
        self._validate_env_vars()
        
        # 初始化配置
        self.init_configs()
    
    def _validate_env_vars(self):
        """验证必要的环境变量是否存在"""
        required_vars = [
            'ARK_API_KEY',
            'ALIYUN_API_KEY',
            'TENCENT_API_KEY',
            'SILICONFLOW_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f'缺少必要的环境变量: {", ".join(missing_vars)}')
    
    def init_configs(self):
        """初始化各API配置"""
        # 方舟API配置
        self.ark = {
            'api_key': os.getenv('ARK_API_KEY'),
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'deepseek-v3-241226',
            'stream': True
        }
        
        # 阿里云API配置
        self.aliyun = {
            'api_key': os.getenv('ALIYUN_API_KEY'),
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model': 'deepseek-r1',
            'stream': True
        }
        
        # 腾讯云API配置
        self.tencent = {
            'api_key': os.getenv('TENCENT_API_KEY'),
            'base_url': 'https://api.lkeap.cloud.tencent.com/v1',
            'model': 'deepseek-r1',
            'stream': True
        }
        
        # 硅基流动平台API配置
        self.siliconflow = {
            'api_key': os.getenv('SILICONFLOW_API_KEY'),
            'base_url': 'https://api.siliconflow.com/v1',
            'model': 'deepseek-ai/DeepSeek-R1',
            'stream': True
        }

# 创建全局配置实例
config = APIConfig()