import json
import os
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


def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    timeout: int = 60,
) -> dict:
    url = urllib.parse.urlparse(base_url)
    path = url.path.rstrip("/") + "/chat/completions"

    body = json.dumps({
        "model": model,
        "messages": messages,
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
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    content = ""
    choices = result.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")

    return {
        "content": content,
        "model": result.get("model", model),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "elapsed_seconds": elapsed,
        "tokens_per_second": completion_tokens / elapsed if elapsed > 0 else 0,
    }


def main():
    config = load_env()

    base_url = config["LLM_BASE_URL"]
    model = config["LLM_MODEL"]
    api_key = config["LLM_API_KEY"]
    timeout = int(config.get("LLM_TIMEOUT", 60))
    system_prompt = config.get("LLM_SYSTEM_PROMPT", "你是一个有帮助的AI助手。")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "请用一句话介绍一下Python语言。"},
    ]

    print(f"模型: {model}")
    print(f"API:  {base_url}")
    print(f"系统提示词: {system_prompt}")
    print("-" * 50)
    print("正在请求 LLM ...")

    result = chat_completion(base_url, api_key, model, messages, timeout)

    print(f"\n{'='*50}")
    print(f"【模型回复】")
    print(f"{result['content']}")
    print(f"\n{'='*50}")
    print(f"【Token 统计】")
    print(f"  输入 tokens:     {result['prompt_tokens']:>8}")
    print(f"  输出 tokens:     {result['completion_tokens']:>8}")
    print(f"  总计 tokens:     {result['total_tokens']:>8}")
    print(f"\n【性能统计】")
    print(f"  请求耗时:        {result['elapsed_seconds']:>8.3f} 秒")
    print(f"  输出速度:        {result['tokens_per_second']:>8.2f} tokens/s")
    print(f"  模型的自我报告:  {result['model']}")


if __name__ == "__main__":
    main()
