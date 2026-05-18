# XM - AI 智能体开发教学项目

基于 Python 标准库的 AI 智能体开发实践教程，从零开始理解 LLM API 调用、流式对话、上下文管理等核心概念。

## 环境要求

- Python 3.13+
- Windows / macOS / Linux
- 任意 OpenAI 兼容协议的 LLM API（如 OpenAI、DeepSeek、本地 ollama/vLLM 等）

## 快速开始

```powershell
# 1. 克隆项目后，创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
.\venv\Scripts\Activate.ps1   # Windows PowerShell
source venv/bin/activate       # macOS / Linux

# 3. 配置 API 参数
cp env.example .env            # 复制模板
# 编辑 .env，填入你的 LLM_API_KEY 等信息
```

## 项目结构

```
XM/
├── env.example                    # 环境变量配置模板（可提交到 Git）
├── .env                           # 实际配置（已被 .gitignore 排除）
├── .gitignore
├── README.md
├── practice01/                    # 第一课：HTTP 直连 LLM
│   └── llm_http_demo.py           #   标准库 http.client 调用 Chat API
└── practice02/                    # 第二课：工具调用与高级对话
    ├── llm_stream_chat.py         #   SSE 流式输出 + 多轮对话上下文
    ├── tool_call_demo.py          #   Function Calling 工具调用（6个工具）
    └── fast_chat.py               #   快速非流式聊天模式
```

## 课程大纲

### Practice 01 - HTTP 直连 LLM

`practice01/llm_http_demo.py`

- 用 Python 标准库 `http.client` 直接构造 OpenAI 兼容协议请求
- 手动解析 `.env` 环境变量（零第三方依赖）
- 统计 token 消耗、请求耗时、输出速度

**运行:**
```powershell
python practice01/llm_http_demo.py
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| Chat Completions API | POST `/v1/chat/completions`，发送 messages 数组 |
| Token 统计 | 从响应的 `usage` 字段获取 prompt/completion/total tokens |
| HTTP 头认证 | `Authorization: Bearer <api_key>` |

---

### Practice 02 - 流式终端对话

`practice02/llm_stream_chat.py`

- 终端交互式聊天界面，循环等待用户输入
- SSE (Server-Sent Events) 流式输出，逐 token 实时打印
- 多轮对话历史自动追加到上下文，维持对话连贯性
- Ctrl+C 优雅退出
- 支持 `/clear` 命令清空历史

**运行:**
```powershell
python practice02/llm_stream_chat.py
```

**对话示例:**
```
==========================================================
  🤖  流式聊天终端  |  基于 OpenAI 兼容协议
==========================================================
  模型: deepseek-chat
  API:  https://api.deepseek.com/v1
  输入 /clear 清空历史  |  Ctrl+C 退出
==========================================================

[You] > 你好，请介绍一下你自己

[AI]  你好！我是一个 AI 助手，我可以帮助你解答问题、编写代码、
分析数据……  很高兴认识你！

──────────────────────────────────────────────────────────
  ⏱  TTFT: 0.312s  |  生成: 2.145s
  📊  输入: 27 tokens  |  输出: 35 tokens
  🚀  速度: 16.3 tokens/s
  📝  上下文长度: 3 条消息

[You] > /clear
♻️  聊天历史已清空。

[You] > ^C
👋 再见！
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| SSE 流式解析 | HTTP 响应中逐行读取 `data: {...}` 事件 |
| `stream: True` | API 请求中开启流式模式 |
| TTFT | Time To First Token，首个 token 的响应延迟 |
| 上下文窗口 | 将历史 messages 数组完整回传，维持对话记忆 |
| 优雅退出 | `signal` / `KeyboardInterrupt` 关闭 HTTP 连接 |

---

### Practice 02 - 工具调用 (Function Calling)

`practice02/tool_call_demo.py`

实现 OpenAI 兼容的 Function Calling 工具调用能力，支持以下 6 个工具：

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `list_files` | 列出目录文件 | `directory` - 目标目录路径 |
| `read_file` | 读取文件内容 | `directory`, `filename` |
| `create_file` | 创建新文件 | `directory`, `filename`, `content` |
| `rename_file` | 重命名文件 | `directory`, `old_name`, `new_name` |
| `delete_file` | 删除文件 | `directory`, `filename` |
| `curl_url` | 访问网页 | `url`, `method`(可选), `headers`(可选) |

**运行:**
```powershell
python practice02/tool_call_demo.py
```

