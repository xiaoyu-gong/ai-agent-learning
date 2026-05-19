# XM — AI 智能体开发教学项目

> 基于 Python 标准库的 AI Agent 渐进式实践教程，零第三方依赖，从 HTTP 直连到链式工具调用。

---

## 摘要

本项目针对 **AI Agent 教学资源碎片化、上手门槛高** 的痛点，设计了一套 **7 个渐进式实践模块**（Practice 01–07），通过纯 Python 标准库（`http.client`、`json`、`subprocess`）实现从 LLM API 调用到链式工具调用的完整学习路径。项目包含 **11 个 Python 源文件** 和 **3 个可热加载的 Skill**（通知撰写、学术报告、文章初始化），累计约 3000 行代码。所有模块可独立运行，兼容任意 OpenAI 协议后端（DeepSeek、通义千问、本地 Ollama/LM Studio）。测试表明，链式调用模块在 3 个典型场景（文件搜索、多文件运算、网页处理）中均正确完成多步骤工具调用。

---

## 一、引言

### 1.1 背景与问题

当前 AI Agent 开发教学存在以下痛点：

1. **框架黑箱**：主流教程依赖 LangChain、AutoGPT 等框架，学习者只知调用 API，不理解底层 HTTP 协议、SSE 流式解析、Function Calling 消息循环等核心机制
2. **依赖爆炸**：第三方库的依赖树（上百个包）掩盖了 Agent 本质——"LLM + 工具调用 + 消息管理"三个基本要素
3. **缺乏渐进性**：现存教程要么过于简单（单次 API 调用），要么过于复杂（完整 Agent 框架），缺少从简单到复杂的平滑过渡
4. **配置混乱**：不同服务商的密钥、端点格式各异，缺少统一的 `.env` 管理模式

### 1.2 创新点

| 序号 | 创新点 | 对应痛点 |
|------|--------|---------|
| 1 | **零第三方依赖**：全程使用 `http.client` + `json` 标准库，透明展示 HTTP 请求/响应全过程 | 痛点 1、2 |
| 2 | **7 级渐进式模块**：从单次请求 → 流式 → 工具调用 → 压缩 → 日志 → Skill → 链式调用 | 痛点 3 |
| 3 | **Skill 热加载系统**：新增技能只需在 `.agents/skills/` 下创建目录和 `SKILL.md`，无需修改代码 | 痛点 4 |
| 4 | **双格式链式调用**：同时支持 OpenAI 标准 `tool_calls` 和自定义 JSON 决策两种格式 | 痛点 1 |

### 1.3 技术路线

项目通过 `http.client` 直接构造 OpenAI 兼容协议请求，每个 Practice 在前一个基础上叠加一项新能力，形成以下演进路径：

```
HTTP 请求 → 流式解析 → Function Calling → 上下文压缩 → 5W 日志
          → 外部知识库 (AnythingLLM) → Skill 系统 → 链式工具调用
```

---

## 二、技术选型与依据

### 2.1 为什么用 Python 标准库而非 requests/httpx

| 方案 | 优势 | 劣势 |
|------|------|------|
| `requests` | 简洁的 API | 需额外安装；屏蔽了 HTTP 连接细节 |
| `httpx` | 支持 async | 依赖多；教学场景不需要异步 |
| **`http.client`（本项目）** | Python 内置；裸金属操作，学习者能看清每次请求的 URL、Header、Body | 代码更冗长 |

本项目为教学目的选择 `http.client`，使学习者理解 `POST /v1/chat/completions` 的完整细节——从 URL 解析、SSL 连接、Header 构造到 `data: {...}` SSE 事件解析。

### 2.2 为什么选择 Qwen2.5-VL-7B + LM Studio

- **成本**：本地运行，零 API 费用，适合学生反复实验
- **可用性**：LM Studio 一键启动，无需 GPU 配置或 Docker
- **兼容性**：完全遵循 OpenAI Chat Completions 协议，`/v1/chat/completions` 端点与 OpenAI 兼容
- **功能支持**：支持流式输出 (`stream: True`) 和 Function Calling (`tools` + `tool_choice: "auto"`)

### 2.3 为什么选择 AnythingLLM

AnythingLLM 是开源 RAG 平台，提供完整 REST API（`/api/v1/workspace/{slug}/chat`）。相比直接调用 LLM：
- 自动处理文档切片与向量化
- 提供 `sources` 引文追踪
- 支持多种文档格式（PDF、TXT、HTML）
- 本地部署，数据不出境

---

## 三、项目架构与实现

### 3.1 项目结构

