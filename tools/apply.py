#!/usr/bin/env python3
"""把中文词表打进 ALVR 源码树。

用法:
    python tools/apply.py --src ../alvr-src --dict translations/zh-CN.json
    python tools/apply.py --src ../alvr-src --dry-run     # 只报告，不写文件

做了什么：
  1. 生成 alvr/gui_common/src/zh_cn.rs（编译期查表，无运行时依赖）
  2. lib.rs 挂载模块；theme.rs 注入中文字体
  3. 设置面板：按「完整设置路径」取中文名/帮助
  4. 仪表盘与启动器：把界面字面量包进 tr()
"""
import argparse
import json
import os
import re
import sys

MARK = 'ALVR-CN-PATCH'
FONT_REL = '../resources/fonts/NotoSansSC-Subset.otf'

# 行内出现这些调用，才认为是界面文案（用 [(] 代替 \( 避免转义嵌套）
UI_GATE = re.compile(
    r'(?:[.]label[(]|[.]button[(]|[.]heading[(]|[.]checkbox[(]|[.]selectable_label[(]'
    r'|[.]small_button[(]|RichText::new[(]|Window::new[(]|CollapsingHeader::new[(]'
    r'|menu_button[(]|hover_text[(]|label[(]ui|button[(]ui)'
)

# 自定义辅助函数（如 statistics.rs 的 label(ui, text: &str, ...)）需要传 &str
HELPER_GATE = re.compile(r'(?:^|[^.\w])(?:label|button)[(]ui')


def rust_str(s: str) -> str:
    out = []
    for ch in s:
        if ch == '\\':
            out.append('\\\\')
        elif ch == '"':
            out.append('\\"')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\r':
            out.append('\\r')
        elif ch == '\t':
            out.append('\\t')
        else:
            out.append(ch)
    return '"' + ''.join(out) + '"'


def gen_table(d: dict) -> str:
    def arms(mapping, doc):
        lines = [f'/// {doc}']
        return lines, mapping

    out = []
    out.append('//! 简体中文词表 —— 由 alvr-cn/tools/apply.py 自动生成，请勿手改。')
    out.append(f'//! {MARK}')
    out.append('')
    for fname, key, doc in (
        ('path_of', 'paths', '按完整设置路径取中文名'),
        ('help_of', 'helps', '按完整设置路径取中文帮助'),
        ('id_of', 'ids', '按字段 id 取中文名（路径查不到时的兜底）'),
        ('text_of', 'text', '按英文原文取中文'),
    ):
        out.append(f'/// {doc}')
        out.append(f'pub fn {fname}(s: &str) -> Option<&\'static str> {{')
        out.append('    match s {')
        for k, v in d.get(key, {}).items():
            out.append(f'        {rust_str(k)} => Some({rust_str(v)}),')
        out.append('        _ => None,')
        out.append('    }')
        out.append('}')
        out.append('')
    out.append('/// 英文原文 -> 中文，查不到原样返回')
    out.append('pub fn tr(s: &str) -> String {')
    out.append('    match text_of(s) {')
    out.append('        Some(zh) => {')
    out.append('            trace_hit(s);')
    out.append('            zh.to_owned()')
    out.append('        }')
    out.append('        None => {')
    out.append('            trace_missing(s);')
    out.append('            s.to_owned()')
    out.append('        }')
    out.append('    }')
    out.append('}')
    out.append('')
    out.append('fn trace_hit(s: &str) {')
    out.append('    use std::io::Write;')
    out.append('    use std::sync::OnceLock;')
    out.append('    static PATH: OnceLock<Option<std::path::PathBuf>> = OnceLock::new();')
    out.append('    let Some(path) = PATH')
    out.append('        .get_or_init(|| std::env::var_os("ALVR_CN_TRACE_HIT").map(Into::into))')
    out.append('    else {')
    out.append('        return;')
    out.append('    };')
    out.append('    if let Ok(mut f) = std::fs::OpenOptions::new()')
    out.append('        .create(true)')
    out.append('        .append(true)')
    out.append('        .open(path)')
    out.append('    {')
    out.append('        let _ = writeln!(f, "HIT\t{s}");')
    out.append('    }')
    out.append('}')
    out.append('')
    out.append('/// 调试用：设置环境变量 ALVR_CN_TRACE=<文件路径> 后，')
    out.append('/// 所有"查表未命中"的界面文案会追加写入该文件，用来排查漏译。')
    out.append('fn trace_missing(s: &str) {')
    out.append('    use std::io::Write;')
    out.append('    use std::sync::OnceLock;')
    out.append('    static PATH: OnceLock<Option<std::path::PathBuf>> = OnceLock::new();')
    out.append('    let Some(path) = PATH')
    out.append('        .get_or_init(|| std::env::var_os("ALVR_CN_TRACE").map(Into::into))')
    out.append('    else {')
    out.append('        return;')
    out.append('    };')
    out.append('    // 跳过已含中文的（重复查表的噪音）和过短的符号串')
    out.append('    if s.len() < 3 || s.chars().any(|c| (\'\\u{4e00}\'..=\'\\u{9fff}\').contains(&c)) {')
    out.append('        return;')
    out.append('    }')
    out.append('    if let Ok(mut f) = std::fs::OpenOptions::new()')
    out.append('        .create(true)')
    out.append('        .append(true)')
    out.append('        .open(path)')
    out.append('    {')
    out.append('        let _ = writeln!(f, "{s}");')
    out.append('    }')
    out.append('}')
    out.append('')
    return '\n'.join(out)


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, s, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)


