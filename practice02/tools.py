import os
import sys
import time
from urllib.parse import urlparse
import http.client
import ssl

def list_files(directory):
    try:
        if not os.path.exists(directory):
            return f"错误：目录 '{directory}' 不存在"
        
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            is_dir = os.path.isdir(item_path)
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else "文件夹"
            mtime = time.ctime(os.path.getmtime(item_path))
            
            files.append({
                'name': item,
                'type': '目录' if is_dir else '文件',
                'size': size,
                'modified': mtime
            })
        
        result = f"目录 '{directory}' 下的文件列表：\n"
        result += "=" * 60 + "\n"
        result += f"{'名称':<30} {'类型':<8} {'大小/状态':<15} {'修改时间'}\n"
        result += "-" * 60 + "\n"
        
        for f in files:
            result += f"{f['name']:<30} {f['type']:<8} {str(f['size']):<15} {f['modified']}\n"
        
        return result
    
    except Exception as e:
        return f"错误：{str(e)}"

def rename_file(old_path, new_name):
    try:
        if not os.path.exists(old_path):
            return f"错误：文件或目录 '{old_path}' 不存在"
        
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)
        
        if os.path.exists(new_path):
            return f"错误：目标文件 '{new_path}' 已存在"
        
        os.rename(old_path, new_path)
        return f"成功：'{old_path}' 已重命名为 '{new_path}'"
    
    except Exception as e:
        return f"错误：{str(e)}"

def delete_file(file_path):
    try:
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        if os.path.isdir(file_path):
            return f"错误：'{file_path}' 是目录，请使用其他方式删除"
        
        os.remove(file_path)
        return f"成功：文件 '{file_path}' 已删除"
    
    except Exception as e:
        return f"错误：{str(e)}"

def create_file(directory, filename, content=""):
    try:
        if not os.path.exists(directory):
            return f"错误：目录 '{directory}' 不存在"
        
        file_path = os.path.join(directory, filename)
        
        if os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 已存在"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功：文件 '{file_path}' 已创建"
    
    except Exception as e:
        return f"错误：{str(e)}"

def read_file(file_path):
    try:
        if not os.path.exists(file_path):
            return f"错误：文件 '{file_path}' 不存在"
        
        if os.path.isdir(file_path):
            return f"错误：'{file_path}' 是目录，无法读取"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 2000:
            content = content[:2000] + "\n\n（内容过长，已截断）"
        
        return content
    
    except Exception as e:
        return f"错误：{str(e)}"

def curl(url, method="GET", headers=None, body=None, timeout=30):
    try:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port or (443 if scheme == 'https' else 80)
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
        
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        if headers:
            default_headers.update(headers)
        
        if scheme == 'https':
            context = ssl.create_default_context()
            conn = http.client.HTTPSConnection(host, port, context=context, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
        
        conn.request(method, path, body=body, headers=default_headers)
        response = conn.getresponse()
        content = response.read().decode('utf-8', errors='ignore')
        conn.close()
        
        if response.status >= 400:
            return f"HTTP错误 {response.status}: {content[:500]}"
        
        if len(content) > 3000:
            content = content[:3000] + "\n\n（内容过长，已截断）"
        
        return content
    
    except Exception as e:
        return f"错误：{str(e)}"

def get_available_functions():
    functions = [
        {
            "name": "list_files",
            "description": "列出指定目录下的所有文件和子目录，包含文件名、类型、大小、修改时间等信息",
            "parameters": {
                "directory": {"type": "string", "description": "要列出的目录路径"}
            }
        },
        {
            "name": "rename_file",
            "description": "重命名指定路径的文件或目录",
            "parameters": {
                "old_path": {"type": "string", "description": "原文件或目录的完整路径"},
                "new_name": {"type": "string", "description": "新的文件名（不含路径）"}
            }
        },
        {
            "name": "delete_file",
            "description": "删除指定的文件",
            "parameters": {
                "file_path": {"type": "string", "description": "要删除的文件完整路径"}
            }
        },
        {
            "name": "create_file",
            "description": "在指定目录下创建新文件并写入内容",
            "parameters": {
                "directory": {"type": "string", "description": "目标目录路径"},
                "filename": {"type": "string", "description": "新文件名"},
                "content": {"type": "string", "description": "文件内容（可选）"}
            }
        },
        {
            "name": "read_file",
            "description": "读取指定文件的内容",
            "parameters": {
                "file_path": {"type": "string", "description": "要读取的文件完整路径"}
            }
        },
        {
            "name": "curl",
            "description": "通过HTTP/HTTPS请求获取网页内容",
            "parameters": {
                "url": {"type": "string", "description": "目标网址"},
                "method": {"type": "string", "description": "HTTP方法（GET/POST，默认为GET）"},
                "headers": {"type": "object", "description": "请求头（可选）"},
                "body": {"type": "string", "description": "请求体（仅POST时使用，可选）"}
            }
        },
        {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "city": {"type": "string", "description": "城市名称（如：北京、上海、广州）"}
            }
        }
    ]
    return functions

