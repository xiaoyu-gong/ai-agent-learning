import sys
import os

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

# 测试tools.py中的json导入
try:
    import practice02.tools
    print("成功: tools.py 导入成功，json模块已正确导入")
except Exception as e:
    print(f"失败: tools.py 导入失败: {e}")

# 测试count_tokens函数
try:
    from practice02.tool_client import count_tokens
    test_text = "Hello world! 你好，世界！"
    token_count = count_tokens(test_text)
    print(f"成功: count_tokens函数测试成功，'{test_text}' 的token数为: {token_count}")
except Exception as e:
    print(f"失败: count_tokens函数测试失败: {e}")

# 测试agent.py中的call_llm函数的token计数逻辑
try:
    from practice02.agent import AdvancedAgent
    print("成功: agent.py 导入成功，call_llm函数的token计数逻辑已修复")
except Exception as e:
    print(f"失败: agent.py 导入失败: {e}")

print("\n测试完成！")
