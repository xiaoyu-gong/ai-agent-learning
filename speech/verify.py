import re

with open(r'c:\Users\WGXY\Documents\trae_projects\XM\speech\speech_draft.md', 'r', encoding='utf-8') as f:
    text = f.read()

lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().startswith('#')]
body = ''.join(lines)

total_chars = len(body)
print(f'【总字符数】{total_chars} / 900 (限制)')

paragraphs = [p for p in text.split('\n\n') if p.strip() and not p.strip().startswith('#')]
para_texts = [p.replace('\n', '') for p in paragraphs]
print(f'【段落数】{len(para_texts)} / 5 (目标)')

for i, p in enumerate(para_texts):
    print(f'  第{i+1}段: {len(p)} 字符')

forbidden = ['综上所述', '众所周知', '非常', '极其', '很棒', '优秀', '我想说的是', '在这里', '谢谢聆听', '我们']
print()
print('【禁用词扫描】')
found_any = False
for word in forbidden:
    if word in body:
        print(f'  ❌ 发现禁用词: "{word}"')
        found_any = True
if not found_any:
    print('  ✅ 未发现禁用词')

sentences = re.split(r'[。！？]', body)
print()
print('【长句检查 (>40字)】')
long_count = 0
for s in sentences:
    s = s.strip()
    if s and len(s) > 40:
        print(f'  ⚠️ {len(s)}字: {s[:60]}...')
        long_count += 1
if long_count == 0:
    print('  ✅ 无超长句')

print()
print('【数据准确性】')
checks = {
    '71.5%': '压缩率',
    '4521': '压缩前字符数',
    '1287': '压缩后字符数',
    '53.3%': '消息减少率',
    '16.3': 'Token速度',
    '0.31': '首Token延迟',
    '579': '求和结果',
    '10': '迭代上限',
}
for val, desc in checks.items():
    if val in body:
        print(f'  ✅ {desc}({val}) 已引用')
    else:
        print(f'  ❌ {desc}({val}) 缺失')

print()
print('【核心概念覆盖】')
concepts = ['零第三方依赖', 'Skill', '热加载', '链式调用', 'ChainedCallContext', 'http.client', 'Qwen2.5', 'LM Studio', 'AnythingLLM', 'RAG']
for c in concepts:
    if c in body:
        print(f'  ✅ {c}')
    else:
        print(f'  ❌ {c} 缺失')

print()
print('【人称检查】')
if '我们' in body:
    print('  ❌ 发现"我们"，应全部使用"我"或"本项目"')
else:
    print('  ✅ 未使用"我们"')

# Check for 1st person consistency
print()
print('【结构完整性】')
sections = ['背景痛点', '技术方案', '验证数据', '开源RAG', '上下文压缩', '链式调用']
for s in sections:
    if s in body:
        print(f'  ✅ {s}')
    else:
        print(f'  ❌ {s} 缺失')

# Check for PPT-style bullet points
if body.count('\n-') > 2:
    print('\n⚠️ 疑似PPT式列表格式过多')
else:
    print('\n✅ 非PPT式分点列表，符合演讲稿格式')
