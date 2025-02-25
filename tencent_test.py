# -*- coding: utf-8 -*-

'''
腾讯云API测试工具

功能说明：
- 支持腾讯云API的流式响应调用
- 实时显示AI响应内容
- 提供完整的性能统计指标

运行命令：
python tencent_test.py

配置参数：
⭐ API密钥：需在.env文件中设置TENCENT_API_KEY
⭐ API地址：可在base_url中修改API接口地址
⭐ 模型选择：可在model参数中指定使用的模型
⭐ 流式响应：stream参数控制是否使用流式响应
'''

import sys
import time
from openai import OpenAI
from config import config

# 初始化OpenAI客户端
client = OpenAI(
    api_key=config.tencent['api_key'],
    base_url=config.tencent['base_url']
)

# 测试消息
# =============================================
# 🔧 测试消息配置 (常用修改部分)
# =============================================
messages = [
    {"role": "user", "content": "100.9和100.11谁大？"}
]
# 使用配置参数
model = config.tencent['model']
stream = config.tencent['stream']

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

print("正在发送API请求...")

try:
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
    
    # 显示性能统计信息
    print("\n\n📊 性能统计：")
    print("网络延迟：{:.2f}秒".format(network_latency))
    print("首个token响应：{:.2f}秒".format(first_token_time - start_time))
    print("实际输出耗时：{:.2f}秒".format(output_time))
    print("总耗时：{:.2f}秒".format(total_time))
    print("\n📝 Token统计：")
    print("输入Token：{}".format(input_tokens))
    print("输出Token：{}".format(output_tokens))
    if output_time > 0:
        output_speed = output_tokens / output_time
        print("输出速度：{:.2f} token/s (计算方式：{} / {:.2f})".format(output_speed, output_tokens, output_time))
    print("————————————")
    print("总消耗Token：{}".format(input_tokens + output_tokens))

except Exception as e:
    print("\n❌ 发生错误：{}".format(str(e)))
    exit(1)