def patch_file(path, pairs, dry, label):
    """pairs: [(旧片段, 新片段)]；已打过就跳过。"""
    if not os.path.exists(path):
        print(f'  !! 找不到 {path}')
        return False
    text = read(path)
    if MARK in text:
        print(f'  = {label} 已打过补丁，跳过')
        return True
    for old, new in pairs:
        if old not in text:
            print(f'  !! {label}: 未匹配到片段 -> {old[:60]!r}')
            return False
        text = text.replace(old, new, 1)
    write(path, text, dry)
    print(f'  + {label}')
    return True


def patch_line(path, old, new, dry, label):
    """按"新内容是否已存在"判断幂等，适用于已有 MARK 的文件再追加改动。"""
    if not os.path.exists(path):
        print(f'  !! 找不到 {path}')
        return False
    text = read(path)
    if old not in text:
        if new.strip() in text:
            print(f'  = {label} 已打过补丁，跳过')
            return True
        print(f'  !! {label}: 未匹配')
        return False
    write(path, text.replace(old, new, 1), dry)
    print(f'  + {label}')
    return True


def patch_regex(path, pattern, repl, dry, label, already=None):
    """正则版补丁：already 命中则视为已打过。"""
    if not os.path.exists(path):
        print(f'  !! 找不到 {path}')
        return False
    text = read(path)
    if already and already in text:
        print(f'  = {label} 已打过补丁，跳过')
        return True
    new, n = re.subn(pattern, repl, text, count=1)
    if n == 0:
        print(f'  !! {label}: 未匹配')
        return False
    write(path, new, dry)
    print(f'  + {label}')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--dict', default='translations/zh-CN.json')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    root = os.path.abspath(args.src)
    d = json.load(open(args.dict, encoding='utf-8'))
    dry = args.dry_run

    guard = os.path.join(root, 'alvr', 'session', 'src', 'settings.rs')
    if not os.path.exists(guard):
        print(f'! {root} 不像 ALVR 源码树')
        sys.exit(1)

    print(f'词表: paths={len(d["paths"])} helps={len(d["helps"])} '
          f'ids={len(d["ids"])} text={len(d["text"])}')

    # 1. 词表模块
    gui = os.path.join(root, 'alvr', 'gui_common')

    # 中文字体随源码一起放进去（theme.rs 用 include_bytes! 内嵌）
    here = os.path.dirname(os.path.abspath(__file__))
    font_src = os.path.join(here, '..', 'fonts', 'NotoSansSC-Subset.otf')
    font_full = os.path.join(here, '..', 'fonts', 'NotoSansSC-Regular.otf')
    font_dst = os.path.join(gui, 'resources', 'fonts', 'NotoSansSC-Subset.otf')

    # 每次打补丁都按当前词表重新裁剪，避免新增翻译引入缺字（豆腐块）
    if os.path.exists(font_full) and not dry:
        try:
            sys.path.insert(0, here)
            import font as font_tool
            n, size = font_tool.build(font_full, args.dict, font_src)
            print(f'  + 重建字体子集：{n} 个字形 / {size/1024:.0f} KB')
        except Exception as e:
            print(f'  ! 字体重建失败（沿用现有子集）: {e}')

    if os.path.exists(font_src):
        if not dry:
            os.makedirs(os.path.dirname(font_dst), exist_ok=True)
            open(font_dst, 'wb').write(open(font_src, 'rb').read())
        print(f'  + alvr/gui_common/resources/fonts/NotoSansSC-Subset.otf '
              f'({os.path.getsize(font_src)/1024:.0f} KB)')
    else:
        print(f'  !! 缺少字体 {font_src}，先跑 tools/font.py')
        sys.exit(1)

    write(os.path.join(gui, 'src', 'zh_cn.rs'), gen_table(d), dry)
    print(f'  + alvr/gui_common/src/zh_cn.rs（{len(d["paths"])} 条路径）')

    patch_file(
        os.path.join(gui, 'src', 'lib.rs'),
        [('pub mod theme;', 'pub mod theme;\npub mod zh_cn; // ' + MARK)],
        dry, 'alvr/gui_common/src/lib.rs 挂载模块')

    # 2. 字体注入
    patch_file(
        os.path.join(gui, 'src', 'theme.rs'),
        [(
            'pub fn set_theme(ctx: &Context) {\n    ctx.set_theme(ThemePreference::Dark);\n',
            'pub fn set_theme(ctx: &Context) {\n'
            '    ctx.set_theme(ThemePreference::Dark);\n\n'
            f'    // {MARK}: 注册简体中文字体（Noto Sans SC 子集，SIL OFL 1.1）\n'
            '    let mut fonts = egui::FontDefinitions::default();\n'
            '    fonts.font_data.insert(\n'
            '        "zh_cn".to_owned(),\n'
            f'        egui::FontData::from_static(include_bytes!("{FONT_REL}")).into(),\n'
            '    );\n'
            '    fonts\n'
            '        .families\n'
            '        .entry(egui::FontFamily::Proportional)\n'
            '        .or_default()\n'
            '        .insert(0, "zh_cn".to_owned());\n'
            '    fonts\n'
            '        .families\n'
            '        .entry(egui::FontFamily::Monospace)\n'
            '        .or_default()\n'
            '        .push("zh_cn".to_owned());\n'
            '    ctx.set_fonts(fonts);\n',
        )],
        dry, 'alvr/gui_common/src/theme.rs 注入中文字体')

    # 3. 设置面板取词函数
    ctrl = os.path.join(root, 'alvr', 'dashboard', 'src', 'dashboard',
                        'components', 'settings_controls')
    patch_file(
        os.path.join(ctrl, 'mod.rs'),
        [(
            'pub fn f64_eq(f1: f64, f2: f64) -> bool {',
            f'// {MARK}: 按完整路径取中文名/帮助\n'
            'pub fn normalize_path(path: &str) -> &str {\n'
            '    path.strip_prefix("session_settings.")\n'
            '        .or_else(|| path.strip_prefix("settings_schema."))\n'
            '        .unwrap_or(path)\n'
            '}\n\n'
            'pub fn get_display_name_localized(\n'
            '    path: &str,\n'
            '    id: &str,\n'
            '    strings: &HashMap<String, String>,\n'
            ') -> String {\n'
            '    if let Some(zh) = alvr_gui_common::zh_cn::path_of(normalize_path(path)) {\n'
            '        return zh.to_owned();\n'
            '    }\n'
            '    let english = get_display_name(id, strings);\n'
            '    alvr_gui_common::zh_cn::tr(&english)\n'
            '}\n\n'
            'pub fn get_help_localized(\n'
            '    path: &str,\n'
            '    strings: &HashMap<String, String>,\n'
            ') -> Option<String> {\n'
            '    if let Some(zh) = alvr_gui_common::zh_cn::help_of(normalize_path(path)) {\n'
            '        return Some(zh.to_owned());\n'
            '    }\n'
            '    strings.get("help").cloned()\n'
            '}\n\n'
            'pub fn f64_eq(f1: f64, f2: f64) -> bool {',
        )],
        dry, 'settings_controls/mod.rs 取词函数')

    # 4. section：名称 / 帮助
    patch_file(
        os.path.join(ctrl, 'section.rs'),
        [(
            '                let id = entry.name;\n'
            '                let display = super::get_display_name(&id, &entry.strings);\n'
            '                let help = entry.strings.get("help").cloned();\n',
            f'                let id = entry.name;\n'
            f'                // {MARK}: 用完整路径查中文\n'
            '                let setting_path = {\n'
            '                    let prefix = alvr_packets::path_to_string(&nesting_info.path);\n'
            '                    if prefix.is_empty() {\n'
            '                        id.clone()\n'
            '                    } else {\n'
            '                        format!("{prefix}.{id}")\n'
            '                    }\n'
            '                };\n'
            '                let display =\n'
            '                    super::get_display_name_localized(&setting_path, &id, &entry.strings);\n'
            '                let help = super::get_help_localized(&setting_path, &entry.strings);\n',
        )],
        dry, 'settings_controls/section.rs 名称与帮助')

    # 5. choice：枚举选项名
    patch_file(
        os.path.join(ctrl, 'choice.rs'),
        [(
            '        let variant_labels = schema_variants\n'
            '            .iter()\n'
            '            .map(|entry| DisplayString {\n'
            '                id: entry.name.clone(),\n'
            '                display: get_display_name(&entry.name, &entry.strings),\n'
            '            })\n',
            f'        // {MARK}: 枚举选项也按完整路径查中文\n'
            '        let variant_prefix = alvr_packets::path_to_string(&nesting_info.path);\n'
            '        let variant_labels = schema_variants\n'
            '            .iter()\n'
            '            .map(|entry| {\n'
            '                let full = if variant_prefix.is_empty() {\n'
            '                    entry.name.clone()\n'
            '                } else {\n'
            '                    format!("{}.{}", variant_prefix, entry.name)\n'
            '                };\n'
            '                let display = alvr_gui_common::zh_cn::path_of(super::normalize_path(&full))\n'
            '                    .map(str::to_owned)\n'
            '                    .unwrap_or_else(|| get_display_name(&entry.name, &entry.strings));\n'
            '                DisplayString {\n'
            '                    id: entry.name.clone(),\n'
            '                    display,\n'
            '                }\n'
            '            })\n',
        )],
        dry, 'settings_controls/choice.rs 枚举选项')

    # 6. 侧边栏：类型改 String + 逐个标签查表（不同版本 emoji 不同，用正则）
    dash_mod = os.path.join(root, 'alvr/dashboard/src/dashboard/mod.rs')
    if 'tab_labels: BTreeMap<Tab, String>' not in read(dash_mod):
        patch_line(dash_mod,
                   "    tab_labels: BTreeMap<Tab, &'static str>,",
                   '    // ' + MARK + ': 改存 String 以便查表\n'
                   '    tab_labels: BTreeMap<Tab, String>,',
                   dry, 'dashboard/mod.rs tab_labels 类型')
        _txt = read(dash_mod)
        _pat = r'[(]Tab::(\w+), ("[^"]+")[)]'
        _n = 0
        while re.search(_pat, _txt):
            _txt, _k = re.subn(_pat, r'(Tab::\1, alvr_gui_common::zh_cn::tr(\2))', _txt, count=1)
            if not _k:
                break
            _n += _k
        write(dash_mod, _txt, dry)
        print(f'  + dashboard/mod.rs 侧边栏标签（{_n} 个）')
        patch_line(dash_mod,
                   'ui.selectable_value(&mut self.selected_tab, *tab, *label);',
                   'ui.selectable_value(&mut self.selected_tab, *tab, label.clone());',
                   dry, 'dashboard/mod.rs 侧边栏取值1')
        patch_line(dash_mod,
                   'ui.heading(RichText::new(self.tab_labels[&self.selected_tab]).size(25.0));',
                   'ui.heading(RichText::new(self.tab_labels[&self.selected_tab].clone()).size(25.0));',
                   dry, 'dashboard/mod.rs 侧边栏取值2')

    # 7. 设置页顶层标签（Video/Audio/...）走完整路径查表
    patch_file(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/settings.rs'),
        [('                let display = super::get_display_name(&id, &entry.strings);',
          f'                // {MARK}: 顶层标签也按路径查中文\n'
          '                let display = super::get_display_name_localized(\n'
          '                    &format!("session_settings.{id}"),\n'
          '                    &id,\n'
          '                    &entry.strings,\n'
          '                );')],
        dry, 'dashboard/components/settings.rs 顶层标签')

    # 8. 预设页：只翻译每行标题，选项值保持英文（选项名参与状态写回，不能动）
    patch_file(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs'),
        [('        strings.insert("display_name".into(), schema.name.clone());',
          f'        // {MARK}: 预设标题查表；选项名不翻译，避免写回 session 时对不上\n'
          '        strings.insert(\n'
          '            "display_name".into(),\n'
          '            alvr_gui_common::zh_cn::tr(&schema.name),\n'
          '        );')],
        dry, 'presets/higher_order_choice.rs 预设标题')

    # 8.5 底部通知提示
    patch_file(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/notifications.rs'),
        [('                    .map(|s| format!("Tip: {s}"));',
          f'                    // {MARK}: 底部提示按原文查表\n'
          '                    .map(|s| {\n'
          '                        format!(\n'
          '                            "{}：{}",\n'
          '                            alvr_gui_common::zh_cn::tr("Tip"),\n'
          '                            alvr_gui_common::zh_cn::tr(*s)\n'
          '                        )\n'
          '                    });')],
        dry, 'dashboard/components/notifications.rs 底部提示')

    # 8.6 黄色警示框（notice）
    patch_line(
        os.path.join(ctrl, 'section.rs'),
        '                let notice = entry.strings.get("notice").cloned();',
        '                let notice = entry.strings\n'
        '                    .get("notice")\n'
        '                    .map(|s| alvr_gui_common::zh_cn::tr(s));',
        dry, 'settings_controls/section.rs 警示框')

    # 8.7 设备页「需要 SteamVR」提示条（跨行字符串）
    patch_line(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/devices.rs'),
        '                                    "ALVR requires running SteamVR! \\\n'
        '                                    Devices will not be discovered or connected.",',
        '                                    alvr_gui_common::zh_cn::tr(\n'
        '                                        "ALVR requires running SteamVR! '
        'Devices will not be discovered or connected.",\n'
        '                                    ),',
        dry, 'devices.rs SteamVR 提示条')

    # 8.8 预设下拉选项：只翻显示文字，name 仍是英文（写回 session 的 variant key）
    patch_line(
        os.path.join(root, 'alvr/dashboard/src/dashboard/components/settings_controls/presets/higher_order_choice.rs'),
        '                            strings: [("display_name".into(), option.display_name)]\n'
        '                                .into_iter()\n'
        '                                .collect(),',
        '                            // ALVR-CN-PATCH: 显示用中文，name 保持英文作为 variant key\n'
        '                            strings: [(\n'
        '                                "display_name".into(),\n'
        '                                alvr_gui_common::zh_cn::tr(&option.display_name),\n'
        '                            )]\n'
        '                            .into_iter()\n'
        '                            .collect(),',
        dry, 'presets/higher_order_choice.rs 选项文字')

    # 8.9 帮助文本兜底：路径查不到时按英文原文查表（覆盖预设自带的 help）
    patch_line(
        os.path.join(ctrl, 'mod.rs'),
        '    strings.get("help").cloned()\n}',
        '    strings\n'
        '        .get("help")\n'
        '        .map(|h| alvr_gui_common::zh_cn::tr(h))\n'
        '}',
        dry, 'settings_controls/mod.rs 帮助兜底')

    # 10.1 头显端 HUD 文案（client_core）：与常量比较，避免复制易错的原文
    patch_file(
        os.path.join(root, 'alvr/client_core/src/connection.rs'),
        [('fn set_hud_message(event_queue: &Mutex<VecDeque<ClientCoreEvent>>, message: &str) {\n'
          '    let message = format!(\n'
          '        "ALVR v{}\\nhostname: {}\\nIP: {}\\n\\n{message}",\n'
          '        *ALVR_VERSION,\n'
          '        Config::load().hostname,\n'
          '        alvr_system_info::local_ip(),\n'
          '    );\n',
          f'// {MARK}: HUD 文案中文（常量保持英文，日志不受影响）\n'
          'fn zh_hud(message: &str) -> &str {\n'
          '    if message == INITIAL_MESSAGE {\n'
          '        return "正在搜索串流端…\\n请在电脑上打开 ALVR，然后点击设备条目右侧的「信任」";\n'
          '    }\n'
          '    if message == SUCCESS_CONNECT_MESSAGE {\n'
          '        return "连接成功！\\n请稍候…";\n'
          '    }\n'
          '    if message == STREAM_STARTING_MESSAGE {\n'
          '        return "串流即将开始\\n请稍候…";\n'
          '    }\n'
          '    if message == SERVER_RESTART_MESSAGE {\n'
          '        return "串流端正在重启\\n请稍候…";\n'
          '    }\n'
          '    if message == SERVER_DISCONNECTED_MESSAGE {\n'
          '        return "串流端已断开连接。";\n'
          '    }\n'
          '    if message == CONNECTION_TIMEOUT_MESSAGE {\n'
          '        return "连接超时。";\n'
          '    }\n'
          '    message\n'
          '}\n'
          '\n'
          'fn set_hud_message(event_queue: &Mutex<VecDeque<ClientCoreEvent>>, message: &str) {\n'
          '    let message = format!(\n'
          '        "ALVR v{}\\n主机名：{}\\nIP：{}\\n\\n{}",\n'
          '        *ALVR_VERSION,\n'
          '        Config::load().hostname,\n'
          '        alvr_system_info::local_ip(),\n'
          '        zh_hud(message),\n'
          '    );\n'),
         ('let message = format!("Connection error:\\n{e}\\nCheck the PC for more details");',
          f'let message = format!("连接错误：\\n{{e}}\\n详细原因请查看电脑端面板"); // {MARK}')],
        dry, 'client_core/connection.rs HUD 文案')

    # 10.2 头显端 lobby 渲染器：追加中文字体作为回退
    graphics = os.path.join(root, 'alvr', 'graphics')
    hud_font = os.path.join(graphics, 'resources', 'NotoSansSC-HUD.otf')
    if os.path.exists(font_src) and not dry:
        os.makedirs(os.path.dirname(hud_font), exist_ok=True)
        open(hud_font, 'wb').write(open(font_src, 'rb').read())
    patch_file(
        os.path.join(graphics, 'src', 'lobby.rs'),
        [('        let ubuntu_font =\n'
          '            FontRef::try_from_slice(include_bytes!("../resources/Ubuntu-Medium.ttf")).unwrap();\n',
          '        let ubuntu_font =\n'
          '            FontRef::try_from_slice(include_bytes!("../resources/Ubuntu-Medium.ttf")).unwrap();\n'
          f'        // {MARK}: 中文字体作为回退（Ubuntu 没有汉字）\n'
          '        let cjk_font =\n'
          '            FontRef::try_from_slice(include_bytes!("../resources/NotoSansSC-HUD.otf")).unwrap();\n'),
         ('                &[&ubuntu_font],', '                &[&ubuntu_font, &cjk_font],'),
         ('        let scaled_font = ubuntu_font.as_scaled(FONT_SIZE);',
          '        let scaled_latin = ubuntu_font.as_scaled(FONT_SIZE);\n'
          '        let scaled_cjk = cjk_font.as_scaled(FONT_SIZE);'),
         ('            if let Some(outlined) = scaled_font.outline_glyph(section_glyph.glyph) {',
          '            let outlined = if section_glyph.font_id == FontId(0) {\n'
          '                scaled_latin.outline_glyph(section_glyph.glyph)\n'
          '            } else {\n'
          '                scaled_cjk.outline_glyph(section_glyph.glyph)\n'
          '            };\n'
          '            if let Some(outlined) = outlined {')],
        dry, 'graphics/lobby.rs 中文字体回退')

    # 10.3 头显端的应用名
    patch_line(
        os.path.join(root, 'alvr/client_openxr/Cargo.toml'),
        'label = "ALVR"',
        'label = "ALVR 客户端" # ALVR-CN-PATCH',
        dry, 'client_openxr/Cargo.toml 应用名')

    # 11. 界面字面量
    ui_keys = sorted(d['text'], key=len, reverse=True)
    hit = 0
    for rel in ('alvr/dashboard/src', 'alvr/launcher/src'):
        for dirpath, _, files in os.walk(os.path.join(root, rel.replace('/', os.sep))):
            for f in files:
                if not f.endswith('.rs'):
                    continue
                p = os.path.join(dirpath, f)
                text = read(p)
                file_changed = 0
                new_lines = []
                for line in text.split('\n'):
                    if not UI_GATE.search(line):
                        new_lines.append(line)
                        continue
                    out = line
                    ref = '&' if HELPER_GATE.search(line) else ''
                    for k in ui_keys:
                        # 含占位符的格式串不能包 tr()，否则 format! 参数不再是字面量
                        if '{' in k or '}' in k:
                            continue
                        lit = '"' + k.replace('\\', '\\\\').replace('"', '\\"') + '"'
                        if lit not in out or ('zh_cn::tr(' + lit + ')') in out:
                            continue
                        out = out.replace(
                            lit, ref + 'alvr_gui_common::zh_cn::tr(' + lit + ')', 1)
                        file_changed += 1
                    new_lines.append(out)
                if file_changed:
                    write(p, '\n'.join(new_lines), dry)
                    relp = os.path.relpath(p, root).replace(os.sep, '/')
                    print(f'  + {relp}（{file_changed} 处文案）')
                    hit += file_changed

    print(f'界面文案共替换 {hit} 处')
    print('完成。' + ('（dry-run，未写入）' if dry else ''))


if __name__ == '__main__':
    main()
