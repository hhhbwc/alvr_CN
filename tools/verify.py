#!/usr/bin/env python3
"""不做编译的静态自检：括号配平、词表一致性、依赖可用性。"""
import json
import os
import re
import subprocess
import sys

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'alvr-src'))


def strip_code(s: str) -> str:
    """去掉注释与字符串字面量，只留结构字符。"""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == '/' and i + 1 < n and s[i + 1] == '/':
            while i < n and s[i] != '\n':
                i += 1
        elif c == '/' and i + 1 < n and s[i + 1] == '*':
            i += 2
            while i + 1 < n and not (s[i] == '*' and s[i + 1] == '/'):
                i += 1
            i += 2
        elif c == '"':
            i += 1
            while i < n:
                if s[i] == '\\':
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
        elif c == 'r' and i + 1 < n and s[i + 1] == '#':
            m = re.match(r'r(#+)"', s[i:])
            if m:
                hashes = m.group(1)
                end = s.find('"' + hashes, i + len(m.group(0)))
                i = (end + len(hashes) + 1) if end != -1 else n
            else:
                out.append(c)
                i += 1
        elif c == "'":
            # 字符字面量或生命周期
            m = re.match(r"'(\\.|[^\\'])'", s[i:])
            if m:
                i += len(m.group(0))
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def balance(text):
    code = strip_code(text)
    return {
        '{': code.count('{') - code.count('}'),
        '(': code.count('(') - code.count(')'),
        '[': code.count('[') - code.count(']'),
    }


def changed_files():
    out = subprocess.run(['git', '-C', SRC, 'diff', '--name-only'],
                         capture_output=True, text=True).stdout.split()
    untracked = subprocess.run(['git', '-C', SRC, 'ls-files', '--others', '--exclude-standard'],
                               capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith('.rs')], [f for f in untracked if f.endswith('.rs')]


def main():
    ok = True
    mod, new = changed_files()
    print(f'修改 {len(mod)} 个 .rs，新增 {len(new)} 个 .rs')

    for f in mod:
        full = os.path.join(SRC, f)
        old = subprocess.run(['git', '-C', SRC, 'show', f'HEAD:{f}'],
                             capture_output=True, text=True).stdout
        b_old, b_new = balance(old), balance(open(full, encoding='utf-8').read())
        if b_new != {'{': 0, '(': 0, '[': 0}:
            print(f'  !! {f} 括号不配平: {b_new}')
            ok = False
        elif b_old != b_new and f.endswith('zh_cn.rs'):
            pass

    for f in new:
        full = os.path.join(SRC, f)
        b = balance(open(full, encoding='utf-8').read())
        if b != {'{': 0, '(': 0, '[': 0}:
            print(f'  !! {f} 括号不配平: {b}')
            ok = False

    # 词表条数
    d = json.load(open(os.path.join(os.path.dirname(__file__), '..',
                                    'translations', 'zh-CN.json'), encoding='utf-8'))
    table = open(os.path.join(SRC, 'alvr', 'gui_common', 'src', 'zh_cn.rs'),
                 encoding='utf-8').read()
    arms = table.count('=> Some(')
    expect = sum(len(d[k]) for k in ('paths', 'helps', 'ids', 'text'))
    print(f'词表条目 {expect}，生成 match 分支 {arms}')
    if arms != expect:
        print('  !! 分支数与词表不一致')
        ok = False

    # 字体
    font = os.path.join(SRC, 'alvr', 'gui_common', 'resources', 'fonts',
                        'NotoSansSC-Subset.otf')
    print(f'字体 {os.path.getsize(font)/1024:.0f} KB' if os.path.exists(font)
          else '  !! 字体缺失')
    if not os.path.exists(font):
        ok = False

    # 逐字校验：词表里的每个汉字/全角符号都必须在字体里，否则界面会出现豆腐块
    if os.path.exists(font):
        try:
            from fontTools.ttLib import TTFont
            cmap = set()
            for t in TTFont(font)['cmap'].tables:
                cmap |= set(t.cmap.keys())
            need = set()
            for sect in ('paths', 'helps', 'ids', 'text'):
                for k, v in d.get(sect, {}).items():
                    need.update(k)
                    need.update(v)
            # 只检查 CJK / 全角区：emoji 由 egui 内置 emoji 字体兜底
            missing = sorted({c for c in need
                              if not c.isspace() and ord(c) not in cmap
                              and (0x3000 <= ord(c) <= 0x9FFF
                                   or 0xFF00 <= ord(c) <= 0xFFEF
                                   or 0x4E00 <= ord(c) <= 0x9FFF)})
            if missing:
                print(f'  !! 字体缺少 {len(missing)} 个字: {"".join(missing)}')
                print('     修法: python tools/font.py --font <NotoSansSC.otf> --out fonts/NotoSansSC-Subset.otf')
                ok = False
            else:
                print('字体覆盖: 词表用字全部命中')
        except ImportError:
            print('  (跳过字形校验：未安装 fonttools)')

    # 依赖检查：用到 zh_cn 的 crate 必须依赖 alvr_gui_common
    for rel in ('alvr/dashboard', 'alvr/launcher'):
        car = open(os.path.join(SRC, rel, 'Cargo.toml'), encoding='utf-8').read()
        if 'alvr_gui_common' not in car:
            print(f'  !! {rel} 未依赖 alvr_gui_common')
            ok = False

    # 残留的坏转义
    for f in mod + new:
        t = open(os.path.join(SRC, f), encoding='utf-8').read()
        if 'bool {{' in t or 'fn {{' in t:
            print(f'  !! {f} 存在双重花括号残留')
            ok = False

    print('自检通过' if ok else '自检有问题')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
