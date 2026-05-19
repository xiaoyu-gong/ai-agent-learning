import json
import os
import time
import datetime
import http.client
import urllib.parse


# ============================================================
#  环境变量加载（复用 practice01 的 load_env 逻辑）
# ============================================================

def load_env(env_path: str = ".env") -> dict[str, str]:
    config = {}
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(project_root, env_path)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(
            f"未找到 {env_path} 文件。\n"
            f"请复制 env.example 为 .env 并填写正确的参数:\n"
            f"  cp env.example .env\n"
            f"路径: {full_path}"
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

    required = ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(
            f".env 文件缺少必要配置项: {', '.join(missing)}\n"
            f"请参考 env.example 补全参数。"
        )

    return config


# ============================================================
#  五个文件系统工具函数的实现
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_path(directory: str) -> str:
    if not os.path.isabs(directory):
        directory = os.path.join(BASE_DIR, directory)
    directory = os.path.normpath(directory)
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")
    if not directory.startswith(os.path.normpath(BASE_DIR + os.sep)):
        raise PermissionError(f"禁止访问项目目录以外的路径: {directory}")
    return directory


def _safe_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    if not filename or ".." in filename:
        raise ValueError(f"非法的文件名: {filename}")
    return filename


def list_files(directory: str) -> str:
    try:
        directory = _resolve_path(directory)
    except (FileNotFoundError, PermissionError) as e:
        return f"[错误] {e}"

    try:
        entries = os.listdir(directory)
    except OSError as e:
        return f"[错误] 无法读取目录: {e}"

    if not entries:
        return f"目录 '{directory}' 为空。"

    lines = [f"目录: {directory}", f"共 {len(entries)} 个项目:", "-" * 56]
    for name in sorted(entries):
        full = os.path.join(directory, name)
        try:
            stat = os.stat(full)
            mode = stat.st_mode
            t = "DIR" if os.path.isdir(full) else "FILE"
            size = stat.st_size
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            perm = ""
            for who, r, w, x in [("U", mode & 0o400, mode & 0o200, mode & 0o100),
                                  ("G", mode & 0o040, mode & 0o020, mode & 0o010),
                                  ("O", mode & 0o004, mode & 0o002, mode & 0o001)]:
                perm += "r" if r else "-"
                perm += "w" if w else "-"
                perm += "x" if x else "-"
            lines.append(f"  [{t:>4}] {perm}  {size:>10,} B  {mtime}  {name}")
        except OSError:
            lines.append(f"  [????] ---  {"":>10}        ???  {name}")

    return "\n".join(lines)


def rename_file(directory: str, old_name: str, new_name: str) -> str:
    try:
        directory = _resolve_path(directory)
    except (FileNotFoundError, PermissionError) as e:
        return f"[错误] {e}"

    old_name = _safe_filename(old_name)
    new_name = _safe_filename(new_name)
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)

    if not os.path.exists(old_path):
        return f"[错误] 源文件不存在: {old_path}"
    if os.path.exists(new_path):
        return f"[错误] 目标文件已存在: {new_path}"

    try:
        os.rename(old_path, new_path)
        return f"成功: '{old_name}' → '{new_name}' (目录: {directory})"
    except OSError as e:
        return f"[错误] 重命名失败: {e}"


def delete_file(directory: str, filename: str) -> str:
    try:
        directory = _resolve_path(directory)
    except (FileNotFoundError, PermissionError) as e:
        return f"[错误] {e}"

    filename = _safe_filename(filename)
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        return f"[错误] 文件不存在: {filepath}"
    if os.path.isdir(filepath):
        return f"[错误] '{filename}' 是目录，此工具仅支持删除文件。"

    try:
        os.remove(filepath)
        return f"成功: 已删除 '{filename}' (目录: {directory})"
    except OSError as e:
        return f"[错误] 删除失败: {e}"


def create_file(directory: str, filename: str, content: str) -> str:
    try:
        directory = _resolve_path(directory)
    except (FileNotFoundError, PermissionError) as e:
        return f"[错误] {e}"

    filename = _safe_filename(filename)
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        return f"[错误] 文件已存在: {filepath}"

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        size = os.path.getsize(filepath)
        return f"成功: 已创建 '{filename}' ({size:,} 字节, 目录: {directory})"
    except OSError as e:
        return f"[错误] 创建文件失败: {e}"


def read_file(directory: str, filename: str) -> str:
    try:
        directory = _resolve_path(directory)
    except (FileNotFoundError, PermissionError) as e:
        return f"[错误] {e}"

    filename = _safe_filename(filename)
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        return f"[错误] 文件不存在: {filepath}"
    if os.path.isdir(filepath):
        return f"[错误] '{filename}' 是目录，此工具仅支持读取文件。"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        size = os.path.getsize(filepath)
        header = f"文件: {filepath}  ({size:,} 字节)\n{'─' * 56}\n"
        return header + content
    except (OSError, UnicodeDecodeError) as e:
        return f"[错误] 读取文件失败: {e}"


# ============================================================
#  工具处理分发器
# ============================================================

