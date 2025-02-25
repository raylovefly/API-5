# -*- coding: utf-8 -*-

"""API性能对比测试工具

这个程序用于并发测试阿里云、火山引擎、腾讯云、硅基流动、OpenRouter和DeepSeek官方API六个平台的API性能，并生成对比报告。

功能特点：
- 支持多平台API并发测试
- 统一的性能指标统计
- 表格化展示测试结果

启动方式：
1. 确保已安装所需依赖：
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install tabulate python-dotenv openai

2. 配置好.env中的各平台API密钥

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
import datetime
import os

def extract_metrics(output, verbose=False, platform_name=None):
    metrics = {
        '网络延迟': None,
        '首token响应': None,
        '输出耗时': None,
        '总耗时': None,
        '输入Token': None,
        '输出Token': None,
        '输出token/s': None,
        '总Token': None
    }
    
    if verbose:
        print(f"\n[调试] 开始从{platform_name or ''}输出中提取指标...")
    
    # 正则表达式模式，匹配各种可能的输出格式
    patterns = {
        '网络延迟': [
            r'网络延迟[：:]\s*(\d+\.?\d*)\s*秒',
            r'网络延迟\s*\|\s*(\d+\.?\d*)',
            r'Network latency\s+(\d+\.\d+)',
        ],
        '首token响应': [
            r'首[个]?token响应[时间]?[：:]\s*(\d+\.?\d*)\s*秒',
            r'首token响应\s*\|\s*(\d+\.?\d*)',
            r'First token latency\s+(\d+\.\d+)',
        ],
        '输出耗时': [
            r'[实际]?输出耗时[：:]\s*(\d+\.?\d*)\s*秒',
            r'[实际]?输出耗时\s*\|\s*(\d+\.?\d*)',
            r'Output time\s+(\d+\.\d+)',
        ],
        '总耗时': [
            r'总耗时[：:]\s*(\d+\.?\d*)\s*秒',
            r'总耗时\s*\|\s*(\d+\.?\d*)',
        ],
        '输入Token': [
            r'输入Token[：:]\s*(\d+)',
            r'输入Token\s*\|\s*(\d+)',
            r'Tokens\s+(\d+)\s+prompt',
        ],
        '输出Token': [
            r'输出Token[：:]\s*(\d+)',
            r'输出Token\s*\|\s*(\d+)',
            r'completion\s+(\d+)',
            r'prompt → (\d+) completion',
        ],
        '输出token/s': [
            r'输出[速率]?[：:]\s*(\d+\.?\d*)\s*token/s',
            r'输出速率\s*\|\s*(\d+\.?\d*)',
            r'Throughput\s+(\d+\.\d+)',
        ],
    }
    
    # 遍历每一行输出，应用所有可能的模式
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        for metric, regex_patterns in patterns.items():
            if metrics[metric] is not None:
                continue  # 已经找到了这个指标，跳过
                
            for pattern in regex_patterns:
                match = re.search(pattern, line)
                if match:
                    value = match.group(1)
                    if verbose:
                        print(f"[调试] 匹配到 {metric}: '{line}' 使用模式 '{pattern}'")
                        print(f"[调试] 提取值: {value}")
                    
                    if metric in ['输入Token', '输出Token', '总Token']:
                        metrics[metric] = int(value)
                    else:
                        metrics[metric] = float(value)
                    break
    
    if verbose:
        print(f"[调试] 指标直接提取结果:")
        for k, v in metrics.items():
            print(f"[调试]   - {k}: {v}")
    
    # 计算未被直接提取的指标
    # 1. 总Token = 输入Token + 输出Token
    if metrics['总Token'] is None and metrics['输入Token'] is not None and metrics['输出Token'] is not None:
        metrics['总Token'] = metrics['输入Token'] + metrics['输出Token']
        if verbose:
            print(f"[调试] 计算总Token: {metrics['输入Token']} + {metrics['输出Token']} = {metrics['总Token']}")
    
    # 2. 输出token/s = 输出Token / 输出耗时
    if metrics['输出token/s'] is None and metrics['输出Token'] is not None and metrics['输出耗时'] is not None and metrics['输出耗时'] > 0:
        metrics['输出token/s'] = round(metrics['输出Token'] / metrics['输出耗时'], 2)
        if verbose:
            print(f"[调试] 计算输出token/s: {metrics['输出Token']} / {metrics['输出耗时']} = {metrics['输出token/s']}")
    
    # 3. 总耗时计算方法一: 首token响应 + 输出耗时
    if metrics['总耗时'] is None and metrics['首token响应'] is not None and metrics['输出耗时'] is not None:
        metrics['总耗时'] = round(metrics['首token响应'] + metrics['输出耗时'], 4)
        if verbose:
            print(f"[调试] 计算总耗时(方法一): {metrics['首token响应']} + {metrics['输出耗时']} = {metrics['总耗时']}")
    
    # 4. 总耗时计算方法二: 如果有网络延迟, 首token响应, 输出token/s, 可以估算总耗时
    if metrics['总耗时'] is None and metrics['首token响应'] is not None and metrics['输出Token'] is not None and metrics['输出token/s'] is not None and metrics['输出token/s'] > 0:
        estimated_output_time = metrics['输出Token'] / metrics['输出token/s']
        metrics['总耗时'] = round(metrics['首token响应'] + estimated_output_time, 4)
        if verbose:
            print(f"[调试] 计算总耗时(方法二): {metrics['首token响应']} + ({metrics['输出Token']} / {metrics['输出token/s']}) = {metrics['总耗时']}")
    
    # 5. 输出耗时计算: 如果总耗时 - 首token响应
    if metrics['输出耗时'] is None and metrics['总耗时'] is not None and metrics['首token响应'] is not None:
        metrics['输出耗时'] = round(metrics['总耗时'] - metrics['首token响应'], 4)
        if verbose:
            print(f"[调试] 计算输出耗时: {metrics['总耗时']} - {metrics['首token响应']} = {metrics['输出耗时']}")
    
    # 6. 首token响应计算: 如果总耗时 - 输出耗时
    if metrics['首token响应'] is None and metrics['总耗时'] is not None and metrics['输出耗时'] is not None:
        metrics['首token响应'] = round(metrics['总耗时'] - metrics['输出耗时'], 4)
        if verbose:
            print(f"[调试] 计算首token响应: {metrics['总耗时']} - {metrics['输出耗时']} = {metrics['首token响应']}")
    
    # 7. 计算输出token/s (多种情况)
    if metrics['输出token/s'] is None:
        if metrics['输出Token'] is not None and metrics['输出耗时'] is not None and metrics['输出耗时'] > 0:
            metrics['输出token/s'] = round(metrics['输出Token'] / metrics['输出耗时'], 2)
            if verbose:
                print(f"[调试] 计算输出token/s(备选): {metrics['输出Token']} / {metrics['输出耗时']} = {metrics['输出token/s']}")
        else:
            metrics['输出token/s'] = 0
            if verbose:
                print(f"[调试] 设置默认输出token/s = 0")
    
    # 最终空值处理 - 设置默认值避免表格出现None
    for key in metrics:
        if metrics[key] is None:
            if key in ['输入Token', '输出Token', '总Token']:
                metrics[key] = 0
                if verbose:
                    print(f"[调试] 设置默认值 {key} = 0")
            elif key == '输出token/s':
                metrics[key] = 0
                if verbose:
                    print(f"[调试] 设置默认值 {key} = 0")
            else:
                metrics[key] = 0.0
                if verbose:
                    print(f"[调试] 设置默认值 {key} = 0.0")
    
    if verbose:
        print("[调试] 最终指标结果:")
        for k, v in metrics.items():
            print(f"[调试]   - {k}: {v}")
                
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

async def save_results_to_file(table_content, metrics_data=None, platforms=None):
    # 生成带时间戳的文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_results_{timestamp}.txt'
    
    # 确保文件写入是异步的
    async with asyncio.Lock():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('=================================================\n')
            f.write('             API性能测试结果报告                 \n')
            f.write('=================================================\n\n')
            f.write(f'测试时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'测试平台: 阿里云、火山引擎、腾讯云、硅基流动、OpenRouter和DeepSeek官方\n\n')
            f.write('测试指标对比表格:\n')
            f.write(table_content)
            
            # 如果提供了详细的指标数据，添加性能分析摘要
            if metrics_data and platforms:
                f.write('\n\n性能分析摘要:\n')
                
                # 最快首token响应
                fastest_first_token = min([(p, metrics_data[p]['首token响应']) for p in platforms], key=lambda x: x[1])
                f.write(f"- 最快首token响应: {fastest_first_token[0]} ({fastest_first_token[1]:.2f}秒)\n")
                
                # 最高输出速率
                fastest_output = max([(p, metrics_data[p]['输出token/s']) for p in platforms], key=lambda x: x[1])
                f.write(f"- 最高输出速率: {fastest_output[0]} ({fastest_output[1]:.2f}token/s)\n")
                
                # 最短总耗时
                fastest_total = min([(p, metrics_data[p]['总耗时']) for p in platforms], key=lambda x: x[1])
                f.write(f"- 最短总耗时: {fastest_total[0]} ({fastest_total[1]:.2f}秒)\n")
                
                # 输出内容最多
                most_output = max([(p, metrics_data[p]['输出Token']) for p in platforms], key=lambda x: x[1])
                f.write(f"- 输出内容最多: {most_output[0]} ({most_output[1]}个token)\n")
                
                # 添加各平台特点分析
                f.write('\n各平台特点:\n')
                for p in platforms:
                    f.write(f"- {p}:\n")
                    f.write(f"  网络延迟: {metrics_data[p]['网络延迟']:.2f}秒\n")
                    f.write(f"  首token响应: {metrics_data[p]['首token响应']:.2f}秒\n")
                    f.write(f"  输出耗时: {metrics_data[p]['输出耗时']:.2f}秒\n")
                    f.write(f"  总耗时: {metrics_data[p]['总耗时']:.2f}秒\n")
                    f.write(f"  输出token/s: {metrics_data[p]['输出token/s']:.2f}个/秒\n")
                    f.write(f"  总Token: {metrics_data[p]['总Token']}个\n\n")
            
            f.write('\n测试说明:\n')
            f.write('1. 网络延迟: 从发送请求到首次收到网络响应的时间\n')
            f.write('2. 首token响应: 从发送请求到接收到第一个token的时间\n')
            f.write('3. 输出耗时: 从接收到第一个token到接收完所有token的时间\n')
            f.write('4. 总耗时: 整个请求的完整时间\n')
            f.write('5. 输出token/s: 输出Token数量除以输出耗时\n\n')
            f.write('注意: 所有平台使用相同的测试消息和测试环境，数据在同一时间段采集\n')
    
    print(f'\n测试结果已保存到文件: {filename}')

async def main():
    # 是否开启详细调试模式
    DEBUG_MODE = False
    
    print("===== API性能对比测试工具 =====")
    print("开始性能测试，将并发测试6个平台的API性能...\n")
    
    # 定义测试脚本和对应的平台名称
    tests = [
        ('aliyun_test.py', '阿里云'),
        ('huoshanyinqing.py', '火山引擎'),
        ('tencent_test.py', '腾讯云'),
        ('siliconflow_test.py', '硅基流动'),
        ('openrout.py', 'OpenRouter'),
        ('deepseek_test.py', 'DeepSeek官方')
    ]
    
    # 并发运行所有测试
    print("正在并发执行测试，请稍候...\n")
    results = await asyncio.gather(*[run_test(script) for script, _ in tests])
    
    # 解析结果
    print("\n测试完成，正在处理结果...")
    metrics_data = {}
    for (script, platform), output in zip(tests, results):
        print(f"\n处理 {platform} 平台结果...")
        metrics = extract_metrics(output, verbose=DEBUG_MODE, platform_name=platform)
        metrics_data[platform] = metrics
        
        # 输出提取到的指标摘要
        print(f"  - 网络延迟: {metrics.get('网络延迟'):.2f}秒")
        print(f"  - 首token响应: {metrics.get('首token响应'):.2f}秒")
        print(f"  - 输出耗时: {metrics.get('输出耗时'):.2f}秒")
        print(f"  - 总耗时: {metrics.get('总耗时'):.2f}秒")
        print(f"  - 输入Token: {metrics.get('输入Token')}个")
        print(f"  - 输出Token: {metrics.get('输出Token')}个")
        print(f"  - 输出token/s: {metrics.get('输出token/s'):.2f}个/秒")
        print(f"  - 总Token: {metrics.get('总Token')}个")
    
    # 准备表格数据
    platforms = ['阿里云', '火山引擎', '腾讯云', '硅基流动', 'OpenRouter', 'DeepSeek官方']
    headers = ['指标'] + platforms
    rows = [
        ['网络延迟(秒)'] + [metrics_data[p].get('网络延迟', 0) for p in platforms],
        ['首token响应(秒)'] + [metrics_data[p].get('首token响应', 0) for p in platforms],
        ['输出耗时(秒)'] + [metrics_data[p].get('输出耗时', 0) for p in platforms],
        ['总耗时(秒)'] + [metrics_data[p].get('总耗时', 0) for p in platforms],
        ['输入Token(个)'] + [metrics_data[p].get('输入Token', 0) for p in platforms],
        ['输出Token(个)'] + [metrics_data[p].get('输出Token', 0) for p in platforms],
        ['输出token/s(个/秒)'] + [metrics_data[p].get('输出token/s', 0) for p in platforms],
        ['总Token(个)'] + [metrics_data[p].get('总Token', 0) for p in platforms]
    ]
    
    # 生成表格内容
    table_content = tabulate(rows, headers=headers, tablefmt='grid', floatfmt=".2f")
    
    # 打印表格
    print("\n所有平台性能指标对比：")
    print(table_content)
    
    # 性能分析摘要
    print("\n性能分析摘要：")
    # 找出最快的首token响应
    fastest_first_token = min([(p, metrics_data[p]['首token响应']) for p in platforms], key=lambda x: x[1])
    print(f"- 最快首token响应: {fastest_first_token[0]} ({fastest_first_token[1]:.2f}秒)")
    
    # 找出最高的输出速率
    fastest_output = max([(p, metrics_data[p]['输出token/s']) for p in platforms], key=lambda x: x[1])
    print(f"- 最高输出速率: {fastest_output[0]} ({fastest_output[1]:.2f}token/s)")
    
    # 找出最短的总耗时
    fastest_total = min([(p, metrics_data[p]['总耗时']) for p in platforms], key=lambda x: x[1])
    print(f"- 最短总耗时: {fastest_total[0]} ({fastest_total[1]:.2f}秒)")
    
    # 找出输出内容最多的
    most_output = max([(p, metrics_data[p]['输出Token']) for p in platforms], key=lambda x: x[1])
    print(f"- 输出内容最多: {most_output[0]} ({most_output[1]}个token)")
    
    # 保存结果到文件
    await save_results_to_file(table_content, metrics_data, platforms)
    
    print("\n测试完成！六个平台的性能指标统计标准已统一。")

if __name__ == '__main__':
    asyncio.run(main())