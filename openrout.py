'''
OpenRouter API测试工具

功能说明：
- 支持OpenRouter API的流式响应调用
- 实时显示AI响应内容
- 提供完整的性能统计指标
- 美化的表格输出格式
- 性能数据可视化展示

运行命令：
python openrouter_test.py

配置参数：
⭐ API密钥：需在.env文件中设置OPENAI_API_KEY
⭐ API地址：使用OpenRouter的API地址
⭐ 模型选择：使用deepseek/deepseek-r1模型
⭐ 流式响应：默认开启流式响应
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
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')
model_id = os.getenv('OPENAI_MODEL_ID')

# 打印配置信息
print(f"使用API地址: {base_url}")
print(f"使用模型: {model_id}")
print(f"API密钥: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

# 测试消息
# =============================================
# 🔧 测试消息配置 (常用修改部分)
# =============================================
messages = [
    {"role": "user", "content": "你是谁？请用中文回答"}
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
    
    # API请求URL
    url = f"{base_url}/chat/completions"
    
    # 请求体
    payload = {
        "model": model_id,
        "messages": messages,
        "stream": True,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7
    }
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "API Test Tool"
    }
    
    print(f"请求URL: {url}")
    print(f"请求模型: {model_id}")
    
    # 记录开始时间
    start_time = time.time()
    first_token_time = None
    network_latency = None
    content = ""
    
    # 发送流式请求
    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    # 获取首次网络连接时间
    network_latency = time.time() - start_time
    print(f"\n网络延迟: {network_latency:.2f}秒")
    
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
                print("\n首个token响应时间：{:.2f}秒".format(first_token_time - start_time))
            
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
    
    # 计算实际输出耗时（总时间 - 首个token时间）
    output_time = total_time - (first_token_time - start_time)
    print(f"\n实际输出耗时: {output_time:.2f}秒")
    
    # 计算token使用情况
    input_tokens = calculate_input_tokens(messages)
    output_tokens = calculate_output_tokens(content)
    output_speed = output_tokens / output_time if output_time > 0 else 0
    
    # 显示Generation details
    print("\n\nGeneration details")
    print("Model", model_id)
    print("Model ID", "openrouter/" + model_id)
    print("Provider", "OpenRouter")
    print("First token latency", "{:.2f} seconds".format(first_token_time - start_time))
    print("Output time", "{:.2f} seconds".format(output_time))
    print("Network latency", "{:.2f} seconds".format(network_latency))
    if output_time > 0:
        throughput = output_tokens / output_time
        print("Throughput", "{:.1f} tokens/second".format(throughput))
    print("Tokens", "{} prompt → {} completion".format(input_tokens, output_tokens))

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