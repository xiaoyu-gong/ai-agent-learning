# AI 智能体开发教学项目

## 项目简介

这是一个基于 Python 的 AI 智能体开发教学项目，旨在学习如何使用 OpenAI 兼容协议与本地大语言模型进行交互。

## 文件结构

```
XM/
├── .env              # 环境变量配置文件
├── env.example       # 环境变量模板
├── .gitignore        # Git 排除文件
├── chat.bat          # 快速启动脚本
├── README.md         # 项目说明文档
├── .venv/            # Python 虚拟环境
└── practice01/
    └── llm_client.py # LLM 客户端脚本
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

**方式 1：双击 chat.bat 文件**

**方式 2：命令行运行**

```bash
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 运行脚本（对话模式）
python practice01/llm_client.py

# 运行脚本（单条命令模式）
python practice01/llm_client.py "你的问题"
```

## llm_client.py 功能说明

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

### 环境变量配置

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

1. 学习如何配置 Python 虚拟环境
2. 掌握 OpenAI 兼容 API 的调用方式
3. 理解流式输出和历史记录的实现
4. 学习 Git 版本控制的基本操作

## 技术栈

- Python 3.11+
- LM Studio（本地 LLM 运行）
- OpenAI API 兼容协议

## 许可证

MIT License