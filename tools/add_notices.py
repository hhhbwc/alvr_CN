#!/usr/bin/env python3
"""把 builtin_schema.rs 里预设页的 notice 抽取出来并补上中文翻译（按顺序对齐）。"""
import json
import re

BS = chr(92)
SRC = r'..\alvr-src\alvr\dashboard\src\dashboard\components\settings_controls\presets\builtin_schema.rs'
src = open(SRC, encoding='utf-8').read()
raw = re.findall(r'"notice"\.into\(\),\s*"([\s\S]*?)"\s*\.into\(\)', src)
print('抓到', len(raw), '条预设警示')


def unescape(s: str) -> str:
    return (s.replace(BS + 'n', chr(10))
             .replace(BS + '"', '"')
             .replace(BS + BS, BS))


vals = [unescape(r) for r in raw]
zh = [
    'AV1 编码仅支持 RDNA3、Ada Lovelace、Intel ARC 或更新的 GPU'
    '（AMD RX 7xxx+、NVIDIA RTX 40xx+、Intel ARC），' + chr(10) +
    '以及搭载 XR2 Gen 2 的头显（Quest 3、Pico 4 Ultra）。' + chr(10) + chr(10) +
    'Windows 上 Intel ARC 显卡目前不支持 H264 编码。',
    '可以在系统任务栏托盘（右下角）切换默认音频设备',
]
assert len(zh) == len(vals), (len(zh), len(vals))

d = json.load(open('translations/extra.json', encoding='utf-8'))
for v, z in zip(vals, zh):
    d[v] = z
json.dump(d, open('translations/extra.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('extra.json ->', len(d), '条')
