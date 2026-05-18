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


### Practice 04 附加 — AnythingLLM 知识库集成

`practice04/chat_with_anythingllm.py`

在 Practice 03 基础上，新增 **AnythingLLM 本地知识库查询**功能，让 Agent 能够访问用户在 AnythingLLM 中构建的文档仓库，实现 RAG（检索增强生成）。

**核心功能：**

| 特性 | 说明 |
|------|------|
| 查询 API | 通过 `subprocess` + `curl` 调用 AnythingLLM 的 `/api/v1/workspace/{slug}/chat` 接口 |
| 认证方式 | Bearer Token 认证（`ANYTHINGLLM_API_KEY`） |
| 中文编码 | 使用 `ensure_ascii=False` + UTF-8 正确处理中文 |
| 触发方式 | 用户提到「文档仓库」「文件仓库」「仓库」「知识库」时自动触发 |

**配置要求 (.env):**
```
ANYTHINGLLM_API_KEY=your-anythingllm-api-key
ANYTHINGLLM_WORKSPACE_SLUG=your-workspace-slug
```

**运行:**
```powershell
python practice04/chat_with_anythingllm.py
```

**运行效果:**
```
=======================================================
  📚 Practice 04 - AnythingLLM 知识库集成
  模型: qwen/qwen2.5-vl-7b
  AnythingLLM: 已配置 ✅
  工作区: my-workspace
  压缩阈值: >5轮 或 >3000字符
=======================================================

[You] > 我的文档仓库里有什么内容

  🔧 调用工具: anythingllm_query
     参数: {'message': '我的文档仓库里有什么内容', 'mode': 'chat'}
     结果:
     根据你的文档仓库，目前包含以下内容：...

  📚 参考来源:
    • anythingllm.txt
    • project-doc.pdf
```

**API 文档查阅:** 遇到错误可在浏览器打开 `http://localhost:3001/api/docs/` 查看完整 API 文档。

**核心知识点:**
| 概念 | 说明 |
|------|------|
| RAG (检索增强生成) | 从本地知识库检索相关文档后再由 LLM 生成回答 |
| AnythingLLM | 开源的本地知识库/RAG 平台，支持多种文档格式 |
| subprocess + curl | 使用系统原生 HTTP 工具，避免依赖第三方库 |
| 中文编码处理 | `ensure_ascii=False` 保证 JSON 中中文不转义为 `\uXXXX` |
| 外部工具集成 | Agent 通过 Function Calling 打通外部知识库 |


---

### Practice 05 — 综合工具调用与对话管理

`practice05/tool_client.py`

将前四个 Practice 的核心能力整合到一个完整的工具调用客户端中，实现了 8 大工具的统一管理和调用。

**集成的工具:**

| 工具名称 | 功能 | 来源 |
|----------|------|------|
| `list_directory` | 列出目录内容（含属性） | Practice 02 |
| `rename_file` | 重命名文件 | Practice 02 |
| `delete_file` | 删除文件 | Practice 02 |
| `create_file` | 创建文件并写入内容 | Practice 02 |
| `read_file` | 读取文件内容 | Practice 02 |
| `fetch_webpage` | 访问网页获取内容 | Practice 02 |
| `search_chat_history` | 搜索聊天历史日志 | Practice 04 |
| `anythingllm_query` | 访问 AnythingLLM 知识库 | Practice 04 |

**新增特性:**

| 特性 | 说明 |
|------|------|
| 流式输出 | 普通对话使用 `stream_llm` 实现流式输出 |
| 非流式工具调用 | 工具调用使用 `call_llm` 确保 Function Calling 稳定性 |
| 聊天历史压缩 | 每 5 轮或超 3000 字符自动压缩前 70% |
| 5W 关键信息提取 | 每 5 轮自动提取并记录到 log.txt |
| /search 命令 | 直接搜索聊天历史日志 |

**运行:**
```powershell
python practice05/tool_client.py
```

> 此代码来源于老师教学仓库 `https://github.com/atfa/2026-Prompt-Course-Practice`


---

### Practice 06 — Skill 技能系统

`practice06/tool_client.py`

在 Practice 05 基础上，新增 **Skill 技能系统**，实现技能的热加载与动态调用。Agent 可以自动发现、加载并遵照已安装的 Skill 规则执行任务。

**Skill 目录结构:**
```
.agents/
└── skills/
    └── notice/           ← notice 技能（撰写通知）
        └── SKILL.md      ← 包含 YAML front matter + 正文规则
```

**新增工具:**

| 函数 | 功能 |
|------|------|
| `list_available_skills()` | 读取 `.agents/skills/` 下所有 SKILL.md 的 YAML front matter，提取 `name` 和 `description` |
| `load_skill_content(skill_name)` | 加载指定技能 SKILL.md 的正文内容（YAML front matter 之后的部分） |

