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
import os
import json
import requests
from dotenv import load_dotenv
from tabulate import tabulate

# 加载环境变量
load_dotenv()

# 获取配置参数
api_key = os.getenv('SILICONFLOW_API_KEY')
base_url = os.getenv('SILICONFLOW_BASE_URL')
model_id = os.getenv('SILICONFLOW_MODEL_ID')

# 打印配置信息
print(f"使用API地址: {base_url}")
print(f"使用模型: {model_id}")
print(f"API密钥: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

# 测试消息
# =============================================
# 🔧 测试消息配置 (常用修改部分)
# =============================================
messages = [
    {"role": "user", "content": "100.9和100.11谁大？"}
]

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
    
    # API请求URL - 硅基流动API的标准格式
    url = f"{base_url}/v1/chat/completions"
    
    # 打印完整的请求URL
    print(f"完整请求URL: {url}")
    
    # 请求体 - 使用与单独测试相同的格式
    payload = {
        "model": model_id,
        "messages": messages,
        "stream": True,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"请求模型: {model_id}")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
    
    # 记录开始时间
    start_time = time.time()
    first_token_time = None
    network_latency = None
    content = ""
    
    # 发送流式请求
    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    # 获取首次网络连接时间
    network_latency = time.time() - start_time
    
    # 检查响应状态
    if response.status_code != 200:
        raise Exception(f"API请求失败: HTTP {response.status_code} - {response.text}")
    
    print("\n🔍 开始接收响应流：")
    
    # 处理流式响应
    for line in response.iter_lines():
        if line:
            # 记录首个token的时间
            if first_token_time is None:
                first_token_time = time.time()
                print("首个token响应时间：{:.2f}秒".format(first_token_time - start_time))
            
            # 解析SSE格式的数据
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                json_str = line_text[6:]  # 去掉'data: '前缀
                if json_str.strip() == '[DONE]':
                    break
                
                try:
                    delta = json.loads(json_str)
                    if 'choices' in delta and len(delta['choices']) > 0:
                        if 'delta' in delta['choices'][0] and 'content' in delta['choices'][0]['delta']:
                            chunk = delta['choices'][0]['delta']['content']
                            content += chunk
                            write_stream_content(chunk)
                except json.JSONDecodeError:
                    continue
    
    # 计算结束时间和总耗时
    end_time = time.time()
    total_time = end_time - start_time
    
    # 计算实际输出耗时（总时间 - 首个token时间 - 网络延迟）
    output_time = total_time - (first_token_time - start_time) if first_token_time else 0
    
    # 计算token使用情况
    input_tokens = calculate_input_tokens(messages)
    output_tokens = calculate_output_tokens(content)
    output_speed = output_tokens / output_time if output_time > 0 else 0
    
    # 准备性能指标数据
    performance_metrics = {
        'network_latency': network_latency or 0,
        'first_token_time': (first_token_time - start_time) if first_token_time else 0,
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
    total_time = end_time - start_time
    metrics = {
        'network_latency': 0,
        'first_token_time': 0,
        'output_time': 0,
        'total_time': total_time,
        'input_tokens': calculate_input_tokens(messages),
        'output_tokens': 0,
        'total_tokens': calculate_input_tokens(messages),
        'output_speed': 0
    }
    
    # 显示已获得的性能统计信息
    print("\n📊 性能统计：")
    print(generate_performance_table(metrics))
    print("\n📝 Token统计：")
    print(generate_token_table(metrics))