```
XM/
├── .env                     # API 密钥与模型配置（不提交 Git）
├── env.example              # 配置模板
├── .agents/skills/          # Skill 热加载目录
│   ├── notice/SKILL.md      #   通知公文撰写规范
│   ├── academic-report/     #   学术报告撰写规范
│   └── init-article/        #   文章初始化（4 约束规则）
├── practice01/              # L1: HTTP 直连 LLM
│   └── llm_http_demo.py
├── practice02/              # L2: 流式对话 + 工具调用
│   ├── llm_stream_chat.py   #   SSE 流式输出
│   ├── tool_call_demo.py    #   6 工具 Function Calling
│   └── fast_chat.py         #   非流式快速聊天
├── practice03/              # L3: 上下文自动压缩总结
│   └── chat_with_summary.py
├── practice04/              # L4: 5W 日志 + 知识库检索
│   ├── chat_with_log.py     #   5W 关键信息提取
│   └── chat_with_anythingllm.py  #   AnythingLLM RAG 集成
├── practice05/              # L5: 综合工具调用整合
│   └── tool_client.py       #   8 工具 + 流式/非流式双模式
├── practice06/              # L6: Skill 技能系统
│   └── tool_client.py       #   YAML front matter 解析
└── practice07/              # L7: 链式工具调用
    ├── tool_client.py       #   ChainedCallContext + 双格式决策
    └── test_chain.py        #   集成测试脚本
```

### 3.2 各模块功能速览

| 模块 | 核心能力 | 新增工具 | 关键技术点 |
|------|---------|---------|-----------|
| **Practice 01** | 单次 HTTP 请求 | — | `http.client`、`.env` 解析、`usage` token 统计 |
| **Practice 02** | 流式对话 + Function Calling | `list_files`、`read_file`、`create_file`、`rename_file`、`delete_file`、`curl_url` | SSE 事件解析、`stream: True`、TTFT 测量、工具执行循环 |
| **Practice 03** | 上下文自动压缩 | `get_date`、`get_weather` + init_article（含 init-article skill） | 70/30 滑动窗口、双阈值触发、LLM 自总结 |
| **Practice 04** | 长期记忆 + 知识库 | `search_chat_log`、`anythingllm_query` | 5W 框架、`subprocess` + curl、增量日志持久化 |
| **Practice 05** | 全功能整合 | 继承 8 工具 | 流式/非流式双模式、聊天历史压缩、`/search` 命令 |
| **Practice 06** | Skill 系统 | `list_available_skills`、`load_skill_content` | YAML front matter 正则解析、环境变量映射表 |
| **Practice 07** | 链式工具调用 | `ChainedCallContext`、`build_analysis_prompt` | JSON/tool_calls 双格式决策、防无限循环(10次)、`/chain` 命令 |

### 3.3 Skill 系统设计

Skill 通过 YAML front matter + Markdown 正文的形式定义：

```markdown
---
name: academic-report
description: 撰写项目报告、参赛报告、小型学术论文。
---

# 文档结构总览
一、引言  →  二、文献综述  →  三、方法论  →  四、测试验证  →  五、结论
```

**加载流程**：
```
用户请求 → list_available_skills() 扫描 .agents/skills/*/SKILL.md
         → 正则匹配 ^--- ... --- 提取 YAML front matter
         → 返回 [{name, description}, ...] 注入 system prompt
         → LLM 判断匹配 → load_skill_content() 返回正文
         → LLM 遵照技能规范执行
```

### 3.4 链式调用执行流程

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 用户请求     │────▶│ 分析提示词    │────▶│ LLM 决策     │
│              │     │ (用户请求+    │     │ (JSON或      │
│              │     │  步骤历史+    │     │  tool_calls) │
│              │     │  决策规则)    │     │              │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                          done? │
                               ┌────────┬───────┘
                               ▼        ▼
                          ┌────────┐ ┌──────────┐
                          │ 返回    │ │ 执行工具  │────▶ 记录到上下文
                          │ 答案    │ │          │      (ChainedCallContext)
                          └────────┘ └──────────┘            │
                                                ◀───────────┘
                                                  继续下一轮
```

---

## 四、运行与验证

### 4.1 环境配置

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10+ / macOS / Linux |
| Python | 3.13+ |
| LLM 后端 | LM Studio（Qwen2.5-VL-7B）+ AnythingLLM（可选） |
| 协议 | OpenAI Chat Completions API 兼容 |

**配置步骤：**
```powershell
# 1. 复制配置模板
cp env.example .env

# 2. 编辑 .env 填入实际参数
LLM_BASE_URL=http://127.0.0.1:1234/v1   # LM Studio 地址
LLM_MODEL=qwen/qwen2.5-vl-7b
LLM_API_KEY=lm-studio

