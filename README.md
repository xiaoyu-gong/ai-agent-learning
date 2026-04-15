# AI 智能体开发教学项目

## 项目简介

这是一个基于 Python 的 AI 智能体开发教学项目，旨在学习如何使用 OpenAI 兼容协议与本地大语言模型进行交互，并实现工具调用功能。

## 文件结构

```
XM/
├── .env              # 环境变量配置文件
├── env.example       # 环境变量模板
├── .gitignore        # Git 排除文件
├── chat.bat          # 快速启动脚本
├── README.md         # 项目说明文档
├── .venv/            # Python 虚拟环境
├── practice01/
│   └── llm_client.py # LLM 客户端脚本（基础对话）
└── practice02/
    ├── tools.py      # 工具函数库
    ├── tool_client.py # 工具调用客户端
    └── agent.py      # 高级 AI Agent
```

## 快速开始

### 1. 配置环境

```bash
# 复制环境变量模板
copy env.example .env

# 编辑 .env 文件，填入您的 LLM 配置
```

### 2. 启动 LM Studio

1. 打开 LM Studio
2. 加载模型（如 Gemma 3 4B Instruct）
3. 在 Developer 面板启动本地服务器（默认端口 1234）

### 3. 运行脚本

**方式 1：基础对话模式**

```bash
.venv\Scripts\Activate.ps1
python practice01/llm_client.py
```

**方式 2：工具调用模式**

```bash
.venv\Scripts\Activate.ps1
python practice02/tool_client.py
```

**方式 3：高级 Agent 模式（推荐）**

```bash
.venv\Scripts\Activate.ps1
python practice02/agent.py
```

**方式 4：双击 chat.bat 文件**

## practice01/llm_client.py - 基础对话客户端

### 核心功能

1. **环境变量加载**：自动读取项目根目录的 .env 文件
2. **OpenAI 兼容 API 调用**：使用 Python 标准库 http.client 访问 LLM
3. **流式输出**：支持逐字显示响应
4. **历史记录**：自动维护聊天上下文
5. **性能统计**：显示 Token 消耗、响应时间、处理速度

### 命令说明

| 命令 | 功能 |
|------|------|
| `exit` / `quit` | 退出对话 |
| `clear` | 清空屏幕 |
| `history` | 查看聊天历史 |
| `reset` | 重置聊天历史 |

## practice02/tools.py - 工具函数库

### 可用工具

| 函数名 | 功能说明 | 参数 |
|--------|----------|------|
| `list_files` | 列出目录下的文件和子目录 | `directory`: 目录路径 |
| `rename_file` | 重命名文件或目录 | `old_path`: 原路径, `new_name`: 新名称 |
| `delete_file` | 删除指定文件 | `file_path`: 文件路径 |
| `create_file` | 创建新文件并写入内容 | `directory`: 目录, `filename`: 文件名, `content`: 内容 |
| `read_file` | 读取文件内容 | `file_path`: 文件路径 |
| `curl` | HTTP/HTTPS 请求获取网页内容 | `url`: 网址, `method`: HTTP方法, `headers`: 请求头, `body`: 请求体 |
| `get_weather` | 获取指定城市的天气信息 | `city`: 城市名称 |

### curl 工具说明

curl 工具用于通过 HTTP/HTTPS 请求获取网页内容，支持以下参数：

- **url**（必填）：目标网址，如 `https://www.baidu.com`
- **method**（可选）：HTTP 方法，支持 `GET`（默认）和 `POST`
- **headers**（可选）：请求头，字典格式
- **body**（可选）：请求体，仅 POST 方法时使用

**使用示例：**

```
🧑 你: 请获取百度首页的内容
🤖 助手: 我将调用工具 'curl'...

🔧 执行工具: curl
参数: {"url": "https://www.baidu.com"}

📊 工具执行结果:
<!DOCTYPE html>
<html>
<head>
    <title>百度一下，你就知道</title>
    ...
</html>

🤖 助手: 已成功获取百度首页内容！
```

