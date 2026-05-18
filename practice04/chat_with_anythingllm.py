import json
import os
import time
import datetime
import http.client
import urllib.parse
import subprocess


def load_env(env_path: str = ".env") -> dict[str, str]:
    config = {}
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(project_root, env_path)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(
            f"未找到 {env_path} 文件。\n"
            f"请复制 env.example 为 .env 并填写正确的参数。"
        )

    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value

    return config


def _request(base_url, api_key, model, messages, tools, temperature, max_tokens, timeout):
    url = urllib.parse.urlparse(base_url)
    path = url.path.rstrip("/") + "/chat/completions"

    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 0.9,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if url.scheme == "https":
        conn = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(url.hostname, url.port or 80, timeout=timeout)

    start_time = time.perf_counter()
    conn.request("POST", path, body=json.dumps(body), headers=headers)
    response = conn.getresponse()
    response_body = response.read().decode("utf-8")
    elapsed = time.perf_counter() - start_time
    conn.close()

    if response.status != 200:
        raise RuntimeError(f"API 请求失败 (HTTP {response.status}): {response_body[:200]}")

    result = json.loads(response_body)
    choice = result.get("choices", [{}])[0]
    message = choice.get("message", {})
    usage = result.get("usage", {})

    return {
        "role": message.get("role", "assistant"),
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls"),
        "finish_reason": choice.get("finish_reason", ""),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "elapsed_seconds": elapsed,
    }


def get_date() -> str:
    now = datetime.datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    wd = weekdays[now.weekday()]
    return f"当前日期时间: {now.strftime('%Y年%m月%d日')} {wd} {now.strftime('%H:%M:%S')}"


def curl_url(url: str, method: str = "GET", headers: str = "") -> str:
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.hostname:
            return f"[错误] 无效URL: {url}"

        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        path = parsed_url.path or "/"
        if parsed_url.query:
            path += "?" + parsed_url.query

        request_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        if headers:
            try:
                for k, v in json.loads(headers).items():
                    request_headers[k] = v
            except json.JSONDecodeError:
                return f"[错误] headers 格式错误，应为 JSON"

        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, port, timeout=30)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=30)

        conn.request(method, path, headers=request_headers)
        response = conn.getresponse()
        body = response.read(1024 * 1024).decode("utf-8", errors="replace")
        conn.close()

        if len(body) > 3000:
            body = body[:3000] + "\n...[已截断]"

        return f"URL: {url}\nHTTP {response.status}\n内容:\n{body}"
    except Exception as e:
        return f"[错误] 访问失败: {str(e)}"


def get_weather(city: str) -> str:
    try:
        encoded = urllib.parse.quote(city)
        url = f"http://wttr.in/{encoded}?format=j1"
        parsed = urllib.parse.urlparse(url)
        conn = http.client.HTTPConnection(parsed.hostname, 80, timeout=30)
        conn.request("GET", parsed.path + "?" + parsed.query)
        response = conn.getresponse()
        body = response.read(1024 * 1024).decode("utf-8", errors="replace")
        conn.close()

        if response.status != 200:
            return f"[错误] 天气查询失败 HTTP {response.status}"

        data = json.loads(body)
        cc = data.get("current_condition", [{}])[0]
        loc = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", city)

        result = f"🌤 {loc}天气\n"
        result += f"气温: {cc.get('temp_C','?')}°C (体感 {cc.get('FeelsLikeC','?')}°C)\n"
        result += f"天气: {cc.get('weatherDesc',[{}])[0].get('value','?')}\n"
        result += f"风速: {cc.get('windspeedKmph','?')}km/h | 湿度: {cc.get('humidity','?')}%"
        return result
    except Exception as e:
        return f"[错误] 天气获取失败: {str(e)}"


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_path(directory: str) -> str:
    if not os.path.isabs(directory):
        directory = os.path.join(BASE_DIR, directory)
    directory = os.path.normpath(directory)
    if not directory.startswith(os.path.normpath(BASE_DIR + os.sep)):
        raise PermissionError(f"禁止访问项目外的路径")
    return directory