def curl_url(url: str, method: str = "GET", headers: str = "") -> str:
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.hostname:
            return f"[错误] 无效的URL: {url}"

        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        path = parsed_url.path or "/"
        if parsed_url.query:
            path += "?" + parsed_url.query

        request_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        if headers:
            try:
                header_dict = json.loads(headers)
                for key, value in header_dict.items():
                    request_headers[key] = value
            except json.JSONDecodeError:
                return f"[错误] headers 参数格式错误，应为 JSON 字符串"

        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, port, timeout=30)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=30)

        conn.request(method, path, headers=request_headers)
        response = conn.getresponse()
        
        status = response.status
        content_type = response.getheader("Content-Type", "text/plain")
        body = response.read(1024 * 1024).decode("utf-8", errors="replace")
        
        conn.close()

        if len(body) > 5000:
            body = body[:5000] + "\n\n[内容已截断，完整内容超过5000字符]"

        result = f"URL: {url}\n"
        result += f"HTTP 状态码: {status}\n"
        result += f"内容类型: {content_type}\n"
        result += f"响应长度: {len(body)} 字符\n"
        result += "-" * 56 + "\n"
        result += body

        return result

    except Exception as e:
        return f"[错误] 访问 URL 失败: {str(e)}"


def get_weather(city: str) -> str:
    try:
        import urllib.parse
        
        encoded_city = urllib.parse.quote(city)
        url = f"http://wttr.in/{encoded_city}?format=j1"
        
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or 80
        path = parsed_url.path or "/"
        if parsed_url.query:
            path += "?" + parsed_url.query

        conn = http.client.HTTPConnection(host, port, timeout=30)
        conn.request("GET", path, headers={"Accept": "application/json"})
        response = conn.getresponse()
        
        if response.status != 200:
            return f"[错误] 获取天气失败，HTTP状态码: {response.status}"
        
        body = response.read(1024 * 1024).decode("utf-8", errors="replace")
        conn.close()

        data = json.loads(body)
        
        current_condition = data.get("current_condition", [{}])[0]
        location = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", city)
        
        temp_c = current_condition.get("temp_C", "N/A")
        temp_f = current_condition.get("temp_F", "N/A")
        weather = current_condition.get("weatherDesc", [{}])[0].get("value", "N/A")
        wind = current_condition.get("windspeedKmph", "N/A")
        humidity = current_condition.get("humidity", "N/A")
        feels_like = current_condition.get("FeelsLikeC", "N/A")

        result = f"🌤️ {location} 天气情况\n"
        result += f"气温: {temp_c}°C ({temp_f}°F)\n"
        result += f"体感温度: {feels_like}°C\n"
        result += f"天气: {weather}\n"
        result += f"风速: {wind} km/h\n"
        result += f"湿度: {humidity}%"

        return result

    except Exception as e:
        return f"[错误] 获取天气失败: {str(e)}"


TOOL_MAP = {
    "list_files": list_files,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file": create_file,
    "read_file": read_file,
    "curl_url": curl_url,
    "get_weather": get_weather,
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    fn = TOOL_MAP.get(tool_name)
    if fn is None:
        return f"[错误] 未知工具: {tool_name}"
    try:
        return fn(**arguments)
    except TypeError as e:
        return f"[错误] 工具参数不匹配: {e}"


# ============================================================
#  OpenAI 兼容协议 - 工具调用循环
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录下的所有文件和子目录，包含权限、大小、修改时间等信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要列出文件的目标目录路径，支持相对路径（相对于项目根目录）和绝对路径。"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "将指定目录下的某个文件或目录重命名为新名称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "文件所在的目录路径。"},
                    "old_name": {"type": "string", "description": "当前的文件名称。"},
                    "new_name": {"type": "string", "description": "新的文件名称。"}
                },
                "required": ["directory", "old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除指定目录下的某个文件（不可恢复，不能删除目录）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "文件所在的目录路径。"},
                    "filename": {"type": "string", "description": "要删除的文件名称。"}
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "在指定目录下新建一个文件并写入内容。如果文件已存在则报错。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目标目录路径。"},
                    "filename": {"type": "string", "description": "新文件的名称。"},
                    "content": {"type": "string", "description": "要写入文件的文本内容。"}
                },
                "required": ["directory", "filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定目录下某个文件的内容（文本文件）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "文件所在的目录路径。"},
                    "filename": {"type": "string", "description": "要读取的文件名称。"}
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "curl_url",
            "description": "通过HTTP/HTTPS访问指定URL并返回网页内容，支持GET方法和自定义请求头。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要访问的目标URL地址，必须包含http://或https://前缀。"},
                    "method": {"type": "string", "description": "HTTP请求方法，默认为GET。"},
                    "headers": {"type": "string", "description": "自定义请求头，JSON格式字符串，例如 '{\"Authorization\": \"Bearer token\"}'。"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的实时天气信息，包括气温、天气状况、风速、湿度等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如北京、上海、Guangzhou等，支持中文和英文。"}
                },
                "required": ["city"]
            }
        }
    }
]