```
🧑 你: 请访问 https://httpbin.org/get 获取测试数据
🤖 助手: 我将调用工具 'curl'...

🔧 执行工具: curl
参数: {"url": "https://httpbin.org/get"}

📊 工具执行结果:
{
  "args": {},
  "headers": {
    "Accept-Encoding": "identity",
    "Host": "httpbin.org",
    ...
  },
  "origin": "192.168.1.100",
  "url": "https://httpbin.org/get"
}

🤖 助手: 已成功获取测试数据！
```

## practice02/tool_client.py - 工具调用客户端

### 核心功能

1. **自动工具调用**：LLM 自动判断是否需要调用工具
2. **工具执行**：执行文件操作和网络请求
3. **结果总结**：基于工具执行结果进行总结回复
4. **流式输出**：支持逐字显示响应
5. **历史记录**：自动维护聊天上下文

## practice02/agent.py - 高级 AI Agent

### 核心功能

1. **文件操作能力**：创建、读取、修改、删除文件
2. **网络访问能力**：HTTP 请求获取网页内容
3. **记忆系统**：短期记忆和长期记忆
4. **智能工具选择**：自动判断何时调用工具
5. **任务规划**：多步骤任务分解和执行

### 命令说明

| 命令 | 功能 |
|------|------|
| `exit` / `quit` | 退出对话 |
| `clear` | 清空屏幕 |
| `tools` | 查看可用工具列表 |
| `memory` | 查看记忆内容 |
| `reset` | 重置对话和记忆 |

### 使用示例

```
=== 🤖 高级 AI Agent ===
我可以帮您执行文件操作、访问网络和完成各种任务
可用工具：list_files, rename_file, delete_file, create_file, read_file, curl
------------------------------------------------------------

🧑 你: 请帮我创建一个 Python 脚本，计算斐波那契数列

🤖 助手: 我将调用工具 'create_file'...

🔧 执行工具: create_file
参数: {"directory": "C:\\Users\\WGXY\\Documents\\trae_projects\\XM\\practice02", "filename": "fibonacci.py", "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nif __name__ == \"__main__\":\n    for i in range(10):\n        print(f\"F({i}) = {fibonacci(i)}\")"}

📊 工具执行结果:
成功：文件 'C:\Users\WGXY\Documents\trae_projects\XM\practice02\fibonacci.py' 已创建

🤖 助手: 我已经帮您创建了一个斐波那契数列的 Python 脚本。该脚本定义了一个递归函数来计算斐波那契数，并在主程序中打印前10个斐波那契数。

--- 📊 统计 ---
输入 Tokens: 15
输出 Tokens: 42
------------------------------------------------------------
```

## 环境变量配置

```env
OPENAI_API_BASE_URL=http://localhost:1234/v1
OPENAI_API_MODEL=gemma-3-4b-it:2
OPENAI_API_KEY=lm-studio
OPENAI_API_TIMEOUT=60
```

## 手动操作指南

### 安装和配置 Git

1. **下载安装 Git**：从 [git-scm.com](https://git-scm.com/) 下载并安装
2. **配置用户名和邮箱**：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 初始化 Git 仓库

在项目目录中执行：

```bash
git init
git add .
git commit -m "Initial commit"
```

## 教学目标

### practice01 教学目标
1. 学习如何配置 Python 虚拟环境
2. 掌握 OpenAI 兼容 API 的调用方式
3. 理解流式输出的实现原理
4. 实现聊天历史记录功能

### practice02 教学目标
1. 学习开发工具函数
2. 理解 LLM 工具调用机制
3. 实现自动工具选择和执行
4. 学习 curl 网络请求实现
5. 构建完整的 AI Agent 系统

## 技术栈

- Python 3.11+
- LM Studio（本地 LLM 运行）
- OpenAI API 兼容协议
- http.client（Python 标准库）

## 许可证

MIT License