import json
import os
import sys
import time
import http.client
import urllib.parse


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


def stream_chat(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    timeout: int = 120,
    temperature: float = 0.3,
    max_tokens: int = 512,
    top_p: float = 0.9,
):
    url = urllib.parse.urlparse(base_url)
    path = url.path.rstrip("/") + "/chat/completions"

    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "n": 1,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "best_of": 1,
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if url.scheme == "https":
        conn = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(url.hostname, url.port or 80, timeout=timeout)

    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    buffer = ""
    first_token_time = None
    start_time = time.perf_counter()

    try:
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()

        if response.status != 200:
            error_body = response.read().decode("utf-8", errors="replace")
            conn.close()
            raise RuntimeError(
                f"API 请求失败 (HTTP {response.status}):\n{error_body[:500]}"
            )

        while True:
            chunk = response.read(4096)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue

                data_str = line[6:]
                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choices = data.get("choices", [])
                usage = data.get("usage")
                if usage:
                    usage_info["prompt_tokens"] = usage.get("prompt_tokens", 0)
                    usage_info["completion_tokens"] = usage.get("completion_tokens", 0)
                    usage_info["total_tokens"] = usage.get("total_tokens", 0)

                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        if first_token_time is None:
                            first_token_time = time.perf_counter()
                        yield content

    except KeyboardInterrupt:
        pass
    finally:
        conn.close()

    end_time = time.perf_counter()
    total_elapsed = end_time - start_time
    ttft = (first_token_time - start_time) if first_token_time else total_elapsed
    gen_time = end_time - first_token_time if first_token_time else 0
    completion_tokens = usage_info["completion_tokens"]
    tps = completion_tokens / gen_time if gen_time > 0 and completion_tokens > 0 else 0

    yield {
        "_stats": {
            "ttft": ttft,
            "total_elapsed": total_elapsed,
            "gen_time": gen_time,
            "prompt_tokens": usage_info["prompt_tokens"],
            "completion_tokens": completion_tokens,
            "total_tokens": usage_info["total_tokens"],
            "tokens_per_second": tps,
        }
    }


def print_banner(config: dict):
    print("=" * 56)
    print("  🤖  流式聊天终端  |  基于 OpenAI 兼容协议")
    print("=" * 56)
    print(f"  模型: {config['LLM_MODEL']}")
    print(f"  API:  {config['LLM_BASE_URL']}")
    print(f"  输入 /clear 清空历史  |  Ctrl+C 退出")
    print("=" * 56)


def main():
    config = load_env()

    base_url = config["LLM_BASE_URL"]
    model = config["LLM_MODEL"]
    api_key = config["LLM_API_KEY"]
    timeout = int(config.get("LLM_TIMEOUT", 120))
    system_prompt = config.get("LLM_SYSTEM_PROMPT", "你是一个直接回答问题的助手，不要解释你的思考过程，直接给出答案。")
    
    temperature = float(config.get("LLM_TEMPERATURE", 0.01))
    max_tokens = int(config.get("LLM_MAX_TOKENS", 256))
    top_p = float(config.get("LLM_TOP_P", 0.5))

    messages = [{"role": "system", "content": system_prompt}]

    print_banner(config)

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

            if user_input.lower() == "/clear":
                messages = [messages[0]]
                print("\n♻️  聊天历史已清空。")
                continue

            messages.append({"role": "user", "content": user_input})

            print(f"\n[AI]  ", end="", flush=True)
            full_response = ""

            stats = None
            for item in stream_chat(base_url, api_key, model, messages, timeout, temperature, max_tokens, top_p):
                if isinstance(item, dict) and "_stats" in item:
                    stats = item["_stats"]
                else:
                    print(item, end="", flush=True)
                    full_response += item

            print()

            messages.append({"role": "assistant", "content": full_response})

            if stats:
                print(f"\n{'─' * 56}")
                print(f"  ⏱  TTFT: {stats['ttft']:.3f}s  |  生成: {stats['gen_time']:.3f}s")
                print(f"  📊  输入: {stats['prompt_tokens']} tokens  |  输出: {stats['completion_tokens']} tokens")
                print(f"  🚀  速度: {stats['tokens_per_second']:.1f} tokens/s")
                print(f"  📝  上下文长度: {len(messages)} 条消息")
            else:
                print(f"\n{'─' * 56}")
                print(f"  ⚠️  未获取到 token 统计 (API 可能不支持 stream_options)")
                print(f"  📝  上下文长度: {len(messages)} 条消息")

    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)


if __name__ == "__main__":
    main()
