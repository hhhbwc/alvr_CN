#!/usr/bin/env python3
"""v20.x 专用补丁：v20 的部分代码写法与 v21 不同，这里补上差异部分。

先跑 apply.py（通用部分），再跑本脚本。
用法: python tools/apply_v20.py --src ../alvr-v20
"""
import argparse
import os
import re
import sys

MARK = 'ALVR-CN-PATCH'


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, s):
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def patch_line(path, old, new, label):
    if not os.path.exists(path):
        print(f'  !! 找不到 {path}')
        return False
    text = read(path)
    if old not in text:
        if new.strip() in text:
            print(f'  = {label} 已打过，跳过')
            return True
        print(f'  !! {label}: 未匹配')
        return False
    write(path, text.replace(old, new, 1))
    print(f'  + {label}')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    args = ap.parse_args()
    root = os.path.abspath(args.src)

    ctrl = os.path.join(root, 'alvr/dashboard/src/dashboard/components/settings_controls')
    presets = os.path.join(ctrl, 'presets/higher_order_choice.rs')

    # 1) 预设标题：v20 走 components::get_display_name
    patch_line(
        presets,
        '        let name = components::get_display_name(&schema.name, &schema.strings);',
        '        // ' + MARK + ': 预设标题查表\n'
        '        let name = alvr_gui_common::zh_cn::tr(&components::get_display_name(\n'
        '            &schema.name,\n'
        '            &schema.strings,\n'
        '        ));',
        'presets 标题')

    # 2) 预设下拉选项：v20 是单行写法
    patch_line(
        presets,
        'strings: [("display_name".into(), option.display_name)]',
        'strings: [("display_name".into(), alvr_gui_common::zh_cn::tr(&option.display_name))]',
        'presets 选项文字')

    # 3) 设备页提示条：v20 用 format! 拼接两个字符串
    patch_line(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/devices.rs'),
        'RichText::new(format!(\n'
        '                                    "ALVR requires running SteamVR! {}",\n'
        '                                    "Devices will not be discovered or connected"\n'
        '                                ))',
        'RichText::new(alvr_gui_common::zh_cn::tr(\n'
        '                                    "ALVR requires running SteamVR! '
        'Devices will not be discovered or connected.",\n'
        '                                ))',
        'devices 提示条')

    # 5) FFmpeg 7+ 把 FF_PROFILE_* 改名为 AV_PROFILE_*，v20 的 C++ 代码还是旧名
    sw = os.path.join(root, 'alvr/server_openvr/cpp/platform/win32/VideoEncoderSW.cpp')
    if os.path.exists(sw):
        t = read(sw)
        if 'FF_PROFILE_H264' in t:
            write(sw, t.replace('FF_PROFILE_H264', 'AV_PROFILE_H264'))
            print('  + VideoEncoderSW.cpp FFmpeg 宏改名')

    # 4) v20 的 alvr_packets 没有 path_to_string，补一个本地实现并改调用点
    ctrl_mod = os.path.join(ctrl, 'mod.rs')
    t = read(ctrl_mod)
    if 'fn path_to_string' not in t:
        t += '''
// ''' + MARK + ''': v20 没有 alvr_packets::path_to_string，这里补一个等价实现
pub fn path_to_string(path: &[PathSegment]) -> String {
    let mut s = String::new();
    for (i, seg) in path.iter().enumerate() {
        match seg {
            PathSegment::Name(name) => {
                if i != 0 {
                    s.push('.');
                }
                s.push_str(name);
            }
            PathSegment::Index(index) => {
                s.push_str(&format!("[{index}]"));
            }
        }
    }
    s
}
'''
        write(ctrl_mod, t)
        print('  + settings_controls/mod.rs 补 path_to_string')

    for name in ('section.rs', 'choice.rs'):
        f = os.path.join(ctrl, name)
        t = read(f)
        if 'alvr_packets::path_to_string' in t:
            write(f, t.replace('alvr_packets::path_to_string', 'super::path_to_string'))
            print(f'  + {name} 改用本地 path_to_string')

    # 5) 侧边栏由 apply.py 的正则步骤统一处理，这里不再重复
    print('  = 侧边栏交由 apply.py 处理')


if __name__ == '__main__':
    main()