def list_files(directory: str) -> str:
    directory = _resolve_path(directory)
    entries = os.listdir(directory)
    if not entries:
        return f"目录为空: {directory}"
    lines = [f"目录: {directory} ({len(entries)}项)"]
    for name in sorted(entries):
        full = os.path.join(directory, name)
        stat = os.stat(full)
        t = "DIR" if os.path.isdir(full) else "FILE"
        size = stat.st_size
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  [{t}] {name:40s} {size:>10,}B  {mtime}")
    return "\n".join(lines)


def read_file(directory: str, filename: str) -> str:
    directory = _resolve_path(directory)
    filepath = os.path.join(directory, os.path.basename(filename))
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return f"文件: {filepath} ({os.path.getsize(filepath):,}B)\n{content[:5000]}"


def create_file(directory: str, filename: str, content: str) -> str:
    directory = _resolve_path(directory)
    filepath = os.path.join(directory, os.path.basename(filename))
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"文件创建成功: {filepath} ({len(content)}字符)"


def rename_file(directory: str, old_name: str, new_name: str) -> str:
    directory = _resolve_path(directory)
    old_path = os.path.join(directory, os.path.basename(old_name))
    new_path = os.path.join(directory, os.path.basename(new_name))
    os.rename(old_path, new_path)
    return f"重命名成功: {old_name} -> {new_name}"


def delete_file(directory: str, filename: str) -> str:
    directory = _resolve_path(directory)
    filepath = os.path.join(directory, os.path.basename(filename))
    if os.path.isdir(filepath):
        return f"[错误] 只能删除文件，不能删除目录"
    os.remove(filepath)
    return f"删除成功: {filename}"


SKILLS_DIR = os.path.join(BASE_DIR, "skills")


def init_article(topic: str, document_type: str = "软件工程报告") -> str:
    try:
        skill_path = os.path.join(SKILLS_DIR, "init-article")
        if not os.path.exists(skill_path):
            return f"[错误] 未找到 init-article skill，请先安装"

        assets_path = os.path.join(skill_path, "assets")
        if not os.path.exists(assets_path):
            return f"[错误] skill 目录结构不完整"

        output_dir = os.path.join(BASE_DIR, "article-output")
        os.makedirs(output_dir, exist_ok=True)

        templates = {
            "topic.md": "topic-example.md",
            "voice.md": "voice-example.md",
            "structure.md": "structure-example.md",
            "check.md": "check-example.md",
        }

        created_files = []
        for output_name, template_name in templates.items():
            template_path = os.path.join(assets_path, template_name)
            output_path = os.path.join(output_dir, output_name)

            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace("[在此填入文档的核心命题，一句话概括]", topic)
            content = content.replace("[描述预期读者画像，影响内容深度与术语使用]", 
                                   f"文档类型: {document_type}")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            created_files.append(output_name)

        return f"✅ 文章初始化完成！\n\n创建的约束规则文件:\n\n" + "\n".join([f"  • {f}" for f in created_files]) + f"\n\n输出目录: {output_dir}\n\n📝 四个约束规则文件已创建:\n  1. topic.md - 主题锚定（写什么，防止跑题）\n  2. voice.md - 语气风格（怎么写，设定语气）\n  3. structure.md - 文档结构（写成什么样）\n  4. check.md - 质量检查（写完后查什么）"

    except Exception as e:
        return f"[错误] 初始化失败: {str(e)}"


