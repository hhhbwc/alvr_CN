#!/usr/bin/env python3
"""解析 alvr/session/src/settings.rs，生成带真实路径的设置项清单。

策略：
1) 先扫描一遍收集所有 struct / enum 定义（字段、类型、schema 文案）。
2) 从根结构体 Settings 出发，按字段类型递归展开，拼出 video.bitrate_mode 这类路径。

用法: python tools/catalog.py --src ../alvr-src --out catalog.json
"""
import argparse
import json
import os
import re

RE_RAW_STR = re.compile(r'r(#*)"(?:.|\n)*?"\1')
RE_STR = re.compile(r'"(?:[^"\\\n]|\\.)*"')
RE_STRUCT = re.compile(r'^\s*(?:pub )?(struct|enum) (\w+)')
RE_FIELD = re.compile(r'^\s*pub (\w+):\s*(.+?),\s*(?://.*)?$')
RE_VARIANT = re.compile(r'^\s*([A-Z]\w*)\s*(?:=\s*-?\d+)?\s*,\s*$')
RE_DN = re.compile(r'display_name\s*=\s*"((?:[^"\\]|\\.)*)"')
RE_HELP = re.compile(r'help\s*=\s*"((?:[^"\\]|\\.)*)"')


def strip_strings(s):
    s = RE_RAW_STR.sub('""', s)
    return RE_STR.sub('""', s)


def parse_defs(text):
    """返回 (structs, enums)。structs: name -> [field...]；enums: name -> [variant...]"""
    structs, enums = {}, {}
    stack = []          # [{'kind','name','depth'}]
    depth = 0
    attr = []           # 待绑定的属性文本行
    collecting = False

    for line in text.split('\n'):
        code = strip_strings(line)
        stripped = line.strip()

        if not collecting and stripped.startswith('#[schema('):
            collecting = True
            attr.append(line)   # 连续多个 #[schema(..)] 要累积，不能覆盖
            if stripped.endswith(')]'):
                collecting = False
            continue
        if collecting:
            attr.append(line)
            if stripped.endswith(')]'):
                collecting = False
            continue

        m = RE_STRUCT.match(code)
        if m:
            stack.append({'kind': m.group(1), 'name': m.group(2), 'depth': depth})
            if m.group(1) == 'struct':
                structs.setdefault(m.group(2), [])
            else:
                enums.setdefault(m.group(2), [])
            attr = []
            depth += code.count('{') - code.count('}')
            continue

        if stack and depth == stack[-1]['depth'] + 1:
            top = stack[-1]
            if top['kind'] == 'struct':
                fm = RE_FIELD.match(code)
                if fm:
                    a = '\n'.join(attr)
                    dn = RE_DN.search(a)
                    hp = RE_HELP.search(a)
                    structs[top['name']].append({
                        'id': fm.group(1),
                        'ty': fm.group(2).strip(),
                        'name': dn.group(1) if dn else None,
                        'help': hp.group(1) if hp else None,
                    })
                    attr = []
            else:
                vm = RE_VARIANT.match(code)
                if vm:
                    a = '\n'.join(attr)
                    dn = RE_DN.search(a)
                    enums[top['name']].append({
                        'id': vm.group(1),
                        'name': dn.group(1) if dn else None,
                    })
                    attr = []

        depth += code.count('{') - code.count('}')
        while stack and depth <= stack[-1]['depth']:
            stack.pop()
        if not stack:
            attr = []

    return structs, enums


WRAP = re.compile(r'^(?:Switch|Option|Vec|Box|Arc|Rc)\s*<(.+)>$')


def inner_type(ty):
    ty = ty.strip()
    while True:
        m = WRAP.match(ty)
        if m:
            ty = m.group(1).strip()
            continue
        if ty.startswith('['):
            ty = ty[1:].split(';')[0].strip()
            continue
        if ty.startswith('HashMap<') or ty.startswith('BTreeMap<'):
            ty = ty.split('<', 1)[1].rsplit('>', 1)[0].split(',')[-1].strip()
            continue
        return ty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', default='catalog.json')
    args = ap.parse_args()

    root = os.path.abspath(args.src)
    sp = os.path.join(root, 'alvr', 'session', 'src', 'settings.rs')
    structs, enums = parse_defs(open(sp, encoding='utf-8').read())

    settings, enum_items = [], []
    seen = set()

    def walk(struct_name, prefix):
        for f in structs.get(struct_name, []):
            path = f'{prefix}.{f["id"]}' if prefix else f['id']
            settings.append({**f, 'path': path, 'struct': struct_name})
            inner = inner_type(f['ty'])
            if inner in structs:
                walk(inner, path)
            elif inner in enums:
                for v in enums[inner]:
                    enum_items.append({
                        'path': f'{path}.{v["id"]}', 'enum': inner,
                        'variant': v['id'], 'name': v['name'],
                    })

    walk('Settings', '')

    ui = {}
    for rel in ['alvr/dashboard/src', 'alvr/launcher/src', 'alvr/gui_common/src']:
        base = os.path.join(root, rel.replace('/', os.sep))
        for dirpath, _, files in os.walk(base):
            for f in files:
                if not f.endswith('.rs'):
                    continue
                full = os.path.join(dirpath, f)
                relf = os.path.relpath(full, root).replace(os.sep, '/')
                for i, line in enumerate(open(full, encoding='utf-8').read().split('\n'), 1):
                    if not re.search(r'ui\.|label\(|button\(|heading\(|checkbox\('
                                     r'|Window::new|RichText|hover_text|notice'
                                     r'|CollapsingHeader', line):
                        continue
                    for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', line):
                        s = m.group(1)
                        if len(s) < 2 or not any(c.isalpha() for c in s):
                            continue
                        if s.startswith(('http', '/', './', '\\')) or '::' in s:
                            continue
                        if s.endswith(('.json', '.exe', '.apk', '.dll', '.rs')):
                            continue
                        ui.setdefault(s, []).append([relf, i])

    out = {
        'settings': settings,
        'enums': enum_items,
        'ui': [{'en': k, 'hits': v} for k, v in
               sorted(ui.items(), key=lambda kv: -len(kv[1]))],
    }
    json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    named = sum(1 for s in settings if s['name'])
    helped = sum(1 for s in settings if s['help'])
    print(f'设置字段: {len(settings)}  显式名称 {named}  帮助 {helped}')
    print(f'枚举变体: {len(enum_items)}  显式名称 {sum(1 for e in enum_items if e["name"])}')
    print(f'UI 文案 : {len(ui)}')
    top = sorted({s['path'].split('.')[0] for s in settings})
    print('顶层分组:', ', '.join(top))


if __name__ == '__main__':
    main()
