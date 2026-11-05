"""扫描两个版本源码里仍未翻译的英文界面文案，并区分：
   [D] 已套 tr() 但词表缺条目（只需补词表）
   [P] 代码里根本没套 tr()（需要打补丁）
用法：python tools/scan_missing.py
"""
import os
import re
import json

ROOTS = {'v20': '../alvr-v20/alvr', 'v21': '../alvr-src/alvr'}
DICTS = {'v20': 'translations/zh-CN-v20.json', 'v21': 'translations/zh-CN.json'}

SKIP = re.compile(
    r'(https?://|\.txt|\.exe|\.dll|\.zip|\.json|\.apk|\.otf|\.ttf'
    r'|%[sd]|\{\}|^[a-z0-9_]+$|^[A-Z0-9_]{3,}$|session_settings'
    r'|^[a-z]+(_[a-z]+)+$|^[A-Za-z]+::|^[A-Z][a-z]+ [A-Z][a-z]+::$'
    r'|Invalid page index|borrow)'
)

# 这些文件的文案不是界面文字（日志/错误上报）
SKIP_FILES = ('data_sources.rs', 'new_version_popup.rs')


def literals(path):
    src = open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'(?<![r#])"((?:[^"\\\n]|\\.)*)"', src):
        out.append((m.group(1), src.count('\n', 0, m.start()) + 1))
    for m in re.finditer(r'r(#*)"(.*?)"\1', src, re.S):
        out.append((m.group(2), src.count('\n', 0, m.start()) + 1))
    return out


def is_wrapped(src, text):
    esc = text.replace('\\', '\\\\').replace('"', '\\"')
    return ('zh_cn::tr("' + esc + '")') in src or ("zh_cn::tr(r#" + '"' + text + '"#)') in src


for tag, root in ROOTS.items():
    text_map = json.load(open(DICTS[tag], encoding='utf-8'))['text']
    print('\n########## %s ##########' % tag)
    need_dict, need_patch = [], []
    for dirpath, _, files in os.walk(root):
        if not any(k in dirpath.replace(os.sep, '/') for k in ('/dashboard', '/launcher')):
            continue
        for f in sorted(files):
            if not f.endswith('.rs') or f == 'zh_cn.rs':
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, root).replace(os.sep, '/')
            src = open(p, encoding='utf-8').read()
            for text, line in literals(p):
                if len(text) < 10 or text in text_map:
                    continue
                if not re.search(r'[A-Za-z]{2,} [A-Za-z]', text):
                    continue
                if SKIP.search(text):
                    continue
                item = (rel, line, text)
                if is_wrapped(src, text):
                    need_dict.append(item)
                elif f not in SKIP_FILES:
                    need_patch.append(item)

    def dump(title, items):
        print('\n--- %s（%d 条）---' % (title, len(items)))
        for rel, line, text in items:
            print('  %-52s :%-4d %s' % (rel, line, text[:86].replace('\n', ' / ')))

    dump('[P] 代码未套 tr()，需打补丁', need_patch)
    dump('[D] 缺词表条目（已套 tr）', need_dict)

    json.dump([{'file': r, 'line': l, 'text': t} for r, l, t in need_dict],
              open('missing-%s.json' % tag, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