def anythingllm_query(message: str, mode: str = "chat") -> str:
    api_key = os.environ.get("ANYTHINGLLM_API_KEY", "")
    workspace_slug = os.environ.get("ANYTHINGLLM_WORKSPACE_SLUG", "")
    if not api_key or not workspace_slug:
        return (
            "[错误] 未配置 AnythingLLM。请检查 .env 文件中的:\n"
            f"  ANYTHINGLLM_API_KEY={'已设置' if api_key else '未设置'}\n"
            f"  ANYTHINGLLM_WORKSPACE_SLUG={'已设置' if workspace_slug else '未设置'}\n"
            "  详细错误信息可查阅 http://localhost:3001/api/docs/"
        )

    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    body = json.dumps({
        "message": message,
        "mode": mode,
    }, ensure_ascii=False)

    try:
        result = subprocess.run(
            [
                "curl.exe", "-s",
                "-X", "POST",
                url,
                "-H", "Content-Type: application/json; charset=utf-8",
                "-H", f"Authorization: Bearer {api_key}",
                "-d", body,
                "--connect-timeout", "30",
                "--max-time", "120",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                return f"[错误] curl 命令执行失败: {stderr}\n请查阅文档: http://localhost:3001/api/docs/"
            return f"[错误] curl 命令返回码: {result.returncode}\n请查阅文档: http://localhost:3001/api/docs/"

        stdout = result.stdout.strip()
        if not stdout:
            return "[错误] AnythingLLM 返回空响应\n请查阅文档: http://localhost:3001/api/docs/"

        data = json.loads(stdout)

        error = data.get("error")
        if error and isinstance(error, str):
            return f"[错误] AnythingLLM: {error}"

        text_response = data.get("textResponse", "")
        sources = data.get("sources", [])

        if not text_response:
            return f"[错误] AnythingLLM 无返回内容。原始响应: {stdout[:500]}"

        result_text = text_response
        if sources:
            result_text += "\n\n📚 参考来源:"
            for src in sources[:5]:
                title = src.get("title", "Unknown")
                result_text += f"\n  • {title}"

        return result_text

    except subprocess.TimeoutExpired:
        return "[错误] 请求超时 (120s)\n请查阅文档: http://localhost:3001/api/docs/"
    except json.JSONDecodeError as e:
        return f"[错误] 响应解析失败: {e}\n原始响应: {result.stdout[:500] if result.stdout else '(空)'}\n请查阅文档: http://localhost:3001/api/docs/"
    except Exception as e:
        return f"[错误] AnythingLLM 查询失败: {e}\n请查阅文档: http://localhost:3001/api/docs/"


TOOL_FUNCTIONS = {
    "get_date": get_date,
    "curl_url": curl_url,
    "get_weather": get_weather,
    "list_files": list_files,
    "read_file": read_file,
    "create_file": create_file,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "init_article": init_article,
    "anythingllm_query": anythingllm_query,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "获取当前日期和时间。当用户询问「今天日期」「现在几点」「今天几号」「星期几」时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的实时天气信息，包括气温、天气状况、风速、湿度等。参数为城市名称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如北京、上海、Guangzhou"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "curl_url",
            "description": "访问指定的URL网页地址，获取网页内容。用于查询新闻、事实等实时信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标URL，如 http://example.com"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录中的文件和子目录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径，如 '.' 代表当前目录"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径"},
                    "filename": {"type": "string", "description": "文件名"}
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "在指定目录创建新文件并写入内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径"},
                    "filename": {"type": "string", "description": "新文件名"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["directory", "filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "重命名指定目录中的文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径"},
                    "old_name": {"type": "string", "description": "旧文件名"},
                    "new_name": {"type": "string", "description": "新文件名"}
                },
                "required": ["directory", "old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除指定目录中的文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径"},
                    "filename": {"type": "string", "description": "要删除的文件名"}
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "init_article",
            "description": "初始化文章写作，根据用户需求创建四个约束规则文件：topic.md（写什么）、voice.md（怎么写）、structure.md（写成什么样）、check.md（写完后查什么）。用于帮助用户规范文档写作流程。",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "文章主题，一句话概括"},
                    "document_type": {"type": "string", "description": "文档类型，如：软件工程报告、读书心得、入党申请书等"}
                },
                "required": ["topic"],
                "optional": ["document_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anythingllm_query",
            "description": "查询AnythingLLM本地知识库/文档仓库。当用户提到「文档仓库」「文件仓库」「仓库」「知识库」「我的文档」「资料库」或需要从个人文档中查找信息时，使用此工具查询AnythingLLM。",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "查询问题，如'总结仓库中的文档内容'"},
                    "mode": {"type": "string", "description": "查询模式：chat(默认，使用LLM+向量检索)、query(仅向量检索)"}
                },
                "required": ["message"],
                "optional": ["mode"]
            }
        }
    },
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    fn = TOOL_FUNCTIONS.get(tool_name)
    if fn is None:
        return f"[错误] 未知工具: {tool_name}"
    try:
        return fn(**arguments)
    except Exception as e:
        return f"[错误] 工具执行失败: {str(e)}"