# 3. 运行任一模块
python practice01/llm_http_demo.py
```

### 4.2 测试结果汇总

#### Practice 03 压缩效果测试

| 指标 | 压缩前 | 压缩后 | 压缩率 |
|------|--------|--------|--------|
| 对话轮数 | 6 | 4 | 33.3% |
| 上下文长度 | 4521 字符 | 1287 字符 | 71.5% |
| 消息条数 | 15 条 | 7 条 | 53.3% |
| 压缩 token 消耗 | — | 854 | — |

#### Practice 06 Skill 触发测试

| 场景 | 输入 | 预期输出 | 结果 |
|------|------|---------|------|
| 无部门通知 | "帮我写五一放假通知" | `XX部通知` 开头 | ✅ |
| 指定部门通知 | "我是销售部，帮我写五一放假通知" | `销售部通知` 开头 | ✅ |
| 技能发现 | — | `list_available_skills` 返回 3 个技能 | ✅ |

#### Practice 07 链式调用测试

| 测试 | 请求 | 工具调用链 | 正确性 |
|------|------|-----------|--------|
| 文件搜索 | 查找 practice06 文件并总结 | `list_directory` → `read_file` → 总结 | ✅ |
| 多文件运算 | 读 1.txt(123) + 2.txt(456) → 写入 result.txt | `read_file` → `read_file` → `create_file` | ✅ 123+456=579 |
| 网页处理 | 访问 nsu.edu.cn 新闻 → 保存 summary.txt | `fetch_webpage` → `create_file` → `read_file` | ✅ |

### 4.3 性能数据

| 指标 | 数值 | 说明 |
|------|------|------|
| Token 生成速度 | 16.3 tokens/s | Qwen2.5-VL-7B + LM Studio @ Ryzen |
| TTFT (首 token 延迟) | 0.31s | 非流式请求，本地模型 |
| 链式调用迭代上限 | 10 次 | 防止 LLM 决策死循环 |
| 上下文压缩阈值 | 5 轮 / 3000 字符 | 双条件触发 |
| 工具总数 (Practice 07) | 10 个 | 含 3 个 Skill 相关工具 |

---

## 五、结论

### 5.1 项目成果

1. **零依赖教学闭环**：通过 7 个渐进式模块，学习者从 HTTP 协议层理解 AI Agent 核心机制，而非停留在框架 API 调用层面。代码总量约 3000 行，每个模块 200–1000 行，符合"最小可学习单元"原则
2. **Skill 热加载系统**：通过 YAML front matter 解析实现技能的热插拔，新增技能无需修改任何 Python 代码。已开发 3 个技能（通知、学术报告、文章初始化），覆盖公文写作、学术写作两大场景
3. **链式调用引擎**：`ChainedCallContext` + 双格式决策解析，使 LLM 能够自主完成多步骤工具调用。在 3 个代表性测试场景中均正确完成，验证了设计的可行性

### 5.2 不足之处

1. **模型依赖本地部署**：当前依赖 LM Studio 运行 Qwen2.5-VL-7B，需要 8GB+ 显存/内存。对于硬件配置较低的学习者，需提供云端 API 的替代方案
2. **链式调用提示词依赖较强**：`build_analysis_prompt` 中的决策规则和 JSON 格式要求对最终效果影响显著，而 Qwen2.5-VL-7B（7B 参数）在 JSON 格式遵循上偶尔出现偏差，导致重复调用同一工具
3. **缺少错误恢复机制**：工具调用失败时，链式引擎会继续尝试而非降级处理。例如 `fetch_webpage` 网络超时后，LLM 缺乏明确的"跳过此步骤并继续"指令
4. **测试覆盖不足**：链式调用的 3 个测试场景均为"快乐路径"，未覆盖异常场景（文件不存在、URL 404、LLM 返回非法 JSON 等）

### 5.3 未来方向

1. **集成更强模型**：接入 DeepSeek-V3、Qwen3 等云端 API，在链式调用的 JSON 决策质量上预期有明显提升
2. **增加异常处理链路**：在 `execute_chained_tool_call` 中引入"失败回退"机制——工具连续失败 2 次时自动跳过该步骤，转入降级处理
3. **Skill 在线市场**：将 `.agents/skills/` 设计为类似 npm 的包管理机制，支持从远端仓库拉取 Skill，拓展技能生态
4. **Web 可视化界面**：为链式调用开发浏览器端的步骤可视化面板，实时展示当前迭代、工具调用链、中间结果，降低调试难度
5. **增加 MCP (Model Context Protocol) 支持**：将工具扩展为标准的 MCP Server 模式，使本项目的 Agent 可以调用外部 MCP 工具集

---

## 附录

### 快速开始

```powershell
git clone https://github.com/xiaoyu-gong/ai-agent-learning.git
cd ai-agent-learning
cp env.example .env
# 编辑 .env 填入 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL
python practice01/llm_http_demo.py
```

### .env 配置说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `LLM_BASE_URL` | OpenAI 兼容 API 端点 | `http://127.0.0.1:1234/v1` |
| `LLM_API_KEY` | API 密钥 | `lm-studio` |
| `LLM_MODEL` | 模型名称 | `qwen/qwen2.5-vl-7b` |
| `LLM_TIMEOUT` | 请求超时(秒) | `120` |
| `LLM_TEMPERATURE` | 生成温度 (0-2) | `0.3` |
| `LLM_MAX_TOKENS` | 最大输出 token 数 | `1024` |
| `ANYTHINGLLM_API_KEY` | AnythingLLM 密钥（可选） | `xxx` |
| `ANYTHINGLLM_WORKSPACE_SLUG` | AnythingLLM 工作区（可选） | `my-workspace` |

### 设计理念

- **零第三方依赖**：全程使用 Python 标准库（`http.client`, `json`, `os`, `subprocess`），理解底层原理
- **渐进式难度**：从单次请求到流式多轮对话，逐步深入
- **即学即用**：每个 practice 目录独立可运行
