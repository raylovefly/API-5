# -*- coding: utf-8 -*-

'''
硅基流动平台API测试工具

功能说明：
- 支持硅基流动API的流式响应调用
- 实时显示AI响应内容
- 提供完整的性能统计指标
- 美化的表格输出格式
- 性能数据可视化展示

运行命令：
python siliconflow_test.py

配置参数：
⭐ API密钥：需在.env文件中设置SILICONFLOW_API_KEY
⭐ API地址：可在base_url中修改API接口地址
⭐ 模型选择：可在model参数中指定使用的模型
⭐ 流式响应：stream参数控制是否使用流式响应

性能指标说明：
- 网络延迟：从发送请求到建立连接的时间
- 首token响应：从发送请求到收到第一个token的时间
- 实际输出耗时：去除网络延迟和首token响应后的纯输出时间
- Token统计：使用UTF-8编码字节长度计算
'''

import sys
import time
from openai import OpenAI
from config import config
from tabulate import tabulate

# 初始化OpenAI客户端
client = OpenAI(
    api_key=config.siliconflow['api_key'],
    base_url=config.siliconflow['base_url']
)

# 测试消息
# =============================================
# 🔧 测试消息配置 (常用修改部分)
# =============================================
messages = [
    {"role": "user", "content": "100.9和100.11谁大？"}
]
# 使用配置参数
model = config.siliconflow['model']
stream = config.siliconflow['stream']

# 计算输入token
def calculate_input_tokens(messages):
    total_tokens = 0
    for message in messages:
        total_tokens += len(message['content'].encode('utf-8'))
    return total_tokens

# 计算输出token
def calculate_output_tokens(content):
    return len(content.encode('utf-8'))

# 输出流式内容
def write_stream_content(text):
    sys.stdout.write(text)
    sys.stdout.flush()

# 生成性能统计表格
def generate_performance_table(metrics):
    headers = ['指标', '数值', '单位']
    rows = [
        ['网络延迟', f"{metrics['network_latency']:.2f}", '秒'],
        ['首token响应', f"{metrics['first_token_time']:.2f}", '秒'],
        ['实际输出耗时', f"{metrics['output_time']:.2f}", '秒'],
        ['总耗时', f"{metrics['total_time']:.2f}", '秒']
    ]
    return tabulate(rows, headers=headers, tablefmt='grid')

# 生成Token统计表格
def generate_token_table(metrics):
    headers = ['Token类型', '数量', '备注']
    rows = [
        ['输入Token', metrics['input_tokens'], '-'],
        ['输出Token', metrics['output_tokens'], '-'],
        ['总Token', metrics['total_tokens'], '-'],
        ['输出速率', f"{metrics['output_speed']:.2f}", 'token/s']
    ]
    return tabulate(rows, headers=headers, tablefmt='grid')

print("正在发送API请求...")

try:
    # 初始化性能指标
    metrics = {
        'network_latency': 0,
        'first_token_time': 0,
        'output_time': 0,
        'total_time': 0,
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0,
        'output_speed': 0
    }
    
    # 记录开始时间
    start_time = time.time()
    first_token_time = None
    network_latency = None
    content = ""
    reasoning_content = ""
    
    # 发送流式请求
    response = client.chat.completions.create(
        model=model,  # 使用配置的模型
        messages=messages,
        stream=stream  # 使用配置的流式响应设置
    )
    
    # 获取首次网络连接时间
    network_latency = time.time() - start_time
    
    print("\n🔍 开始接收响应流：")
    
    # 处理流式响应
    for chunk in response:
        # 记录首个token的时间
        if first_token_time is None:
            first_token_time = time.time()
            print("首个token响应时间：{:.2f}秒".format(first_token_time - start_time))
        
        # 处理推理内容
        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
            reasoning_content += chunk.choices[0].delta.reasoning_content
            write_stream_content(chunk.choices[0].delta.reasoning_content)
        # 处理普通内容
        elif hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
            write_stream_content(chunk.choices[0].delta.content)
    
    # 计算结束时间和总耗时
    end_time = time.time()
    total_time = end_time - start_time
    
    # 计算实际输出耗时（总时间 - 首个token时间 - 网络延迟）
    output_time = total_time - (first_token_time - start_time) - network_latency
    
    # 计算token使用情况
    input_tokens = calculate_input_tokens(messages)
    output_tokens = calculate_output_tokens(content)
    output_speed = output_tokens / output_time if output_time > 0 else 0
    
    # 准备性能指标数据
    performance_metrics = {
        'network_latency': network_latency,
        'first_token_time': first_token_time - start_time,
        'output_time': output_time,
        'total_time': total_time
    }
    
    # 准备Token统计数据
    token_metrics = {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'output_speed': output_speed
    }
    
    # 显示性能统计信息
    print("\n\n📊 性能统计：")
    print(generate_performance_table(performance_metrics))
    
    print("\n📝 Token统计：")
    print(generate_token_table(token_metrics))

except Exception as e:
    print("\n❌ 发生错误：{}".format(str(e)))
    
    # 即使发生错误也计算已获得的指标
    end_time = time.time()
    if network_latency is not None:
        metrics['network_latency'] = network_latency
    if first_token_time is not None:
        metrics['first_token_time'] = first_token_time - start_time
    metrics['total_time'] = end_time - start_time
    
    # 计算已获得的token数据
    metrics['input_tokens'] = calculate_input_tokens(messages)
    if content:
        metrics['output_tokens'] = calculate_output_tokens(content)
        metrics['total_tokens'] = metrics['input_tokens'] + metrics['output_tokens']
        if metrics['output_time'] > 0:
            metrics['output_speed'] = metrics['output_tokens'] / metrics['output_time']
    
    # 显示已获得的性能统计信息
    print("\n📊 部分性能统计：")
    print(generate_performance_table(metrics))
    print("\n📝 部分Token统计：")
    print(generate_token_table(metrics))
    
    # 不立即退出，让数据能够被收集
    pass