**工具调用示例:**
```
[You] > 帮我查看一下项目根目录有哪些文件

  🔧 调用工具 [list_files]
     参数: {"directory": "."}
     结果:
目录: C:\Users\WGXY\Documents\trae_projects\XM
共 7 个项目:
  [FILE] rw-rw-rw-         896 B  .gitignore
  ...

[AI]  项目根目录共有7个文件和目录，包括 .gitignore、README.md、practice01 和 practice02 等。
```

**curl_url 使用示例:**
```
[You] > 帮我访问一下 http://httpbin.org/get

  🔧 调用工具 [curl_url]
     参数: {"url": "http://httpbin.org/get"}
     结果:
URL: http://httpbin.org/get
HTTP 状态码: 200
内容类型: application/json
响应长度: 317 字符
--------------------------------------------------------
{
  "args": {}, 
  "headers": {...},
  "origin": "xxx.xxx.xxx.xxx",
  "url": "http://httpbin.org/get"
}

[AI]  成功获取到 httpbin.org 的响应，返回了你的请求信息。
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| Function Calling | 让 LLM 根据用户请求自动选择并调用工具 |
| 工具定义 | JSON Schema 格式描述工具名称、描述、参数 |
| 工具执行循环 | LLM 返回 tool_calls → 执行工具 → 结果回传 → 继续对话 |
| 安全边界 | 文件操作限制在项目目录内，防止路径穿越 |

---

### Practice 03 - 上下文压缩与对话管理

`practice03/chat_with_summary.py`

在 Practice 02 的工具调用基础上，新增**聊天记录自动压缩总结**机制，解决长对话中上下文不断膨胀导致 token 浪费和响应变慢的问题。

**压缩触发条件（满足任一即触发）:**
| 条件 | 阈值 | 说明 |
|------|------|------|
| 对话轮数 | > 5 轮 | 用户发送超过 5 条消息后触发 |
| 上下文长度 | > 3000 字符 | 所有消息文本总长度超过 3000 字符 |

**压缩策略:**
```
原始消息: [sys, u1, a1, u2, a2, u3, a3, u4, a4, u5, a5, u6, a6]
                ← 前 70% 压缩 →         ← 后 30% 保留原文 →

压缩后:   [sys, 摘要消息, u4, a4, u5, a5, u6, a6]
```

- 保留 system 消息不变
- 前 70% 的消息发送给 LLM 做一次性总结，压缩为一条摘要
- 后 30% 的消息保留原文，维持近期对话的上下文连贯性
- 消息数为奇数时自动对齐为偶数，避免切断 user/assistant 对

**运行:**
```powershell
python practice03/chat_with_summary.py
```

**压缩效果对比:**
```
=======================================================
  📚 Practice 03 - 聊天记录压缩总结
  模型: qwen/qwen2.5-vl-7b
  压缩阈值: >5轮 或 >3000字符
  策略: 前70%压缩为摘要 | 后30%保留原文
=======================================================

[You] > 你好

[AI] 你好！有什么可以帮助你的吗？

[You] > ... (多轮对话后)

  🔔 触发历史压缩条件
     当前轮数: 6 (阈值: 5)
     上下文长度: 4521 字符 (阈值: 3000)
     消息总数: 15 条 -> 开始压缩...
  📊 总结消耗: 854 tokens | ⏱ 2.15s
  📝 总结内容: 用户询问了日期、天气和文件操作，AI使用工具获取了当前时间，
     查询了北京天气，并列出了项目目录文件...
  ✅ 压缩完成:
     轮数: 6 -> 4
     长度: 4521 -> 1287 字符
     消息: 15 -> 7 条
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| 上下文窗口管理 | LLM 有 token 上限，长对话需要压缩历史来节省 token |
| 滑动窗口策略 | 前 70% 压缩 + 后 30% 保留，兼顾效率与连贯性 |
| LLM 自总结 | 用 LLM 本身总结对话历史，保持语义信息不丢失 |
| 轮数与长度双阈值 | 双重检测机制，确保在 token 超限前及时压缩 |
| 工具调用兼容 | 从 practice02 继承完整 Function Calling，工具结果也参与压缩 |

> **设计思路**：在实际 AI Agent 应用中，对话会越来越长。如果不压缩，每轮都要把全部历史发给 LLM，token 消耗呈线性增长。通过智能压缩，可以把 O(n) 的增长控制为 O(1)，让 Agent 可以长期运行而不爆 token 上限。


---

### Practice 04 - 聊天日志与 5W 关键信息提取

`practice04/chat_with_log.py`

在 Practice 03 的基础上，新增**5W 关键信息自动提取**和**聊天历史搜索**功能，实现对话的长期记忆与检索。

