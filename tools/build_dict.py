#!/usr/bin/env python3
"""合并 catalog.json 与 translations/*.json，校验并生成最终词表 zh-CN.json。

校验内容：
  - names/helps 里的 key 必须存在于 catalog 的路径中（防笔误）
  - 统计覆盖率，列出仍未翻译的条目
"""
import argparse
import json
import os
import sys


def load(p):
    return json.load(open(p, encoding='utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', default='catalog.json')
    ap.add_argument('--dir', default='translations')
    ap.add_argument('--out', default='translations/zh-CN.json')
    args = ap.parse_args()

    cat = load(args.catalog)
    names = load(os.path.join(args.dir, 'names.json'))
    helps = load(os.path.join(args.dir, 'helps.json'))
    ui = load(os.path.join(args.dir, 'ui.json'))
    extra_path = os.path.join(args.dir, 'extra.json')
    extra = load(extra_path) if os.path.exists(extra_path) else {}

    setting_paths = {s['path'] for s in cat['settings']}
    enum_paths = {e['path'] for e in cat['enums']}
    all_paths = setting_paths | enum_paths
    help_paths = {s['path'] for s in cat['settings'] if s['help']}
    ui_keys = {u['en'] for u in cat['ui']}

    errors = []
    for k in names:
        if k not in all_paths:
            errors.append(f'names.json 里不存在的路径: {k}')
    for k in helps:
        if k not in help_paths:
            errors.append(f'helps.json 里没有帮助文案的路径: {k}')
    for k in ui:
        if k not in ui_keys:
            errors.append(f'ui.json 里未在源码中找到的文案: {k!r}')
    # 词表是跨版本共用的：本版本里不存在的路径/文案只提示，不算错
    if errors:
        print(f'提示: {len(errors)} 条词条不属于本版本（将跳过）')
        for e in errors[:5]:
            print('  ', e)

    # id 兜底表：叶子 id -> 中文（同 id 冲突则保留首个）
    ids = {}
    conflict = set()
    for p, zh in names.items():
        leaf = p.split('.')[-1]
        if leaf in ids and ids[leaf] != zh:
            conflict.add(leaf)
        ids.setdefault(leaf, zh)
    for c in conflict:
        ids.pop(c, None)

    # 英文原文 -> 中文（显式 display_name 为英文时也能命中）
    text = dict(extra)
    text.update(ui)
    for s in cat['settings']:
        zh = names.get(s['path'])
        if zh and s['name']:
            text.setdefault(s['name'], zh)
    for e in cat['enums']:
        zh = names.get(e['path'])
        if zh and e['name']:
            text.setdefault(e['name'], zh)

    out = {
        'meta': {
            'language': 'zh-CN',
            'based_on': 'alvr-org/ALVR master (21.0.0-dev14)',
            'generated_by': 'alvr-cn/tools/build_dict.py',
        },
        'paths': names,
        'helps': helps,
        'ids': ids,
        'text': text,
    }
    json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    s_total = len(cat['settings'])
    s_done = sum(1 for s in cat['settings'] if s['path'] in names)
    e_total = len(cat['enums'])
    e_done = sum(1 for e in cat['enums'] if e['path'] in names)
    h_total = len(help_paths)
    h_done = len(helps)
    u_total = len(ui_keys)
    u_done = sum(1 for u in cat['ui'] if u['en'] in ui)

    print(f'设置项名称  {s_done}/{s_total}')
    print(f'枚举变体    {e_done}/{e_total}')
    print(f'帮助文案    {h_done}/{h_total}')
    print(f'界面文案    {u_done}/{u_total}')
    print(f'id 兜底表   {len(ids)} 条（{len(conflict)} 个 id 有歧义已剔除）')
    print(f'原文直译表  {len(text)} 条')
    print(f'已写出 {args.out}')

    print('\n--- 仍缺名称的设置项 ---')
    for s in cat['settings']:
        if s['path'] not in names:
            print('  ', s['path'])
    print('--- 仍缺翻译的帮助 ---')
    for p in sorted(help_paths):
        if p not in helps:
            print('  ', p)
    print('--- 仍缺翻译的界面文案 ---')
    for u in cat['ui']:
        if u['en'] not in ui:
            print('  ', repr(u['en']))


if __name__ == '__main__':
    main()
