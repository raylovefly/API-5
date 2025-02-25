# -*- coding: utf-8 -*-

"""API性能对比测试工具

这个程序用于并发测试阿里云、火山引擎和腾讯云三个平台的API性能，并生成对比报告。

功能特点：
- 支持多平台API并发测试
- 统一的性能指标统计
- 表格化展示测试结果

使用方法：
1. 确保已安装所需依赖：
   pip install tabulate python-dotenv

2. 配置好config.py中的API参数和.env中的密钥

3. 运行测试：
   python run_tests.py

输出格式：
程序将以表格形式展示以下指标：
- 网络延迟（秒）
- 首token响应时间（秒）
- 输出耗时（秒）
- 总耗时（秒）
- 输入Token数量
- 输出Token数量
- Token输出速率（token/s）
- 总Token数量
"""

import asyncio
import subprocess
import re
from tabulate import tabulate

def extract_metrics(output):
    metrics = {
        '网络延迟': None,
        '首token响应': None,
        '输出耗时': None,
        '总耗时': None,
        '输入Token': None,
        '输出Token': None
    }
    
    # 解析性能统计数据
    for line in output.split('\n'):
        if '网络延迟：' in line:
            metrics['网络延迟'] = float(re.search(r'网络延迟：(\d+\.\d+)秒', line).group(1))
        elif '首个token响应时间：' in line:
            metrics['首token响应'] = float(re.search(r'首个token响应时间：(\d+\.\d+)秒', line).group(1))
        elif '实际输出耗时：' in line:
            metrics['输出耗时'] = float(re.search(r'实际输出耗时：(\d+\.\d+)秒', line).group(1))
        elif '总耗时：' in line:
            metrics['总耗时'] = float(re.search(r'总耗时：(\d+\.\d+)秒', line).group(1))
        elif '输入Token：' in line:
            metrics['输入Token'] = int(re.search(r'输入Token：(\d+)', line).group(1))
        elif '输出Token：' in line:
            metrics['输出Token'] = int(re.search(r'输出Token：(\d+)', line).group(1))
    
    # 计算输出速率
    if metrics['输出耗时'] and metrics['输出Token']:
        metrics['输出token/s'] = round(metrics['输出Token'] / metrics['输出耗时'], 2)
    else:
        metrics['输出token/s'] = 0
    
    # 计算总Token
    if metrics['输入Token'] is not None and metrics['输出Token'] is not None:
        metrics['总Token'] = metrics['输入Token'] + metrics['输出Token']
    else:
        metrics['总Token'] = 0
        
    return metrics

async def run_test(script_name):
    try:
        process = await asyncio.create_subprocess_exec(
            'python', script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode('utf-8')
    except Exception as e:
        print(f'运行 {script_name} 时发生错误: {str(e)}')
        return ''

async def main():
    # 定义测试脚本和对应的平台名称
    tests = [
        ('aliyun_test.py', '阿里云'),
        ('huoshanyinqing.py', '火山引擎'),
        ('tencent_test.py', '腾讯云')
    ]
    
    # 并发运行所有测试
    results = await asyncio.gather(*[run_test(script) for script, _ in tests])
    
    # 解析结果
    metrics_data = {}
    for (_, platform), output in zip(tests, results):
        metrics_data[platform] = extract_metrics(output)
    
    # 准备表格数据
    headers = ['指标 单位（秒）', '阿里云', '火山引擎', '腾讯云']
    rows = [
        ['网络延迟'] + [metrics_data[p]['网络延迟'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['首token响应'] + [metrics_data[p]['首token响应'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['输出耗时'] + [metrics_data[p]['输出耗时'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['总耗时'] + [metrics_data[p]['总耗时'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['输入Token'] + [metrics_data[p]['输入Token'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['输出Token'] + [metrics_data[p]['输出Token'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['输出token/s'] + [metrics_data[p]['输出token/s'] for p in ['阿里云', '火山引擎', '腾讯云']],
        ['总Token'] + [metrics_data[p]['总Token'] for p in ['阿里云', '火山引擎', '腾讯云']]
    ]
    
    # 打印表格
    print(tabulate(rows, headers=headers, tablefmt='grid'))

if __name__ == '__main__':
    asyncio.run(main())