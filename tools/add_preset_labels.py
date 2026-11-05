#!/usr/bin/env python3
"""补充预设下拉项与预设 help 的中文（只影响显示，不影响写回 session 的值）。"""
import json
import re

BS = chr(92)
SRC = r'..\alvr-src\alvr\dashboard\src\dashboard\components\settings_controls\presets\builtin_schema.rs'
src = open(SRC, encoding='utf-8').read()

# 预设带的 help（含 Rust 行连续符，需要按编译器规则还原）
raw_helps = re.findall(r'"help"\.into\(\),\s*"([\s\S]*?)"\s*\.into\(\)', src)


def rust_unescape(s: str) -> str:
    # 1) 行尾反斜杠 + 换行 + 行首空白 -> 直接删除（Rust 行连续）
    s = re.sub(BS + BS + r'\r?\n[ \t]*', '', s, count=0) if False else s
    out, i = [], 0
    while i < len(s):
        if s[i] == BS and i + 1 < len(s) and s[i + 1] in '\r\n':
            i += 1
            if s[i] == '\r':
                i += 1
            while i < len(s) and s[i] in ' \t':
                i += 1
            continue
        if s[i] == BS and i + 1 < len(s):
            nxt = s[i + 1]
            out.append({'n': '\n', 't': '\t', 'r': '\r', '"': '"', BS: BS}.get(nxt, nxt))
            i += 2
            continue
        out.append(s[i])
        i += 1
    return ''.join(out)


helps = [rust_unescape(h) for h in raw_helps]
zh_helps = [
    '分辨率选得过高（通常是「高（宽 5184）」）会导致延迟升高甚至黑屏。',
    '画质档位选得太高可能造成卡顿甚至画面定格！',
    '注视点编码会影响画面边缘的像素化程度，并显著降低编解码延迟。' + chr(10) +
    '不建议完全关闭，否则可能出现卡顿和高编解码延迟！',
]
assert len(zh_helps) == len(helps), (len(zh_helps), len(helps))

# 预设下拉项（只用于显示）
values = {
    'Very Low (width: 3072)': '极低（宽 3072）',
    'Low (width: 3712)': '低（宽 3712）',
    'Medium (width: 4288)': '中（宽 4288）',
    'High (width: 5184)': '高（宽 5184）',
    'Ultra (width: 5632)': '超高（宽 5632）',
    'Extreme (width: 6080)': '极高（宽 6080）',
    'Speed': '速度优先',
    'Balanced': '均衡',
    'Quality': '画质优先',
    'Light': '轻',
    'Medium': '中',
    'High': '高',
    'Disabled': '关闭',
    'Enabled': '启用',
    'System Default': '系统默认',
    'Automatic': '自动',
    'ALVR bindings': 'ALVR 按键绑定',
}

d = json.load(open('translations/extra.json', encoding='utf-8'))
d.update(values)
for h, z in zip(helps, zh_helps):
    d[h] = z
json.dump(d, open('translations/extra.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('extra.json ->', len(d), '条')

# H.264 配置档保持英文（避免被 "High"->"高" 这类通用词波及）
n = json.load(open('translations/names.json', encoding='utf-8'))
for v in ('High', 'Main', 'Baseline'):
    n[f'video.encoder_config.h264_profile.{v}'] = v
json.dump(n, open('translations/names.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('names.json ->', len(n), '条')