def chat_completion_with_tools(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    tools: list[dict],
    timeout: int = 120,
) -> dict:
    url = urllib.parse.urlparse(base_url)
    path = url.path.rstrip("/") + "/chat/completions"

    body = json.dumps({
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False,
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if url.scheme == "https":
        conn = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(url.hostname, url.port or 80, timeout=timeout)

    start_time = time.perf_counter()
    conn.request("POST", path, body=body, headers=headers)
    response = conn.getresponse()
    response_body = response.read().decode("utf-8")
    elapsed = time.perf_counter() - start_time
    conn.close()

    if response.status != 200:
        raise RuntimeError(
            f"API 请求失败 (HTTP {response.status}):\n{response_body[:500]}"
        )

    result = json.loads(response_body)
    usage = result.get("usage", {})
    choice = result.get("choices", [{}])[0]
    message = choice.get("message", {})

    return {
        "role": message.get("role", "assistant"),
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls"),
        "finish_reason": choice.get("finish_reason", ""),
        "model": result.get("model", model),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "elapsed_seconds": elapsed,
    }


def run_tool_call_loop(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    tools: list[dict],
    timeout: int,
    max_iterations: int = 10,
):
    total_prompt = 0
    total_completion = 0
    total_time = 0.0
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        result = chat_completion_with_tools(
            base_url, api_key, model, messages, tools, timeout
        )
        total_prompt += result["prompt_tokens"]
        total_completion += result["completion_tokens"]
        total_time += result["elapsed_seconds"]

        finish_reason = result["finish_reason"]
        tool_calls = result["tool_calls"]
        content = result["content"]

        if tool_calls:
            assistant_msg = {"role": "assistant", "tool_calls": tool_calls}
            if content:
                assistant_msg["content"] = content
            messages.append(assistant_msg)

            for tc in tool_calls:
                fn_info = tc.get("function", {})
                fn_name = fn_info.get("name", "unknown")
                fn_args = json.loads(fn_info.get("arguments", "{}"))
                tc_id = tc.get("id", "unknown")

                print(f"\n  🔧 调用工具 [{fn_name}]")
                print(f"     参数: {json.dumps(fn_args, ensure_ascii=False)}")

                tool_result = execute_tool(fn_name, fn_args)

                print(f"     结果:\n{tool_result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": tool_result,
                })

        elif finish_reason == "stop" and content:
            messages.append({"role": "assistant", "content": content})
            return {
                "final_content": content,
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_time": total_time,
                "iterations": iteration,
            }

        else:
            messages.append({"role": "assistant", "content": content or "(空响应)"})
            return {
                "final_content": content or "(空响应)",
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_time": total_time,
                "iterations": iteration,
            }

    return {
        "final_content": f"已达最大工具调用轮次 ({max_iterations})，对话终止。",
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_time": total_time,
        "iterations": iteration,
    }


# ============================================================
#  主流程
# ============================================================

SYSTEM_PROMPT = (
    "你是一个具备文件系统操作能力的 AI 助手。\n"
    "你可以使用提供的工具函数来操作项目目录下的文件。\n\n"
    "使用指南:\n"
    "- 当用户要求查看目录内容时，使用 list_files 工具。\n"
    "- 当用户要求重命名文件时，使用 rename_file 工具。\n"
    "- 当用户要求删除文件时，使用 delete_file 工具。调用前应确认操作。\n"
    "- 当用户要求创建新文件时，使用 create_file 工具。\n"
    "- 当用户要求查看文件内容时，使用 read_file 工具。\n"
    "- 目录参数可以使用相对路径（如 '.' 代表项目根目录）或绝对路径。\n"
    "- 执行完工具调用后，根据结果向用户汇报。"
)


def main():
    config = load_env()
    base_url = config["LLM_BASE_URL"]
    model = config["LLM_MODEL"]
    api_key = config["LLM_API_KEY"]
    timeout = int(config.get("LLM_TIMEOUT", 120))

    print("=" * 56)
    print("  🛠️  Function Calling 工具调用演示")
    print("=" * 56)
    print(f"  模型: {model}")
    print(f"  API:  {base_url}")
    print(f"  已注册工具: {', '.join(TOOL_MAP.keys())}")
    print("=" * 56)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    turn = 0
    try:
        while True:
            turn += 1
            try:
                user_input = input(f"\n[You] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 再见！")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            print()
            result = run_tool_call_loop(
                base_url, api_key, model, messages, TOOLS, timeout
            )

            print(f"\n[AI]  {result['final_content']}")

            print(f"\n{'─' * 56}")
            print(
                f"  📊  输入: {result['total_prompt_tokens']} tokens  "
                f"|  输出: {result['total_completion_tokens']} tokens"
            )
            print(
                f"  ⏱   耗时: {result['total_time']:.3f}s  "
                f"|  轮次: {result['iterations']}  "
                f"|  上下文: {len(messages)} 条"
            )

    except KeyboardInterrupt:
        print("\n\n👋 再见！")


if __name__ == "__main__":
    main()