**工作流程:**
```
用户请求 → list_available_skills (获取技能列表)
         → LLM 判断匹配的技能
         → load_skill_content (加载技能正文)
         → LLM 遵照技能规则执行任务
```

**SKILL.md 格式 (YAML front matter + Markdown 正文):**
```markdown
---
name: notice
description: 撰写、修改、润色通知类公文。
---

# 通知撰写规范
## 核心规则
1. 通知标题不能以"通知"二字开头，必须冠以部门前缀
2. ...
```

**环境变量适配:**
`practice06` 自动将项目的 `.env` 变量名映射为老师代码的变量名：

| 你的 .env | → | 代码使用的变量 |
|-----------|-----|--------------|
| `LLM_BASE_URL` | → | `BASE_URL` |
| `LLM_MODEL` | → | `MODEL` |
| `LLM_API_KEY` | → | `API_KEY` |
| `LLM_TEMPERATURE` | → | `TEMPERATURE` |
| `LLM_MAX_TOKENS` | → | `MAX_TOKENS` |

**测试结果:**

| 场景 | 输入 | 期望 | 结果 |
|------|------|------|------|
| 场景1 | "帮我写五一放假通知"（未说部门） | `XX部通知` 开头 | ✅ |
| 场景2 | "我是销售部，帮我写五一放假通知" | `销售部通知` 开头 | ✅ |

**运行:**
```powershell
python practice06/tool_client.py
```

**核心知识点:**
| 概念 | 说明 |
|------|------|
| YAML Front Matter | Markdown 文件头部的 `---` 元数据区域，用于声明技能属性 |
| Skill 热加载 | 新增技能只需在 `.agents/skills/` 下创建目录 + SKILL.md，无需修改代码 |
| 技能规则注入 | 技能正文通过 tool call 返回结果注入对话上下文，LLM 遵照执行 |
| 变量名映射 | 通过 `load_env` 中的映射表，统一不同代码库的配置名差异 |


---

### Practice 07 — 链式工具调用

`practice07/tool_client.py`

在 Practice 06 基础上，新增 **链式工具调用（Chained Tool Calls）** 功能。LLM 可以根据前一步的工具执行结果，自主决定下一步的调用——前一步的输出成为后一步的输入。

**核心组件:**

| 组件 | 功能 |
|------|------|
| `ChainedCallContext` | 链式调用上下文管理器，记录每一步的调用和结果，存储中间变量 |
| `build_analysis_prompt()` | 构建分析提示词，包含用户请求、已执行步骤历史、决策规则和 JSON 输出格式 |
| `execute_chained_tool_call()` | 链式调用主循环，最多迭代 10 次，支持双格式解析 |

**工作流程:**
```
用户请求 → 构建分析提示词
         → 调用 LLM 决策（JSON 或 tool_calls 格式）
         → 如果任务完成 → 返回答案
         → 如果需要继续 → 执行工具 → 记录到上下文 → 下一轮
         → (最多迭代 10 次)
```

**双格式支持:**

| 格式 | 说明 | 示例 |
|------|------|------|
| JSON 格式 | LLM 在 content 中返回 JSON | `{"done": false, "tool_call": {...}}` 或 `{"done": true, "answer": "..."}` |
| tool_calls 格式 | OpenAI 标准 Function Calling | 自动转换为链式调用格式 |

**使用方式:**
```powershell
# 启动程序
python practice07/tool_client.py

# 链式调用模式
> 你: /chain 读取1.txt和2.txt，把两个数相加写入result.txt

# 普通对话模式（直接输入，不需要/chain前缀）
> 你: 帮我写一份通知
```

**测试结果:**

| 测试 | 请求 | 工具调用链 | 结果 |
|------|------|------------|------|
| 测试1 | 查找 practice06 目录文件并总结 | list_directory → read_file → 总结 | ✅ |
| 测试2 | 读取 1.txt (123) 和 2.txt (456)，相加写入 result.txt | read_file → read_file → create_file | ✅ (123+456=579) |
| 测试3 | 访问网页 → 总结 → 保存 summary.txt | fetch_webpage → create_file → read_file | ✅ |

**核心知识点:**
| 概念 | 说明 |
|------|------|
| 链式调用 | 前一个工具的输出作为后一个工具的输入参数 |
| 上下文管理 | `ChainedCallContext` 记录步骤历史、中间变量、迭代计数 |
| 双格式解析 | 同时支持 JSON content 和 tool_calls 两种 LLM 响应格式 |
| Markdown 代码块提取 | 用正则 `re.search(r'```(?:json)?\s*\n?(.*?)\n?```', ...)` 提取 JSON |
| 防无限循环 | `max_iterations=10` 限制最大迭代次数 |
| 降级解析 | JSON 解析失败时，用正则从文本中提取 `done`/`answer` 字段 |


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
