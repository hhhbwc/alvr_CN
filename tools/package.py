#!/usr/bin/env python3
"""把构建产物打包成发布用 zip（去掉 pdb/debug 等体积大户）。

用法: python tools/package.py --src <streamer_dir> --out <zip> [--suffix _zh]
"""
import argparse
import os
import zipfile

# 发布包里不需要的文件
SKIP_EXT = ('.pdb', '.lib', '.exp', '.h', '.hpp', '.pc')
SKIP_DIR = ('debug',)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--root', default='', help='zip 内的顶层目录名')
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    n = 0
    total = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dirpath, dirnames, files in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
            for f in files:
                if f.lower().endswith(SKIP_EXT):
                    continue
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, src).replace(os.sep, '/')
                arc = f'{args.root}/{rel}' if args.root else rel
                z.write(full, arc)
                n += 1
                total += os.path.getsize(full)
    print(f'{n} 个文件，原始 {total/1048576:.0f} MB -> {os.path.getsize(out)/1048576:.0f} MB')
    print(out)


if __name__ == '__main__':
    main()
