# 多平台大模型 API 测试工具

## 项目概述

这是一个用于测试多个大模型 API 平台性能和功能的 Python 工具集。支持阿里云、火山引擎、腾讯云、硅基流动和 OpenRouter 等平台的 API 性能测试，提供详细的性能指标对比，包括网络延迟、响应时间和 Token 使用情况的实时监控。

## 主要特性
- 支持多平台 API 的流式响应调用
- 实时显示 AI 响应内容
- 支持多平台性能对比测试
- 提供完整的性能统计指标：
  - 网络延迟
  - 首个 token 响应时间
  - 输出耗时
  - 总体请求耗时
  - Token 使用统计
  - 输出速度（token/s）
- 自动计算缺失指标，确保数据完整一致
- 生成详细的性能对比报告和分析

## 支持平台
- **阿里云**：基于 deepseek-r1 模型
- **火山引擎**：基于 deepseek-v3-241226 模型
- **腾讯云**：基于 deepseek-r1 模型
- **硅基流动**：基于 DeepSeek-V3 模型
- **OpenRouter**：支持多种模型，本测试使用 deepseek/deepseek-r1

## 环境要求
- Python 3.x
- openai Python 包
- python-dotenv 包
- tabulate 包
- asyncio 包

## 安装步骤
1. 克隆或下载项目代码
2. 安装依赖包：
```bash
pip install openai python-dotenv tabulate asyncio
```
3. 在项目根目录创建 .env 文件，配置各平台 API 密钥：
```
# 阿里云配置
ALIYUN_API_KEY=your-aliyun-api-key
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
ALIYUN_MODEL_ID=deepseek-r1

# 火山引擎配置
ARK_API_KEY=your-ark-api-key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL_ID=deepseek-v3-241226

# 腾讯云配置
TENCENT_API_KEY=your-tencent-api-key
TENCENT_BASE_URL=https://api.lkeap.cloud.tencent.com/v1
TENCENT_MODEL_ID=deepseek-r1

# 硅基流动配置
SILICONFLOW_API_KEY=your-siliconflow-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn
SILICONFLOW_MODEL_ID=deepseek-ai/DeepSeek-V3

# OpenRouter 配置
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL_ID=deepseek/deepseek-r1
```

## 使用方法

### 单平台测试
运行特定平台的测试脚本：
```bash
# 阿里云测试
python aliyun_test.py

# 火山引擎测试
python huoshanyinqing.py

# 腾讯云测试
python tencent_test.py

# 硅基流动测试
python siliconflow_test.py

# OpenRouter 测试
python openrout.py
```

### 多平台对比测试
运行综合测试脚本，同时测试所有平台并生成对比报告：
```bash
python run_tests.py
```

## 最新测试结果

### 平台性能对比
| 指标 | 阿里云 | 火山引擎 | 腾讯云 | 硅基流动 | OpenRouter |
|------|--------|---------|--------|---------|------------|
| 网络延迟(秒) | 1.01 | 0.70 | 1.54 | 0.96 | 1.54 |
| 首token响应(秒) | 1.01 | 0.70 | 1.55 | 0.96 | 1.90 |
| 输出耗时(秒) | 4.32 | 4.34 | 99.56 | 9.57 | 40.64 |
| 总耗时(秒) | 6.34 | 5.74 | 102.65 | 10.53 | 42.54 |
| 输入Token(个) | 36 | 22 | 23 | 23 | 30 |
| 输出Token(个) | 163 | 522 | 784 | 576 | 313 |
| 输出token/s(个/秒) | 37.73 | 120.28 | 7.87 | 60.20 | 7.70 |
| 总Token(个) | 199 | 544 | 807 | 599 | 343 |

## 性能指标说明
### 时间指标
- **网络延迟**：从发送请求到首次收到网络响应的时间
- **首token响应**：从发送请求到接收到第一个token的时间
- **输出耗时**：从接收到第一个token到接收完所有token的时间
- **总耗时**：整个请求的完整时间（从发送请求到完成响应）

### Token统计
- **输入Token**：请求消息中的token数量
- **输出Token**：响应内容的token数量
- **输出token/s**：输出Token数量除以输出耗时，表示生成速率
- **总Token**：输入Token和输出Token的总和

## 性能分析摘要
- **最快首token响应**: 火山引擎 (0.70秒)
- **最高输出速率**: 火山引擎 (120.28 token/秒)
- **最短总耗时**: 火山引擎 (5.74秒)
- **输出内容最多**: 腾讯云 (784个token)

## 各平台特点分析

### 火山引擎
- **优势**: 网络延迟最低(0.70秒)，首token响应最快(0.70秒)，输出速率最高(120.28 token/秒)
- **特点**: 高效的响应处理能力和文本生成速度，极短的启动延迟
- **适用场景**: 实时对话系统、客服机器人、需要快速响应的应用场景

### 阿里云
- **优势**: 低网络延迟(1.01秒)，快速的首token响应(1.01秒)，稳定的输出速率(37.73 token/秒)
- **特点**: 性能均衡，适合各类通用场景
- **适用场景**: 企业级应用、需要稳定性和平衡性能的场景

### 硅基流动
- **优势**: 响应速度适中(0.96秒)，较高的输出效率(60.20 token/秒)
- **特点**: 输出效率高，适合内容生成场景
- **适用场景**: 内容创作、文档生成、对输出效率要求较高的场景

### 腾讯云
- **优势**: 输出内容最丰富(784个token)
- **特点**: 内容生成量大，但速度偏慢
- **适用场景**: 详细内容生成、复杂问题解答，对速度要求不高的场景

### OpenRouter
- **优势**: 多模型支持，统一API接入
- **特点**: 灵活性高，可根据需求选择不同模型
- **适用场景**: 需要测试多种模型的开发者，特定模型需求的应用

## 性价比排名
1. **火山引擎**：综合性能最佳，特别适合需要快速生成内容的场景
2. **阿里云**：稳定均衡，适合企业级应用和生产环境
3. **硅基流动**：较高的输出效率，适合内容生成场景
4. **OpenRouter**：灵活性高，适合多模型测试和特定需求
5. **腾讯云**：内容生成丰富但速度较慢，适合非实时场景

## 测试环境与条件
- 所有测试在同一网络环境下进行
- 使用相同的测试问题和请求格式
- 每个平台使用相同或类似的模型配置
- 流式输出(Stream)模式下的性能表现

## 测试结果文件说明
测试完成后，程序会生成带有时间戳的详细测试报告文件：
```
test_results_YYYYMMDD_HHMMSS.txt
```

文件包含：
- 完整的性能对比表格
- 性能分析摘要
- 各平台详细指标
- 测试说明和注意事项

## 注意事项
- API 密钥请妥善保管，不要泄露
- 测试结果会受到网络环境和服务器负载的影响，建议多次测试取平均值
- Token 统计采用 UTF-8 编码字节长度计算，可能与实际收费的 token 数有所差异
- 不同时间段的测试结果可能有所不同，建议在评估时进行多次测试