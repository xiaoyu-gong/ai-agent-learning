import sys, json
sys.path.insert(0, '.')
import tool_client as tc

tc.load_env()

SYSTEM_PROMPT = """你是一个执行链式工具调用的AI助手。

## 输出格式要求
你必须严格按以下JSON格式输出（不要用markdown代码块包裹）：

继续调用工具时:
{"done": false, "tool_call": {"name": "list_directory", "arguments": {"path": "practice07"}}}

任务完成时:
{"done": true, "answer": "最终回答内容，总结完成的所有步骤和结果"}

## 可用工具
1. list_directory(path) - 列出目录内容
2. read_file(directory, file_name) - 读取文件内容  
3. create_file(directory, file_name, content) - 创建文件并写入内容
4. fetch_webpage(url) - 获取网页内容

## 注意事项
- 第1步应该是 list_directory 查看目录
- 不要尝试读取目录(非文件)
- 完成所有必要步骤后立即返回 done:true
- 读取文件后得到的数据如果是数字，直接做计算
"""

TOOLS = [
    {"type":"function","function":{"name":"list_directory","description":"列出目录","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"read_file","description":"读文件","parameters":{"type":"object","properties":{"directory":{"type":"string"},"file_name":{"type":"string"}},"required":["directory","file_name"]}}},
    {"type":"function","function":{"name":"create_file","description":"创建文件","parameters":{"type":"object","properties":{"directory":{"type":"string"},"file_name":{"type":"string"},"content":{"type":"string"}},"required":["directory","file_name","content"]}}},
    {"type":"function","function":{"name":"fetch_webpage","description":"获取网页","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
]

# Test 1: File search chain
print("=" * 60)
print("TEST 1: 文件搜索链式调用")
print("=" * 60)
r1 = tc.execute_chained_tool_call(
    "请查找 practice06 目录下有什么文件，并总结其功能",
    SYSTEM_PROMPT, TOOLS
)
print(f"\n最终结果: {r1[:500]}")

# Test 2: Multi-file math
print("\n" + "=" * 60)
print("TEST 2: 多文件操作（读两个数→相加→写结果）")
print("=" * 60)
r2 = tc.execute_chained_tool_call(
    "1.txt和2.txt在项目根目录(C:/Users/WGXY/Documents/trae_projects/XM)。读取这两个文件，把两个正整数相加，将结果写入practice07/result.txt",
    SYSTEM_PROMPT, TOOLS
)
print(f"\n最终结果: {r2[:500]}")

# Test 3: Web processing chain
print("\n" + "=" * 60)
print("TEST 3: 网页处理链式调用")
print("=" * 60)
r3 = tc.execute_chained_tool_call(
    "访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 获取页面内容，总结并保存到 practice07/summary.txt",
    SYSTEM_PROMPT, TOOLS
)
print(f"\n最终结果: {r3[:500]}")

print("\n" + "=" * 60)
print("所有测试完成")