ROUND_THRESHOLD = 5
LENGTH_THRESHOLD = 3000


def count_rounds(messages: list[dict]) -> int:
    rounds = 0
    for msg in messages:
        if msg.get("role") == "user":
            rounds += 1
    return rounds


def estimate_length(messages: list[dict]) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if content:
            total += len(content)
        tool_calls = msg.get("tool_calls")
        if tool_calls:
            total += len(json.dumps(tool_calls, ensure_ascii=False))
    return total


def summarize_history(config: dict, messages: list[dict]) -> list[dict]:
    system_msg = messages[0]
    conversation = [m for m in messages if m.get("role") != "system"]

    if len(conversation) < 4:
        return messages

    split_idx = int(len(conversation) * 0.7)
    if split_idx % 2 != 0:
        split_idx += 1

    to_summarize = conversation[:split_idx]
    to_keep = conversation[split_idx:]

    if len(to_summarize) < 2 or len(to_keep) < 2:
        return messages

    summary_prompt = [
        {
            "role": "system",
            "content": (
                "你是一个对话总结助手。请用简洁的要点形式总结以下对话的核心内容，包括:\n"
                "1. 用户问了哪些关键问题\n"
                "2. AI做了哪些操作或工具调用\n"
                "3. 得出了什么关键结论\n"
                "字数控制在200字以内。"
            )
        }
    ]
    summary_prompt.extend(to_summarize)
    summary_prompt.append({"role": "user", "content": "请总结以上对话的核心内容。"})

    base_url = config.get("LLM_BASE_URL")
    api_key = config.get("LLM_API_KEY", "lm-studio")
    model = config.get("LLM_MODEL")
    timeout = int(config.get("LLM_TIMEOUT", 120))
    temperature = float(config.get("LLM_TEMPERATURE", 0.3))
    max_tokens = int(config.get("LLM_MAX_TOKENS", 1024))

    try:
        result = _request(base_url, api_key, model, summary_prompt, tools=None,
                         temperature=temperature, max_tokens=max_tokens, timeout=timeout)
        summary = result.get("content", "").strip()

        if summary:
            total = result.get("total_tokens", 0)
            print(f"  📊 总结消耗: {total} tokens | ⏱ {result['elapsed_seconds']:.2f}s")
            print(f"  📝 总结内容: {summary}")

            new_messages = [system_msg]
            new_messages.append({
                "role": "assistant",
                "content": f"[对话历史总结]\n{summary}"
            })
            new_messages.extend(to_keep)
            return new_messages
    except Exception as e:
        print(f"  ⚠️ 总结失败，保留原文: {e}")

    return messages


def check_and_summarize(config: dict, messages: list[dict]) -> list[dict]:
    rounds = count_rounds(messages)
    length = estimate_length(messages)

    if rounds > ROUND_THRESHOLD or length > LENGTH_THRESHOLD:
        print(f"\n  🔔 触发历史压缩条件")
        print(f"     当前轮数: {rounds} (阈值: {ROUND_THRESHOLD})")
        print(f"     上下文长度: {length} 字符 (阈值: {LENGTH_THRESHOLD})")
        print(f"     消息总数: {len(messages)} 条 -> 开始压缩...")

        before_rounds = rounds
        before_length = length
        before_count = len(messages)

        messages = summarize_history(config, messages)

        after_rounds = count_rounds(messages)
        after_length = estimate_length(messages)
        after_count = len(messages)

        print(f"  ✅ 压缩完成:")
        print(f"     轮数: {before_rounds} -> {after_rounds}")
        print(f"     长度: {before_length} -> {after_length} 字符")
        print(f"     消息: {before_count} -> {after_count} 条")

    return messages


