"""补充第二批词条：向导、统计页、关于/调试/通知、预设帮助、v20 独有的底部提示等。

用法：python tools/add_v2.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TDIR = os.path.join(HERE, '..', 'translations')

ADDITIONS = {
    # ---------- 侧边栏（v20 用 ⚙，v21 用 🔧）----------
    '⚙  Settings': '⚙  设置',

    # ---------- 设置向导 ----------
    'This setup wizard will help you setup ALVR.': '本向导将帮你完成 ALVR 的初始配置。',
    'It is recommended to reset your settings everytime you update ALVR.':
        '建议每次更新 ALVR 后都重置一次设置。',
    'Hardware requirements': '硬件要求',
    'Software requirements': '软件要求',
    'Firewall': '防火墙',
    'Recommendations': '使用建议',
    'Finished': '完成',
    'Back': '返回',
    'Unsupported OS': '不支持的操作系统',
    'ALVR requires a dedicated and recent graphics card. Low-end Intel integrated graphics may fail to work.\nMake sure you have at least one output audio device.':
        'ALVR 需要一块独立且较新的显卡。低端 Intel 核显可能无法正常工作。\n请确保至少有一个可用的音频输出设备。',
    'To stream the headset microphone on Windows you need to install Virtual Audio Cable, VB-Cable, Voicemeeter':
        '要在 Windows 上串流头显麦克风，需安装 Virtual Audio Cable、VB-Cable 或 Voicemeeter',
    'You need the PipeWire (0.3.49+ version) audio system to be able to stream audio and use microphone.':
        '要串流音频并使用麦克风，需要 PipeWire 音频系统（0.3.49 及以上版本）。',
    'To communicate with the headset, some firewall rules need to be set.\nThis requires administrator rights!':
        '要与头显通信，需要添加一些防火墙规则。\n此操作需要管理员权限！',
    'ALVR supports multiple types of PC hardware and headsets but not all might work correctly with default settings. Please try tweaking different settings like resolution, bitrate, encoder and others if your ALVR experience is not optimal.':
        'ALVR 支持多种 PC 硬件与头显，但并非所有组合在默认设置下都能正常工作。'
        '如果体验不理想，可以试着调整分辨率、码率、编码器等设置。',
    'You can always restart this setup wizard from the "Installation" tab on the left.':
        '之后随时可以从左侧「安装」页重新运行本向导。',

    # ---------- 统计页 ----------
    'Motion to Photon Latency': '动显延迟',
    'Client System (not ALVR latency)': '客户端系统（非 ALVR 延迟）',
    'Client App Compositor': '客户端应用合成',
    'Game Render (not ALVR latency)': '游戏渲染（非 ALVR 延迟）',
    'Bitrate and Throughput': '码率与吞吐量',
    'Initial calculated throughput': '初始计算吞吐量',
    'Encoder latency limiter': '编码延迟限制值',
    'Network latency limiter': '网络延迟限制值',
    'Decoder latency limiter': '解码延迟限制值',
    'Manual max throughput': '手动最大吞吐量',
    'Manual min throughput': '手动最小吞吐量',
    'Requested bitrate': '请求码率',
    'Recorded throughput': '实测吞吐量',
    'Recorded bitrate': '实测码率',
    'Note: throughput is the peak bitrate, packet_size/network_latency.':
        '说明：吞吐量指峰值码率，即 包大小/网络延迟。',
    'Total packets lost:': '累计丢包：',

    # ---------- 关于 / 调试 / 设备 / 通知 ----------
    'Visit us on GitHub': '在 GitHub 上查看我们',
    'Join us on Discord': '加入我们的 Discord',
    'Latest release': '最新版本',
    'Donate to ALVR on Open Collective': '在 Open Collective 上支持 ALVR',
    'Capture frame': '截取画面',
    'Unknown IP': '未知 IP',
    'No new notifications': '暂无新通知',

    # ---------- 设置控件 ----------
    'Preset not applied': '未应用预设',
    'default list': '默认列表',
    'Reset to ': '重置为 ',
    'Please save your in-game progress first': '请先保存游戏进度',
    'This setting can be changed in real-time during streaming!': '该设置可在串流过程中实时修改！',
    'Changing this setting will make SteamVR restart!': '修改该设置会导致 SteamVR 重启！',

    # ---------- 预设帮助（v20 措辞与 v21 不同）----------
    'AV1 is only supported on newer gpus (AMD RX 7xxx+ , NVIDIA RTX 30xx+, Intel ARC)!':
        'AV1 仅在较新的 GPU 上受支持（AMD RX 7xxx+、NVIDIA RTX 30xx+、Intel ARC）！',
    'Disabled: hands cannot emulate buttons. Useful for using Joy-Cons or other non-native controllers.\n'
    'SteamVR Input 2.0: create separate SteamVR devices for hand tracking.\n'
    'ALVR bindings: use ALVR hand tracking button bindings. Check the wiki for help.\n':
        '禁用：手部不能模拟按键。适合搭配 Joy-Con 等非原生手柄使用。\n'
        'SteamVR Input 2.0：为手势追踪创建独立的 SteamVR 设备。\n'
        'ALVR 绑定：使用 ALVR 自带的手势按键绑定。用法见 wiki。\n',
    'SteamVR Input 2.0': 'SteamVR 输入 2.0',

    # ---------- v20 独有的底部提示（与 v21 措辞不同）----------
    'Increasing "Maximum buffering" may reduce stutters at the cost of more latency.':
        '调高「最大缓冲帧数」可以减少卡顿，但会增加延迟。',
    'If you experience "white snow" flickering, reduce the resolution to "Low" and disable "Foveated encoding".':
        '如果出现「白雪花」闪烁，把分辨率调到「低」，并关闭「注视点编码」。',
    'Increasing "Color correction"->"Sharpness" may improve the perceived image quality.':
        '调高「色彩校正 > 锐化」可以提升观感清晰度。',
    'If you have problems syncing external controllers or trackers to ALVR tracking space, add one element to "Extra openvr props", then set a custom "Tracking system name".':
        '如果外部手柄或追踪器无法与 ALVR 追踪空间对齐，在「额外 OpenVR 属性」里加一条，并设置自定义的「追踪系统名称」。',
    'ALVR supports hand tracking gestures ("Presets"->"Hand tracking interaction"->"ALVR Bindings"). Check out wiki how to use them properly: https://github.com/alvr-org/ALVR/wiki/Hand-tracking-controller-bindings.':
        'ALVR 支持手势追踪（「预设 > 手势模拟手柄 > ALVR 绑定」）。用法见 wiki：'
        'https://github.com/alvr-org/ALVR/wiki/Hand-tracking-controller-bindings',
    'If hand tracking gestures are annoying, you can disable them in "Controllers"->"Gestures". Alternatively, you can enable "Gestures"->"Only touch".':
        '如果手势操作太烦，可以在「手柄 > 手势模拟手柄」里关闭；也可以开启其中的「仅触摸」。',
    'You can fine-tune the controllers responsiveness with "Controllers"->"Prediction".':
        '可以用「手柄 > 预测」微调手柄的跟手程度。',
    'If the visual controller/hand models do not match the physical controller, you can tweak the offset in "Headset"->"Controllers"->"Left controller position/rotation offset" (affects both controllers).':
        '如果手柄或手部模型与实际手柄位置对不上，可以在「头显 > 手柄 > 左手柄位置/旋转偏移」里调整（同时影响两只手柄）。',
    'When using external trackers or controllers, you should set both "Position/Rotation recentering mode" to "Disabled".':
        '使用外部追踪器或手柄时，应把「位置/旋转居中模式」都设为「禁用」。',
    'You can enable tilt mode. Set "Position recentering mode" to "Local" and "Rotation recentering mode" to "Tilted".':
        '可以开启倾斜模式：把「位置居中模式」设为「本地」，「旋转居中模式」设为「倾斜」。',
    'If you often experience image glitching, you can trade that with stutter frames using "Avoid video glitching".':
        '如果经常出现画面撕裂，可以用「避免画面撕裂」以少量掉帧换取稳定。',
    'You can run custom commands/programs at headset connection/disconnection using the "On connect/disconnect script".':
        '可以用「连接/断开时脚本」在头显连接或断开时执行自定义命令或程序。',
    'For hacking purposes, you can enable "Log tracking", "Log button presses" and "Log haptics". You can get the data using a websocket at ws://localhost:8082/api/events':
        '做逆向调试可开启「记录追踪数据」「记录按键」「记录震动」，数据可通过 '
        'ws://localhost:8082/api/events 获取。',
    'You can quickly cycle through tips like this one by toggling "Show notification tip"':
        '切换「显示通知提示」可以快速轮换这类提示。',
    'If you want to use body trackers or other SteamVR drivers together with ALVR, set "Driver launch action" to "Unregister ALVR at shutdown"':
        '如果想同时使用身体追踪器或其他 SteamVR 驱动，把「驱动启动操作」设为「关闭时注销 ALVR」。',
    'It\'s handy to enable "Extra"->"Steamvr Launcher"->"Open and close SteamVR with dashboard"':
        '建议开启「其他 > SteamVR 启动 > 随面板开关 SteamVR」。',
    'If you want to share a video recording for reporting a bug, you can enable "Extra"->"Capture"->"Rolling video files" to limit the file size of the upload':
        '想分享录像来报 bug 时，可以开启「其他 > 录制 > 循环录像文件」限制文件大小。',
}


def main():
    path = os.path.join(TDIR, 'extra.json')
    d = json.load(open(path, encoding='utf-8'))
    before = len(d)
    added = 0
    for k, v in ADDITIONS.items():
        if k not in d:
            added += 1
        d[k] = v
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'extra.json: {before} -> {len(d)}（新增 {added}，覆盖 {len(ADDITIONS) - added}）')


if __name__ == '__main__':
    main()
