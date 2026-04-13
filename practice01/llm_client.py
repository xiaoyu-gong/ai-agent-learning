import os
import sys
import time
import json
import http.client
import ssl
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    import re
    text = re.sub(r'[^\x00-\x7F\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]', '', text)
    return text

def load_env():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    env_path = os.path.join(project_root, '.env')
    env_vars = {}
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        print("Please copy env.example to .env and fill in the required values.")
        sys.exit(1)
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def count_tokens(text):
    return len(text.split())

def call_llm_stream(base_url, api_key, model, messages, timeout=30):
    parsed_url = urlparse(base_url)
    scheme = parsed_url.scheme
    host = parsed_url.hostname
    port = parsed_url.port or (443 if scheme == 'https' else 80)
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model,
        'messages': messages,
        'stream': True
    }
    
    try:
        if scheme == 'https':
            context = ssl.create_default_context()
            conn = http.client.HTTPSConnection(host, port, context=context, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
        
        conn.request('POST', path, body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        if response.status != 200:
            response_body = response.read().decode('utf-8')
            print(f"API Error: {response.status}")
            print(f"Response: {response_body}")
            conn.close()
            return None, None, None, None
        
        full_content = ""
        start_time = time.time()
        
        while True:
            line = response.readline()
            if not line:
                break
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                line = line[6:]
                if line == '[DONE]':
                    break
                try:
                    chunk = json.loads(line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            print(clean_text(content), end='', flush=True)
                            full_content += content
                except json.JSONDecodeError:
                    continue
        
        end_time = time.time()
        conn.close()
        
        elapsed_time = end_time - start_time
        return full_content, count_tokens(str(messages)), count_tokens(full_content), elapsed_time
    
    except Exception as e:
        print(f"\nError calling LLM: {e}")
        return None, None, None, None

def call_llm(base_url, api_key, model, prompt, timeout=30):
    parsed_url = urlparse(base_url)
    scheme = parsed_url.scheme
    host = parsed_url.hostname
    port = parsed_url.port or (443 if scheme == 'https' else 80)
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'stream': False
    }
    
    start_time = time.time()
    
    try:
        if scheme == 'https':
            context = ssl.create_default_context()
            conn = http.client.HTTPSConnection(host, port, context=context, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
        
        conn.request('POST', path, body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        response_body = response.read().decode('utf-8')
        conn.close()
        
        end_time = time.time()
        
        if response.status != 200:
            print(f"API Error: {response.status}")
            print(f"Response: {response_body}")
            return None, None, None, None
        
        result = json.loads(response_body)
        content = result['choices'][0]['message']['content']
        
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', count_tokens(prompt))
        completion_tokens = usage.get('completion_tokens', count_tokens(content))
        total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
        
        elapsed_time = end_time - start_time
        
        return content, prompt_tokens, completion_tokens, elapsed_time
    
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None, None, None, None

def chat_mode(base_url, api_key, model, timeout):
    max_tokens = 4000
    history = []
    
    print("\n=== 对话模式 ===")
    print("直接输入您的问题，按 Enter 发送")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'clear' 清空屏幕")
    print("输入 'history' 查看聊天历史")
    print("输入 'reset' 重置聊天历史")
    print(f"注意：输入文本建议不超过 {max_tokens} tokens")
    print("-" * 50)
    
    while True:
        try:
            prompt = input("\n你: ")
        except KeyboardInterrupt:
            print("\n\n退出对话")
            break
        
        if prompt.lower() in ['exit', 'quit']:
            print("再见！")
            break
        
        if prompt.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        
        if prompt.lower() == 'history':
            print("\n--- 聊天历史 ---")
            for i, msg in enumerate(history):
                role = "你" if msg['role'] == 'user' else "助手"
                print(f"{i+1}. {role}: {msg['content'][:50]}..." if len(msg['content']) > 50 else f"{i+1}. {role}: {msg['content']}")
            print("-" * 50)
            continue
        
        if prompt.lower() == 'reset':
            history = []
            print("聊天历史已重置")
            continue
        
        if not prompt.strip():
            continue
        
        prompt_tokens = count_tokens(prompt)
        if prompt_tokens > max_tokens:
            print(f"警告：输入文本过长 ({prompt_tokens} tokens)，可能超过模型上下文限制")
            choice = input("是否截断文本继续发送？(y/n): ")
            if choice.lower() != 'y':
                print("已取消发送")
                continue
            words = prompt.split()
            prompt = ' '.join(words[:max_tokens])
            print(f"文本已截断，保留前 {max_tokens} tokens")
        
        history.append({'role': 'user', 'content': prompt})
        
        messages = history.copy()
        
        print("\n助手: ", end='', flush=True)
        content, prompt_tokens, completion_tokens, elapsed_time = call_llm_stream(base_url, api_key, model, messages, timeout)
        print()
        
        if content is None:
            history.pop()
            print("助手: 请求失败，请重试")
            continue
        
        history.append({'role': 'assistant', 'content': content})
        
        print("\n--- 统计 ---")
        print(f"输入 Tokens: {prompt_tokens}")
        print(f"输出 Tokens: {completion_tokens}")
        print(f"耗时: {elapsed_time:.2f}秒")
        if elapsed_time > 0:
            print(f"速度: {(prompt_tokens + completion_tokens) / elapsed_time:.2f} tokens/s")
        print("-" * 50)

def main():
    env_vars = load_env()
    
    base_url = env_vars.get('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('OPENAI_API_MODEL', 'gpt-4o-mini')
    api_key = env_vars.get('OPENAI_API_KEY', '')
    timeout = int(env_vars.get('OPENAI_API_TIMEOUT', 30))
    
    if not api_key or api_key == 'your-api-key-here':
        print("Error: Please set OPENAI_API_KEY in your .env file")
        sys.exit(1)
    
    print(f"Using Base URL: {base_url}")
    print(f"Using Model: {model}")
    
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        content, prompt_tokens, completion_tokens, elapsed_time = call_llm(base_url, api_key, model, prompt, timeout)
        
        if content is None:
            print("Failed to get response from LLM")
            sys.exit(1)
        
        print("-" * 50)
        print("\nResponse:")
        print(clean_text(content))
        print("\n" + "-" * 50)
        print("Performance Metrics:")
        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Completion Tokens: {completion_tokens}")
        print(f"Total Tokens: {prompt_tokens + completion_tokens}")
        print(f"Time Elapsed: {elapsed_time:.2f} seconds")
        if elapsed_time > 0:
            print(f"Token/s Speed: {(prompt_tokens + completion_tokens) / elapsed_time:.2f} tokens/s")
    else:
        chat_mode(base_url, api_key, model, timeout)

if __name__ == "__main__":
    main()