def get_weather(city, api_key="demo"):
    try:
        import urllib.parse
        
        encoded_city = urllib.parse.quote(city)
        
        if api_key == "demo" or not api_key:
            mock_data = {
                "北京": {"temp": "25°C", "description": "晴朗", "humidity": "45%", "wind": "东北风 3级"},
                "上海": {"temp": "28°C", "description": "多云", "humidity": "65%", "wind": "东南风 2级"},
                "广州": {"temp": "32°C", "description": "雷阵雨", "humidity": "85%", "wind": "南风 4级"},
                "深圳": {"temp": "30°C", "description": "多云转晴", "humidity": "70%", "wind": "东风 3级"},
                "成都": {"temp": "22°C", "description": "阴", "humidity": "80%", "wind": "北风 2级"},
                "杭州": {"temp": "26°C", "description": "晴", "humidity": "55%", "wind": "西北风 3级"},
                "武汉": {"temp": "24°C", "description": "多云", "humidity": "60%", "wind": "东北风 2级"},
                "南京": {"temp": "25°C", "description": "晴转多云", "humidity": "50%", "wind": "西南风 3级"},
                "西安": {"temp": "20°C", "description": "晴", "humidity": "40%", "wind": "西风 2级"},
                "重庆": {"temp": "27°C", "description": "小雨", "humidity": "90%", "wind": "东北风 1级"},
                "天津": {"temp": "23°C", "description": "多云", "humidity": "55%", "wind": "东风 3级"},
                "苏州": {"temp": "26°C", "description": "晴", "humidity": "50%", "wind": "东南风 2级"},
            }
            
            if city in mock_data:
                weather = mock_data[city]
                return f"{city}天气信息：\n🌡️ 温度：{weather['temp']}\n☁️ 天气：{weather['description']}\n💧 湿度：{weather['humidity']}\n💨 风力：{weather['wind']}"
            else:
                supported = "、".join(list(mock_data.keys()))
                return f"抱歉，暂未收录 '{city}' 的天气信息。支持的城市：{supported}"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid={api_key}&units=metric&lang=zh_cn"
        parsed_url = urlparse(url)
        
        conn = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port or 80, timeout=10)
        conn.request('GET', parsed_url.path + '?' + parsed_url.query)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        
        if response.status != 200:
            return f"获取天气失败，错误码: {response.status}"
        
        result = json.loads(data)
        temp = result['main']['temp']
        desc = result['weather'][0]['description']
        humidity = result['main']['humidity']
        wind = result['wind']['speed']
        
        return f"{city}天气信息：\n🌡️ 温度：{temp}°C\n☁️ 天气：{desc}\n💧 湿度：{humidity}%\n💨 风速：{wind} m/s"
    
    except Exception as e:
        return f"获取天气时出错: {str(e)}"

def call_function(function_name, **kwargs):
    functions = {
        'list_files': list_files,
        'rename_file': rename_file,
        'delete_file': delete_file,
        'create_file': create_file,
        'read_file': read_file,
        'curl': curl,
        'get_weather': get_weather
    }
    
    if function_name not in functions:
        return f"错误：未知函数 '{function_name}'"
    
    try:
        return functions[function_name](**kwargs)
    except TypeError as e:
        return f"错误：函数参数不正确 - {str(e)}"
    except Exception as e:
        return f"错误：{str(e)}"