def main():
    config = load_env()

    base_url = config.get("LLM_BASE_URL", "http://localhost:1234/v1")
    model = config.get("LLM_MODEL", "qwen/qwen2.5-vl-7b")
    api_key = config.get("LLM_API_KEY", "lm-studio")
    temperature = float(config.get("LLM_TEMPERATURE", 0.3))
    max_tokens = int(config.get("LLM_MAX_TOKENS", 1024))
    timeout = int(config.get("LLM_TIMEOUT", 120))

    anythingllm_api_key = config.get("ANYTHINGLLM_API_KEY", "")
    anythingllm_workspace = config.get("ANYTHINGLLM_WORKSPACE_SLUG", "")
    os.environ["ANYTHINGLLM_API_KEY"] = anythingllm_api_key
    os.environ["ANYTHINGLLM_WORKSPACE_SLUG"] = anythingllm_workspace

    system_prompt = (
        "你是一个具备工具调用能力的AI助手。\n"
        "请根据用户的问题，决定是否需要调用工具：\n"
        "- 如果用户询问日期、时间 → 调用 get_date\n"
        "- 如果用户询问天气 → 调用 get_weather\n"
        "- 如果用户需要搜索网络信息 → 调用 curl_url\n"
        "- 如果用户需要操作文件 → 调用 list_files/read_file/create_file/rename_file/delete_file\n"
        "- 如果用户提到「文档仓库」「文件仓库」「仓库」「知识库」「我的文档」或需要查找本地知识库中的信息 → 调用 anythingllm_query\n"
        "- 如果问题不需要工具，可以直接回答"
    )

    messages = [{"role": "system", "content": system_prompt}]

    print("=" * 55)
    print("  📚 Practice 04 - AnythingLLM 知识库集成")
    print(f"  模型: {model}")
    print(f"  AnythingLLM: {'已配置 ✅' if anythingllm_api_key else '未配置 ⚠️'}")
    if anythingllm_api_key:
        print(f"  工作区: {anythingllm_workspace}")
    print(f"  压缩阈值: >{ROUND_THRESHOLD}轮 或 >{LENGTH_THRESHOLD}字符")
    print("=" * 55)

    try:
        while True:
            user_input = input("\n[You] > ").strip()
            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("👋 再见！")
                break

            messages.append({"role": "user", "content": user_input})

            messages = check_and_summarize(config, messages)

            total_prompt = 0
            total_completion = 0
            total_time = 0.0

            for _ in range(5):
                result = _request(base_url, api_key, model, messages, TOOLS, temperature, max_tokens, timeout)
                total_prompt += result["prompt_tokens"]
                total_completion += result["completion_tokens"]
                total_time += result["elapsed_seconds"]

                content = result.get("content")
                tool_calls = result.get("tool_calls")

                if tool_calls:
                    if content:
                        print(f"\n[AI] {content}")

                    tool_results = []
                    for tc in tool_calls:
                        fn_name = tc.get("function", {}).get("name", "?")
                        fn_args = json.loads(tc.get("function", {}).get("arguments", "{}"))
                        tc_id = tc.get("id", "?")

                        print(f"\n  🔧 调用工具: {fn_name}")
                        print(f"     参数: {fn_args}")
                        tool_result = execute_tool(fn_name, fn_args)
                        print(f"     结果:\n{tool_result}")

                        tool_results.append({
                            "tool_call_id": tc_id,
                            "content": tool_result
                        })

                    messages.append({
                        "role": "assistant",
                        "content": content or "",
                        "tool_calls": tool_calls
                    })

                    for tr in tool_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tr["tool_call_id"],
                            "content": tr["content"]
                        })

                    continue

                print(f"\n[AI] {content or '(空)'}")
                messages.append({"role": "assistant", "content": content or ""})
                break

            print(f"\n  📊 tokens: {total_prompt}+{total_completion} | ⏱ {total_time:.2f}s")

    except KeyboardInterrupt:
        print("\n\n👋 再见！")


if __name__ == "__main__":
    main()
