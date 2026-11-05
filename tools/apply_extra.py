"""补充汉化补丁：包住此前漏掉的多行调用、辅助函数与单点文案。

用法：python tools/apply_extra.py --src ../alvr-v20
      python tools/apply_extra.py --src ../alvr-src

所有改动都是幂等的（已改过的会跳过）。适用于 v20.14.1 与 v21 两条代码线。
"""
import argparse
import os
import sys

MARK = 'ALVR-CN-PATCH'
TR = 'alvr_gui_common::zh_cn::tr'

# (相对 alvr/ 的路径, 说明, 旧串, 新串, 是否全量替换)
PATCHES = [
    # ---------- 统计页 ----------
    ('dashboard/src/dashboard/components/statistics.rs', '统计页 图表标题',
     'ui.label(RichText::new(title).size(20.0));',
     f'ui.label(RichText::new({TR}(title)).size(20.0));', False),
    ('dashboard/src/dashboard/components/statistics.rs', '统计页 图表行标签（全部）',
     'ui.colored_label(color, text);',
     f'ui.colored_label(color, {TR}(text));', True),
    ('dashboard/src/dashboard/components/statistics.rs', '统计页 吞吐量注释',
     'ui.small("Note: throughput is the peak bitrate, packet_size/network_latency.");',
     f'ui.small({TR}("Note: throughput is the peak bitrate, packet_size/network_latency."));', False),
    ('dashboard/src/dashboard/components/statistics.rs', '统计页 丢包标签',
     'ui[0].label("Total packets lost:");',
     f'ui[0].label({TR}("Total packets lost:"));', False),

    # ---------- 设置向导 ----------
    ('dashboard/src/dashboard/components/setup_wizard.rs', '向导 小标题',
     'ui.heading(RichText::new(subtitle).size(20.0));',
     f'ui.heading(RichText::new({TR}(subtitle)).size(20.0));', False),
    ('dashboard/src/dashboard/components/setup_wizard.rs', '向导 正文',
     'ui.add(Label::new(RichText::new(paragraph).size(14.0)).wrap());',
     f'ui.add(Label::new(RichText::new({TR}(paragraph)).size(14.0)).wrap());', False),
    ('dashboard/src/dashboard/components/setup_wizard.rs', '向导 Back 按钮',
     'Button::new("Back")',
     f'Button::new({TR}("Back"))', False),

    # ---------- 警示框组件（统一兜底）----------
    ('dashboard/src/dashboard/components/settings_controls/notice.rs', '警示框组件',
     'ui.add(Label::new(RichText::new(text).size(11.0).color(Color32::BLACK)).wrap());',
     f'ui.add(Label::new(RichText::new({TR}(text)).size(11.0).color(Color32::BLACK)).wrap());', False),

    # ---------- 关于页 ----------
    ('dashboard/src/dashboard/components/about.rs', '关于页 GitHub 链接',
     'ui.hyperlink_to("Visit us on GitHub", "https://github.com/alvr-org/ALVR");',
     f'ui.hyperlink_to({TR}("Visit us on GitHub"), "https://github.com/alvr-org/ALVR");', False),
    ('dashboard/src/dashboard/components/about.rs', '关于页 Discord 链接',
     'ui.hyperlink_to("Join us on Discord", "https://discord.gg/ALVR");',
     f'ui.hyperlink_to({TR}("Join us on Discord"), "https://discord.gg/ALVR");', False),
    ('dashboard/src/dashboard/components/about.rs', '关于页 最新版本链接',
     '        "Latest release",',
     f'        {TR}("Latest release"),', False),
    ('dashboard/src/dashboard/components/about.rs', '关于页 捐赠链接',
     '        "Donate to ALVR on Open Collective",',
     f'        {TR}("Donate to ALVR on Open Collective"),', False),

    # ---------- 调试页 ----------
    ('dashboard/src/dashboard/components/debug.rs', '调试页 截图按钮',
     'if ui[0].button("Capture frame").clicked() {',
     f'if ui[0].button({TR}("Capture frame")).clicked() {{', False),

    # ---------- 设备页 ----------
    ('dashboard/src/dashboard/components/devices.rs', '设备页 未知 IP',
     '.map_or_else(|| "Unknown IP".into(), |ip| ip.to_string()),',
     f'.map_or_else(|| {TR}("Unknown IP").into(), |ip| ip.to_string()),', False),

    # ---------- 通知区 ----------
    ('dashboard/src/dashboard/components/notifications.rs', '无通知提示 1',
     'message: NO_NOTIFICATIONS_MESSAGE.into(),',
     f'message: {TR}(NO_NOTIFICATIONS_MESSAGE).into(),', False),
    ('dashboard/src/dashboard/components/notifications.rs', '无通知提示 2',
     '.unwrap_or_else(|| NO_NOTIFICATIONS_MESSAGE.into());',
     f'.unwrap_or_else(|| {TR}(NO_NOTIFICATIONS_MESSAGE).into());', False),

    # ---------- 枚举选项文字：路径查不到时再按原文查表 ----------
    ('dashboard/src/dashboard/components/settings_controls/choice.rs', '枚举选项文字兜底',
     '                    .unwrap_or_else(|| get_display_name(&entry.name, &entry.strings));',
     f'                    .unwrap_or_else(|| {{\n'
     f'                        {TR}(&get_display_name(&entry.name, &entry.strings))\n'
     f'                    }});', False),

    # ---------- 预设下拉 ----------
    ('dashboard/src/dashboard/components/settings_controls/choice.rs', '预设未应用',
     '            "Preset not applied".into()',
     f'            {TR}("Preset not applied").into()', False),

    # ---------- 字典/向量默认值 ----------
    # 注意：reset_button 的第三个参数是 &str，tr() 返回 String，必须加 &
    ('dashboard/src/dashboard/components/settings_controls/dictionary.rs', '字典默认列表',
     'reset::reset_button(ui, true, "default list")',
     f'reset::reset_button(ui, true, &{TR}("default list"))', False),
    ('dashboard/src/dashboard/components/settings_controls/vector.rs', '向量默认列表',
     'reset::reset_button(ui, true, "default list")',
     f'reset::reset_button(ui, true, &{TR}("default list"))', False),
    ('dashboard/src/dashboard/components/settings_controls/dictionary.rs', '字典默认列表(补 &)',
     f'reset::reset_button(ui, true, {TR}("default list"))',
     f'reset::reset_button(ui, true, &{TR}("default list"))', False),
    ('dashboard/src/dashboard/components/settings_controls/vector.rs', '向量默认列表(补 &)',
     f'reset::reset_button(ui, true, {TR}("default list"))',
     f'reset::reset_button(ui, true, &{TR}("default list"))', False),

    # ---------- 重置按钮悬浮提示 ----------
    ('dashboard/src/dashboard/components/settings_controls/reset.rs', '重置按钮提示',
     '.on_hover_text(format!("Reset to {default_str}"))',
     f'.on_hover_text(format!("{{}}{{default_str}}", {TR}("Reset to ")))', False),

    # ---------- 设置项提示 ----------
    ('dashboard/src/dashboard/components/settings_controls/section.rs', '需先保存进度',
     '                                "Please save your in-game progress first"',
     f'                                {TR}("Please save your in-game progress first")', False),
    # tooltip(ui, id, text: &str) 需要 &str
    ('dashboard/src/dashboard/components/settings_controls/section.rs', '实时生效提示',
     '                            "This setting can be changed in real-time during streaming!",',
     f'                            &{TR}("This setting can be changed in real-time during streaming!"),', False),
    ('dashboard/src/dashboard/components/settings_controls/section.rs', '实时生效提示(补 &)',
     f'                            {TR}("This setting can be changed in real-time during streaming!"),',
     f'                            &{TR}("This setting can be changed in real-time during streaming!"),', False),
    ('dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs', '预设 需先保存进度',
     '                        "Please save your in-game progress first"',
     f'                        {TR}("Please save your in-game progress first")', False),
    ('dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs', '预设 实时生效提示',
     '                    "This setting can be changed in real-time during streaming!",',
     f'                    &{TR}("This setting can be changed in real-time during streaming!"),', False),
    ('dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs', '预设 实时生效提示(补 &)',
     f'                    {TR}("This setting can be changed in real-time during streaming!"),',
     f'                    &{TR}("This setting can be changed in real-time during streaming!"),', False),
    ('dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs', '预设 重启 SteamVR 提示',
     '                        "Changing this setting will make SteamVR restart!\\n{}",',
     f'                        "{{}}\\n{{}}",\n'
     f'                        {TR}("Changing this setting will make SteamVR restart!"),', False),

    # ---------- v21 变体：section.rs 里的跨行提示（\n\ 续行写法）----------
    ('dashboard/src/dashboard/components/settings_controls/section.rs', 'v21 重启 SteamVR 提示',
     '                                "Changing this setting will make SteamVR restart!\\n\\\n'
     '                                Please save your in-game progress first",',
     '                                format!(\n'
     f'                                    "{{}}\\n{{}}",\n'
     f'                                    {TR}("Changing this setting will make SteamVR restart!"),\n'
     f'                                    {TR}("Please save your in-game progress first")\n'
     '                                ),', False),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='ALVR 源码根目录')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    root = os.path.join(args.src, 'alvr')
    if not os.path.isdir(root):
        print(f'!! 找不到 {root}')
        sys.exit(1)

    ok = skip = miss = 0
    for rel, label, old, new, all_occurrences in PATCHES:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f'  !! {label}: 文件不存在 {rel}')
            miss += 1
            continue
        text = open(path, encoding='utf-8').read()
        if new in text and old not in text.replace(new, ''):
            print(f'  = {label} 已打过，跳过')
            skip += 1
            continue
        if old not in text:
            if new in text:
                print(f'  = {label} 已打过，跳过')
                skip += 1
            else:
                print(f'  !! {label}: 未匹配 -> {old[:60]}')
                miss += 1
            continue
        if all_occurrences:
            n = text.count(old)
            text = text.replace(old, new)
        else:
            n = 1
            text = text.replace(old, new, 1)
        if not args.dry_run:
            open(path, 'w', encoding='utf-8', newline='\n').write(text)
        print(f'  + {label}（{n} 处）')
        ok += 1

    print(f'\n合计：新增 {ok}，已存在 {skip}，未匹配 {miss}')
    return 0 if miss == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