**功能一：5W 关键信息自动提取与持久化**

| 特性 | 说明 |
|------|------|
| 触发频率 | 每 **5 轮**对话自动提取一次 |
| 提取规则 | 按 **Who / What / When / Where / Why** 五要素提取 |
| 存储位置 | `D:\chat-log\log.txt`（自动创建目录和文件） |
| 更新方式 | 增量追加，不覆盖历史记录 |
| 提取方式 | 调用 LLM 分析对话，结构化输出 |

**5W 提取格式:**
```
[Who:小明] [What:查询了北京天气] [When:2026-05-18] [Where:N/A] [Why:准备出行]
[Who:AI助手] [What:使用get_weather工具获取天气] [When:2026-05-18] [Where:N/A] [Why:N/A]
```

**功能二：聊天历史搜索**

| 触发方式 | 说明 |
|----------|------|
| `/search` 命令 | 用户输入以 `/search` 开头，如 `/search 昨天讨论了什么` |
| 语义触发 | 用户表达"查找聊天历史"、"回顾之前对话"等意图 |
| Function Call | LLM 主动判断需要调用 `search_chat_log` 工具 |

搜索时将 log.txt 内容与用户查询组合，发送给 LLM 获取智能回答。

**运行:**
```powershell
python practice04/chat_with_log.py
```

**运行效果:**
```
=======================================================
  📚 Practice 04 - 聊天日志与5W关键信息提取
  模型: qwen/qwen2.5-vl-7b
  提取频率: 每5轮提取一次5W关键信息
  日志文件: D:\chat-log\log.txt
  搜索功能: /search + 关键词
=======================================================

[You] > 你好，我叫小明，我在北京

[AI] 你好小明！有什么可以帮助你的吗？

[You] > 今天天气怎么样

  🔧 调用工具: get_weather
     参数: {'city': '北京'}
     结果:
     🌤 北京天气
     气温: 22°C (体感 20°C)
     天气: Sunny
     风速: 15km/h | 湿度: 45%

[AI] 小明，今天北京天气晴朗，气温22°C...

... (5轮后)

  🔍 触发5W关键信息提取 (每5轮)...
  📋 提取到 3 条关键信息:
     [Who:小明] [What:在查询北京天气] [When:2026-05-18] [Where:北京] [Why:出行准备]
     [Who:AI助手] [What:调用get_weather获取天气数据] [When:2026-05-18] [Where:N/A] [Why:N/A]
     [Who:小明] [What:询问文件操作相关功能] [When:2026-05-18] [Where:N/A] [Why:N/A]
  💾 已记录 3 条关键信息到 D:\chat-log\log.txt

[You] > /search 小明问了什么

  🔍 搜索聊天历史: 小明问了什么

[AI] 根据聊天历史日志，小明问了以下问题：
     1. 查询了北京天气
     2. 询问了文件操作相关功能
  📊 tokens: 245+89 | ⏱ 1.23s
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| 5W 信息提取 | Who/What/When/Where/Why 是信息分析的基本框架 |
| 对话记忆持久化 | 将关键信息写入磁盘文件，实现跨会话的长期记忆 |
| 增量日志 | 追加写入不覆盖，保留完整时间线 |
| LLM 辅助检索 | 用 LLM 理解日志内容，而非简单关键词匹配 |
| 结构化输出 | 要求 LLM 按固定格式输出，便于后续解析和处理 |

> **设计思路**：在真实 Agent 应用中，用户可能几天后回来继续对话。通过 5W 日志持久化到磁盘 + 搜索功能，Agent 获得了"长期记忆"能力——可以回顾历史对话中的关键信息，而不需要把所有对话都保存在上下文窗口中。


---

## .env 配置说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `LLM_BASE_URL` | API 端点地址 | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API 密钥 | `sk-xxxx` |
| `LLM_MODEL` | 模型名称 | `gpt-3.5-turbo` |
| `LLM_TIMEOUT` | 请求超时(秒) | `60` |
| `LLM_SYSTEM_PROMPT` | 系统提示词 | `你是一个有帮助的AI助手。` |

> 兼容任意 OpenAI 协议的服务商，如 DeepSeek、通义千问、智谱 GLM、本地 Ollama 等。

## 设计理念

- **零第三方依赖**: 全程使用 Python 标准库 (`http.client`, `json`, `os`)，理解底层原理
- **渐进式难度**: 从单次请求到流式多轮对话，逐步深入
- **即学即用**: 每个 practice 目录独立可运行，拷贝即可使用
