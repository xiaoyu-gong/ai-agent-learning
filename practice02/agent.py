import os
import sys
import time
import json
import http.client
import ssl
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from practice02.tools import call_function, get_available_functions

sys.stdout.reconfigure(encoding='utf-8')

class AgentMemory:
    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = {}
    
    def add_short_term(self, entry):
        self.short_term_memory.append({
            'timestamp': time.time(),
            'content': entry
        })
        if len(self.short_term_memory) > 100:
            self.short_term_memory = self.short_term_memory[-50:]
    
    def add_long_term(self, key, value):
        self.long_term_memory[key] = {
            'timestamp': time.time(),
            'value': value
        }
    
    def get_short_term_summary(self):
        if len(self.short_term_memory) == 0:
            return "无最近对话历史"
        recent = self.short_term_memory[-5:]
        summary = "最近对话摘要：\n"
        for entry in recent:
            summary += f"- {entry['content'][:50]}...\n"
        return summary
    
    def get_long_term(self, key):
        return self.long_term_memory.get(key, {}).get('value')

class AdvancedAgent:
    def __init__(self, base_url, api_key, model, timeout=30):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.memory = AgentMemory()
        self.functions = get_available_functions()
        self.conversation_history = []
    
    def clean_text(self, text):
        import re
        text = re.sub(r'[^\x00-\x7F\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]', '', text)
        return text
    
    def call_llm(self, messages, functions=None, function_call='auto'):
        parsed_url = urlparse(self.base_url)
        scheme = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port or (443 if scheme == 'https' else 80)
        path = parsed_url.path.rstrip('/') + '/chat/completions'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'stream': False
        }
        
        if functions:
            data['functions'] = functions
            data['function_call'] = function_call
        
        try:
            if scheme == 'https':
                context = ssl.create_default_context()
                conn = http.client.HTTPSConnection(host, port, context=context, timeout=self.timeout)
            else:
                conn = http.client.HTTPConnection(host, port, timeout=self.timeout)
            
            conn.request('POST', path, body=json.dumps(data), headers=headers)
            response = conn.getresponse()
            response_body = response.read().decode('utf-8')
            conn.close()
            
            if response.status != 200:
                print(f"API Error: {response.status}")
                print(f"Response: {response_body}")
                return None, None, None
            
            result = json.loads(response_body)
            choice = result['choices'][0]
            message = choice['message']
            
            content = message.get('content', '')
            function_call = message.get('function_call', None)
            
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            
            return content, function_call, {'prompt_tokens': prompt_tokens, 'completion_tokens': completion_tokens}
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None, None, None
    
    def call_llm_stream(self, messages):
        parsed_url = urlparse(self.base_url)
        scheme = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port or (443 if scheme == 'https' else 80)
        path = parsed_url.path.rstrip('/') + '/chat/completions'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'stream': True
        }
        
        try:
            if scheme == 'https':
                context = ssl.create_default_context()
                conn = http.client.HTTPSConnection(host, port, context=context, timeout=self.timeout)
            else:
                conn = http.client.HTTPConnection(host, port, timeout=self.timeout)
            
            conn.request('POST', path, body=json.dumps(data), headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                response_body = response.read().decode('utf-8')
                print(f"API Error: {response.status}")
                print(f"Response: {response_body}")
                conn.close()
                return None
            
            full_content = ""
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
                                print(self.clean_text(content), end='', flush=True)
                                full_content += content
                    except json.JSONDecodeError:
                        continue
            
            conn.close()
            return full_content
        
        except Exception as e:
            print(f"\nError calling LLM: {e}")
            return None
    
    def execute_tool(self, func_name, func_args):
        print(f"\n🔧 执行工具: {func_name}")
        print(f"参数: {json.dumps(func_args, ensure_ascii=False)}")
        
        result = call_function(func_name, **func_args)
        print(f"\n📊 工具执行结果:\n{result}")
        
        return result
    
    def run(self):
        print("\n=== 🤖 高级 AI Agent ===")
        print("我可以帮您执行文件操作、访问网络和完成各种任务")
        print("可用工具：list_files, rename_file, delete_file, create_file, read_file, curl")
        print("输入 'exit' 或 'quit' 退出")
        print("输入 'clear' 清空屏幕")
        print("输入 'tools' 查看可用工具")
        print("输入 'memory' 查看记忆")
        print("输入 'reset' 重置对话")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n🧑 你: ")
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            
            if user_input.lower() in ['exit', 'quit']:
                print("👋 再见！")
                break
            
            if user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            if user_input.lower() == 'tools':
                print("\n--- 🛠️ 可用工具 ---")
                for func in self.functions:
                    print(f"\n📌 {func['name']}: {func['description']}")
                    print("   参数:")
                    for param, info in func['parameters'].items():
                        print(f"     - {param}: {info['description']}")
                print("-" * 60)
                continue
            
            if user_input.lower() == 'memory':
                print("\n--- 🧠 记忆内容 ---")
                print(self.memory.get_short_term_summary())
                print("-" * 60)
                continue
            
            if user_input.lower() == 'reset':
                self.conversation_history = []
                self.memory = AgentMemory()
                print("🔄 对话已重置")
                continue
            
            if not user_input.strip():
                continue
            
            self.conversation_history.append({'role': 'user', 'content': user_input})
            self.memory.add_short_term(f"用户: {user_input}")
            
            system_prompt = {
                'role': 'system',
                'content': f"""
你是一个高级 AI Agent，具备以下能力：
1. 文件操作：创建、读取、修改、删除文件
2. 网络访问：HTTP/HTTPS 请求获取网页内容
3. 记忆功能：记住对话历史和重要信息

请根据用户需求，决定是否需要调用工具：
- 如果需要获取文件内容、创建文件、删除文件等，请调用相应工具
- 如果需要访问网页内容，请使用 curl 工具
- 如果问题可以直接回答，不需要调用工具

当前时间: {time.ctime()}
最近对话: {self.memory.get_short_term_summary()}

请用中文回答。
"""
            }
            
            messages = [system_prompt] + self.conversation_history
            
            content, function_call, usage = self.call_llm(messages, self.functions)
            
            if content is None:
                print("❌ 请求失败，请重试")
                self.conversation_history.pop()
                continue
            
            if function_call:
                func_name = function_call['name']
                func_args = function_call.get('arguments', {})
                
                if isinstance(func_args, str):
                    try:
                        func_args = json.loads(func_args)
                    except json.JSONDecodeError:
                        print(f"❌ 解析参数失败: {func_args}")
                        self.conversation_history.pop()
                        continue
                
                tool_result = self.execute_tool(func_name, func_args)
                
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': None,
                    'function_call': function_call
                })
                self.conversation_history.append({
                    'role': 'function',
                    'name': func_name,
                    'content': tool_result
                })
                
                self.memory.add_short_term(f"执行工具: {func_name}, 结果: {str(tool_result)[:30]}...")
                
                summary_prompt = {
                    'role': 'system',
                    'content': '请根据工具执行结果，用自然、友好的语言总结给用户。'
                }
                
                summary_messages = [summary_prompt] + self.conversation_history
                
                print("\n🤖 助手: ", end='', flush=True)
                summary_content = self.call_llm_stream(summary_messages)
                print()
                
                if summary_content:
                    self.conversation_history.append({'role': 'assistant', 'content': summary_content})
                    self.memory.add_short_term(f"助手: {summary_content[:30]}...")
            else:
                print(f"\n🤖 助手: {self.clean_text(content)}")
                self.conversation_history.append({'role': 'assistant', 'content': content})
                self.memory.add_short_term(f"助手: {content[:30]}...")
            
            if usage:
                print("\n--- 📊 统计 ---")
                print(f"输入 Tokens: {usage['prompt_tokens']}")
                print(f"输出 Tokens: {usage['completion_tokens']}")
                print("-" * 60)

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

def main():
    env_vars = load_env()
    
    base_url = env_vars.get('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('OPENAI_API_MODEL', 'gpt-4o-mini')
    api_key = env_vars.get('OPENAI_API_KEY', '')
    timeout = int(env_vars.get('OPENAI_API_TIMEOUT', 30))
    
    if not api_key or api_key == 'your-api-key-here':
        print("Error: Please set OPENAI_API_KEY in your .env file")
        sys.exit(1)
    
    print(f"📡 连接到: {base_url}")
    print(f"🧠 使用模型: {model}")
    
    agent = AdvancedAgent(base_url, api_key, model, timeout)
    agent.run()

if __name__ == "__main__":
    main()