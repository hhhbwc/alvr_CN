#!/usr/bin/env python3
"""把 Noto Sans SC 裁剪成只含本项目用到的字形。

apply.py 会在打补丁前自动调用 build()，所以词表改动后不会出现豆腐块。

用法: python tools/font.py --font fonts/NotoSansSC-Regular.otf --out fonts/NotoSansSC-Subset.otf
"""
import argparse
import json
import os
import sys

# 除词表用字外额外保留：ASCII + 常用中英标点
EXTRA = (
    ''.join(chr(c) for c in range(0x20, 0x7F))
    + '、。，；：？！“”‘’（）《》【】…—～·×÷±°→←↑↓％'
    + '０１２３４５６７８９'
)


def collect_chars(dict_path: str) -> str:
    chars = set(EXTRA)
    d = json.load(open(dict_path, encoding='utf-8'))
    for sect in ('paths', 'helps', 'ids', 'text'):
        for k, v in d.get(sect, {}).items():
            chars.update(k)
            chars.update(v)

    # 顺带扫目录下所有词表 json，防止"改了翻译没跑 build_dict"
    tdir = os.path.dirname(os.path.abspath(dict_path))
    for name in os.listdir(tdir):
        if not name.endswith('.json'):
            continue
        try:
            data = json.load(open(os.path.join(tdir, name), encoding='utf-8'))
        except Exception:
            continue
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                stack.extend(cur.keys())
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
            elif isinstance(cur, str):
                chars.update(cur)
    return ''.join(sorted(chars))


def build(full_font: str, dict_path: str, out_path: str) -> tuple:
    from fontTools import subset

    text = collect_chars(dict_path)
    opts = subset.Options()
    opts.name_IDs = ['*']
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ['DSIG']

    font = subset.load_font(full_font, opts)
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    subset.save_font(font, out_path, opts)
    return len(text), os.path.getsize(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', default='fonts/NotoSansSC-Regular.otf')
    ap.add_argument('--dict', default='translations/zh-CN.json')
    ap.add_argument('--out', default='fonts/NotoSansSC-Subset.otf')
    args = ap.parse_args()

    try:
        n, size = build(args.font, args.dict, args.out)
    except ImportError:
        print('需要 fonttools： python -m pip install fonttools')
        sys.exit(1)
    print(f'需要字形 {n} 个 -> {args.out} {size/1024:.0f} KB')


if __name__ == '__main__':
    main()
