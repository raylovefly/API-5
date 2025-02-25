# API性能对比测试工具

## 项目概述

这是一个用于对比测试多个AI平台API性能和功能的Python脚本工具。目前支持阿里云、火山引擎、腾讯云、硅基流动和OpenRouter五个平台的API调用测试，提供统一的性能指标统计和对比分析功能。

## 主要特性

- 支持五大平台API测试：
  - 阿里云
  - 火山引擎
  - 腾讯云
  - 硅基流动
  - OpenRouter
- 统一的性能指标统计：
  - 网络延迟
  - 首个token响应时间
  - 输出耗时
  - 总体请求耗时
  - Token使用统计（输入Token、输出Token、总Token）
  - 输出速度（token/s）
- 自动推导缺失指标（确保数据完整性）
- 实时监控每个平台的响应表现
- 支持流式响应和实时显示
- 生成详细的性能对比报告和分析
- 自动生成性能排名和优势分析

## 环境要求

- Python 3.x
- 依赖包：
  - openai Python包（用于OpenRouter接口）
  - python-dotenv包（环境变量管理）
  - tabulate包（表格化数据展示）
  - asyncio包（并发请求处理）

## 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包：
```bash
pip install openai python-dotenv tabulate asyncio
```
3. 在项目根目录创建.env文件，配置各平台API密钥：
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

# 硅基流动平台配置
SILICONFLOW_API_KEY=your-siliconflow-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn
SILICONFLOW_MODEL_ID=deepseek-ai/DeepSeek-V3

# OpenRouter配置
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL_ID=deepseek/deepseek-r1
```

## 使用方法

### 运行全部平台测试

执行以下命令运行所有平台的API测试：

```bash
python run_tests.py
```

程序将并发测试所有平台，生成统一格式的性能对比报告，包括各平台的性能数据和分析。

### 单独测试特定平台

```bash
python aliyun_test.py     # 测试阿里云
python huoshanyinqing.py  # 测试火山引擎
python tencent_test.py    # 测试腾讯云
python siliconflow_test.py # 测试硅基流动
python openrout.py        # 测试OpenRouter
```

## 性能指标说明

### 时间指标

- **网络延迟**：从发送请求到首次收到网络响应的时间
- **首token响应**：从发送请求到接收到第一个token的时间
- **输出耗时**：从接收到第一个token到接收完所有token的时间
- **总耗时**：整个请求的完整时间（从发送请求到完成响应）

### Token统计

- **输入Token**：请求消息中的token数量
- **输出Token**：响应内容的token数量
- **总Token**：输入Token和输出Token的总和
- **输出token/s**：输出Token数量除以输出耗时，表示生成速率

## 结果分析

测试程序会自动生成以下分析：

1. **性能排名**：在各项指标上表现最佳的平台
2. **各平台特点分析**：每个平台的优势和适用场景
3. **性能对比图表**：直观展示各平台在不同指标上的表现差异
4. **详细的指标报告**：所有测试指标的详细数据

## 最佳实践建议

1. **测试环境**：
   - 在稳定的网络环境下测试
   - 多次测试取平均值，避免偶然因素影响
   - 在相近时间段内测试各平台，减少时间差异影响

2. **结果解读**：
   - 根据具体应用场景选择关注的指标
   - 综合考虑性能、成本和功能需求
   - 关注长期稳定性，不仅是单次测试结果

3. **应用场景匹配**：
   - 实时交互场景：关注首token响应和输出速率
   - 内容生成场景：关注输出质量和总Token数
   - 大规模应用：关注API稳定性和成本效益

## 注意事项

- 所有平台的测试使用相同的查询内容和环境配置，确保测试结果的可比性
- Token计算基于UTF-8编码字节长度，可能与平台实际计费标准有差异
- 测试数据可能受网络波动、服务器负载等因素影响，建议多次测试
- API密钥安全管理至关重要，避免泄露或公开共享
- 各平台可能有不同的计费标准和使用限制，详情请参考官方文档

## 结果文件说明

测试完成后，程序会生成带有时间戳的结果文件，包含：
- 完整的性能对比表格
- 性能分析摘要
- 各平台详细指标
- 测试说明和注意事项

文件格式为：`test_results_YYYYMMDD_HHMMSS.txt`