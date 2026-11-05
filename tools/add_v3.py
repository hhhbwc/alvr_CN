"""第三批词条：v20 独有措辞的设置帮助、枚举名、提示等（由运行时缺词追踪实测得出）。

用法：python tools/add_v3.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TDIR = os.path.join(HERE, '..', 'translations')

ADDITIONS = {
    # ---------- 设置项名称（由字段名自动生成，v20 路径与 v21 不同）----------
    'Activation delay': '激活延迟',
    'Deactivation delay': '取消延迟',
    'Amplitude curve': '振幅曲线',
    'Angular velocity cutoff': '角速度阈值',
    'Linear velocity cutoff': '线速度阈值',
    'Click threshold': '点击阈值',
    'Force threshold': '强制阈值',
    'Touch threshold': '触摸阈值',
    'Distance threshold': '距离阈值',
    'Edge threshold': '边缘阈值',
    'Edge direction': '边缘方向',
    'Edge sharpness': '边缘锐度',
    'Drop probability': '丢包率',
    'Intensity multiplier': '强度倍率',
    'Saturation multiplier': '饱和度倍率',
    'Max saturation multiplier': '最大饱和度倍率',
    'Latency overstep multiplier': '延迟超限倍率',
    'Max level': '最大级别',
    'Super sampling': '超采样',
    'Upscale factor': '放大倍率',
    'View height': '视野高度',
    'Serial number': '序列号',
    'Repeat delay': '重复延迟',
    'Force enable': '强制启用',
    'Force enable on smartphone clients': '在手机客户端上强制启用',
    'Emulation mode': '模拟模式',
    'Multimodal tracking': '多模态追踪',
    'Hand skeleton': '手部骨骼',
    'Premultiplied alpha': '预乘 Alpha',
    'Orientation correction': '朝向校正',
    'Prompt calibration on start': '启动时提示校准',
    'Hide spammy events': '隐藏高频事件',
    'Hide while version': '隐藏直到新版本',
    'High accuracy': '高精度',
    'Only touch': '仅触摸',
    'Auto trust clients': '自动信任客户端',
    'Button set': '按键组',
    'Button mappings': '按键绑定',
    'Button mapping config': '按键映射配置',
    'Extra openvr props': '额外 OpenVR 属性',
    'Joystick deadzone': '摇杆死区',
    'Joystick range': '摇杆范围',
    'Joystick offset horizontal': '摇杆水平偏移',
    'Joystick offset vertical': '摇杆垂直偏移',
    'Curl touch distance': '弯曲触摸距离',
    'Curl trigger distance': '弯曲扳机距离',
    'Pinch touch distance': '捏合触摸距离',
    'Pinch trigger distance': '捏合扳机距离',
    'Maximum bitrate': '最大码率',
    'Minimum bitrate': '最小码率',
    'Maximum decoder latency': '最大解码延迟',
    'Maximum network latency': '最大网络延迟',
    'Value start min': '数值起点最小值',
    'Value start max': '数值起点最大值',
    'Value end min': '数值终点最小值',
    'Value end max': '数值终点最大值',
    'Hue start min': '色相起点最小值',
    'Hue start max': '色相起点最大值',
    'Hue end min': '色相终点最小值',
    'Hue end max': '色相终点最大值',
    'Saturation start min': '饱和度起点最小值',
    'Saturation start max': '饱和度起点最大值',
    'Saturation end min': '饱和度终点最小值',
    'Saturation end max': '饱和度终点最大值',
    'Left controller position offset': '左手柄位置偏移',
    'Left controller rotation offset': '左手柄旋转偏移',
    'Left hand tracking position offset': '左手手部追踪位置偏移',
    'Left hand tracking rotation offset': '左手手部追踪旋转偏移',
    'Right controller offset is mirrored horizontally': '右手柄偏移会水平镜像',
    'List of OpenXR-syle paths': 'OpenXR 风格路径列表',
    'latency overstep': '延迟超限',

    # ---------- 枚举变体名 ----------
    'Body tracking bd': '身体追踪（BD）',
    'Body tracking fb': '身体追踪（Meta）',
    'Eye expressions htc': '眼部表情（HTC）',
    'Lip expressions htc': '嘴部表情（HTC）',
    'Eye tracking fb': '眼动追踪（Meta）',
    'Face tracking fb': '面部追踪（Meta）',
    'Face tracking pico': '面部追踪（Pico）',
    'Full body': '全身',
    'Client core': '客户端核心',
    'Client gfx': '客户端图形',
    'Client impl': '客户端实现',
    'Server core': '服务端核心',
    'Server gfx': '服务端图形',
    'Server impl': '服务端实现',
    'Steamvr input 2 0': 'SteamVR 输入 2.0',
    'VRChat Eye OSC': 'VRChat 眼部 OSC',

    # ---------- 帮助文案 ----------
    'Allow untrusted clients to connect without confirmation. This is not recommended for security reasons.':
        '允许未受信任的客户端在无需确认的情况下连接。出于安全原因，不建议开启。',
    'Allowed percentage of frame interval to allocate for video encoding':
        '允许分配给视频编码的帧间隔百分比',
    'Allows the encoder to perform pre-analysis the motion of the video and use the information for better encoding':
        '允许编码器对画面运动做预分析，并利用该信息提升编码质量',
    'Async Compute is currently broken in SteamVR, keep disabled. ONLY FOR TESTING.':
        'SteamVR 中的异步计算目前有问题，请保持关闭。仅供测试。',
    'Async reprojection only works if you can always hit at least half of your refresh rate.':
        '异步重投影仅在帧率始终能达到刷新率一半以上时才有效。',
    'Because of runtime limitations, this option is ignored when body tracking is active.':
        '受运行时限制，启用身体追踪时该选项会被忽略。',
    'CABAC produces better compression but it\'s significantly slower and may lead to runaway latency':
        'CABAC 压缩率更好，但明显更慢，可能导致延迟失控',
    'CAVLC algorithm is recommended.': '建议使用 CAVLC 算法。',
    'CBR: Constant BitRate mode. This is recommended.': 'CBR：固定码率模式。推荐使用。',
    'Controls how much the bitrate is reduced when the decoder latency goes above the threshold':
        '控制解码延迟超过阈值时码率的下降幅度',
    'Currently there is a bug where the decoder latency keeps rising when above a certain bitrate':
        '目前存在一个问题：码率超过某个值后解码延迟会持续上升',
    'Currently this cannot be reliably estimated automatically. The correct value should be 2 but 3 is default for smoother tracking at the cost of slight lag.':
        '目前无法可靠地自动估算。正确值应为 2，默认 3 可让追踪更平滑，代价是轻微延迟。',
    'Dimensional resolution multiplier, high values will cause performance issues with weaker headset hardware or higher resolutions':
        '分辨率倍率。数值过高会在头显性能较弱或分辨率较高时造成性能问题',
    'Disabled: the playspace orientation is determined by the room-scale guardian setup.':
        '禁用：游玩空间朝向由房间级边界设置决定。',
    'Disabled: the playspace origin is determined by the room-scale guardian setup.':
        '禁用：游玩空间原点由房间级边界设置决定。',
    'Disabling foveated encoding may result in significantly higher encode/decode times and stuttering, or even crashing.':
        '关闭注视点编码会显著增加编解码耗时并造成卡顿，甚至崩溃。',
    'Does not work with the "Reduce color banding" option, requires enabling "Use preproc"':
        '与「减少色带」选项不兼容，需要开启「使用预处理」',
    'Enables high motion quality boost mode.': '启用高动态画质增强模式。',
    'Enables pre-analysis during encoding. This will likely result in reduced performance, but may increase quality.':
        '编码时启用预分析。可能降低性能，但能提升画质。',
    'Enabling this allows using hand gestures to emulate controller inputs.':
        '启用后可用手势模拟手柄输入。',
    'Enabling this passes skeletal hand data (finger tracking) to SteamVR.':
        '启用后会把手部骨骼数据（手指追踪）传给 SteamVR。',
    'Enabling this will adapt transparency based on the brightness of each pixel.':
        '启用后会根据每个像素的亮度调整透明度。',
    'Enabling this will use separate tracker objects with the full skeletal tracking level when hand tracking is detected. This is required for VRChat hand tracking.':
        '启用后，检测到手部追踪时会使用独立的追踪器对象并采用完整骨骼级别。VRChat 手部追踪需要此项。',
    'Higher values make the controllers track smoother.': '数值越高，手柄追踪越平滑。',
    'How close the tips of your fingers need to be to register a pinch click.':
        '指尖需要多近才能触发捏合点击。',
    'How close to your palm the tips of your fingers need to be to register a curl click.':
        '指尖到手掌多近才能触发弯曲点击。',
    'How close to your palm the tips of your fingers need to be to start registering a trigger pull.':
        '指尖到手掌多近才开始识别扳机拉动。',
    'How close together the tips of your fingers need to be to start registering a pinch trigger pull.':
        '指尖需要多接近才开始识别捏合扳机拉动。',
    'How long the after the gesture has been deactivated before it can be activated again.':
        '手势取消后需等待多久才能再次激活。',
    'How long the gesture must be continuously held before it is activated.':
        '手势需持续保持多久才会被激活。',
    'How long the gesture must be continuously released before it is deactivated.':
        '手势需持续松开多久才会被取消。',
    'If on_connect.bat exists alongside session.json, it will be run on headset connect. Env var ACTION will be set to `connect`.':
        '如果 session.json 同目录下存在 on_connect.bat，头显连接时会执行它，环境变量 ACTION 会被设为 `connect`。',
    'If on_disconnect.bat exists alongside session.json, it will be run on headset disconnect. Env var ACTION will be set to `disconnect`.':
        '如果 session.json 同目录下存在 on_disconnect.bat，头显断开时会执行它，环境变量 ACTION 会被设为 `disconnect`。',
    'If the client has no preference, enables compositing VR layers to an RGBA float16 framebuffer, and doing sRGB/YUV conversions in shader code.':
        '客户端没有指定偏好时，把 VR 图层合成到 RGBA float16 帧缓冲，并在着色器里完成 sRGB/YUV 转换。',
    'If the client, server or the network discarded one packet, discard packets until a IDR packet is found.':
        '如果客户端、服务端或网络丢弃了一个数据包，则持续丢弃数据直到收到 IDR 帧。',
    'If the framerate changes more than this factor, trigger a parameters update':
        '帧率变化超过该倍数时触发参数更新',
    'If trackers have not been calibrated before, the calibration process will start after you connect to the streamer.':
        '如果追踪器之前没有校准过，连接串流端后会开始校准流程。',
    'If you want to reduce the amount of pixelation on the edges, increase the center region width and height':
        '想减少边缘的像素化，请调大中心区域的宽和高',
    'Improve clarity of high contrast edges and counteract blur.':
        '提升高对比度边缘的清晰度，抵消模糊。',
    'Improves accuracy of the tracking at the cost of higher latency.':
        '提升追踪精度，代价是更高的延迟。',
    'Improves visual quality by using the edge direction to upscale at a slight performance loss':
        '利用边缘方向进行放大来提升画质，性能略有损失',
    'In CBR mode, this makes sure the bitrate does not fall below the assigned value. This is mostly useful for debugging.':
        '在 CBR 模式下确保码率不低于设定值。主要用于调试。',
    'It\'s recommended to set Tracking Mode to Full-Body Tracking in Motion Tracker app settings on your Pico headset.':
        '建议在 Pico 头显的 Motion Tracker 应用里把追踪模式设为全身追踪。',
    'Local floor: the origin is on the floor and resets when long pressing the oculus button.':
        '本地地面：原点在地面，长按 Oculus 键时重置。',
    'Local: the origin resets when long pressing the oculus button, and is calculated as an offset from the current head position.':
        '本地：长按 Oculus 键时重置原点，并以当前头部位置为偏移计算。',
    'Number of consecutive frames above the threshold to trigger a bitrate reduction':
        '连续超过阈值的帧数达到该值后触发码率下调',
    'Percentage of network bandwidth to allocate for video transmission':
        '分配给视频传输的网络带宽百分比',
    'Predict hand skeleton to make it less floaty. It may make hands too jittery.':
        '预测手部骨骼以减少飘忽感，但可能让手部抖动更明显。',
    'Reduce flicker for high contrast edges.': '减少高对比度边缘的闪烁。',
    'Sets the encoder to encode full range RGB (0-255) instead of limited/video range RGB (16-235), if the client has no preference':
        '客户端没有指定偏好时，让编码器使用全范围 RGB（0-255）而不是有限/视频范围 RGB（16-235）',
    'Spatial: Helps reduce color banding, but high-complexity scenes might look worse.':
        '空间：有助于减少色带，但复杂场景画质可能变差。',
    'TCP: Slower than UDP, but more stable. Pick this if you experience video or audio stutters with UDP.':
        'TCP：比 UDP 慢但更稳定。用 UDP 时画面或声音卡顿时可选它。',
    'Technically, this is the time (counted in frames) between pose submitted to SteamVR and the corresponding virtual vsync happens.':
        '严格来说，是指姿态提交给 SteamVR 到对应虚拟垂直同步发生之间的时间（按帧计）。',
    'Temporal: Helps improve overall encoding quality, very small trade-off in speed.':
        '时间：有助于提升整体编码质量，速度损失很小。',
    'The radius of motion of the joystick. The joystick can be controlled if the thumb is within 2x this range.':
        '摇杆的运动半径。拇指处于该范围的 2 倍以内时可控制摇杆。',
    'The server discards video packets if it can\'t push them to the network.':
        '当服务端无法把视频包推送到网络时会丢弃它们。',
    'The server will override the headset client\'s preference for 10-bit encoding.':
        '服务端会覆盖头显客户端的 10 位编码偏好。',
    'The server will override the headset client\'s preference for HDR.':
        '服务端会覆盖头显客户端的 HDR 偏好。',
    'The server will override the headset client\'s preference for encoding gamma.':
        '服务端会覆盖头显客户端的编码伽马偏好。',
    'The server will override the headset client\'s preference for full range color.':
        '服务端会覆盖头显客户端的全范围色彩偏好。',
    'The threshold is applied per-channel': '该阈值按通道分别应用',
    'This could happen on TCP. A IDR frame is requested in this case.':
        '在 TCP 下可能出现。此时会请求一个 IDR 帧。',
    'This device is set in SteamVR as the default microphone':
        '该设备会在 SteamVR 中被设为默认麦克风',
    'This device is used by ALVR to output microphone audio':
        'ALVR 使用该设备输出麦克风音频',
    'This is a similar effect to AR glasses.': '效果类似 AR 眼镜。',
    'This works only on Windows. It shouldn\'t be disabled except in certain circumstances when you know the VR game will not meet the target framerate.':
        '仅在 Windows 上有效。除非你确定 VR 游戏达不到目标帧率，否则不要关闭。',
    'Tilted: the world gets tilted when long pressing the oculus button. This is useful for using VR while laying down.':
        '倾斜：长按 Oculus 键时世界会倾斜，适合躺着玩 VR。',
    'To be able to use the microphone on Windows, you need to install Virtual Audio Cable':
        '要在 Windows 上使用麦克风，需要安装 Virtual Audio Cable',
    'Track hand skeleton while holding controllers. This will reduce hand tracking frequency to 30Hz.':
        '握着手柄时仍追踪手部骨骼。这会把手指追踪频率降到 30Hz。',
    'Turn this off to temporarily pause sending data.': '关闭可暂时停止发送数据。',
    'Turn this off to temporarily pause tracking.': '关闭可暂时停止追踪。',
    'Turning this off will make the controllers appear powered off.': '关闭后手柄会显示为已关机。',
    'UDP: Faster, but less stable than TCP. Try this if your network is well optimized and free of interference.':
        'UDP：比 TCP 快但稳定性差。网络质量好、干扰少时可用。',
    'Useful when the input resolution is high compared to the headset display':
        '输入分辨率高于头显屏幕时有用',
    'Useful when the input resolution is low compared to the headset display':
        '输入分辨率低于头显屏幕时有用',
    'VBR: Variable BitRate mode. Not commended because it may throw off the adaptive bitrate algorithm. This is only supported on Windows and only with AMD/Nvidia GPUs':
        'VBR：可变码率模式。不推荐，可能干扰自适应码率算法。仅 Windows 支持，且只适用于 AMD/NVIDIA 显卡',
    'Wether ALVR should try to automatically launch the client when establishing a wired connection.':
        '建立有线连接时，ALVR 是否尝试自动启动客户端。',
    'When the decoder latency goes above this threshold, the bitrate will be reduced':
        '解码延迟超过该阈值时会下调码率',
    'Which release type of client should ALVR look for when establishing a wired connection.':
        '建立有线连接时 ALVR 应查找哪种发行版本的客户端。',
    'Yaw: the forward direction is reset when long pressing the oculus button.':
        '偏航：长按 Oculus 键时重置前方朝向。',
}


def main():
    path = os.path.join(TDIR, 'extra.json')
    d = json.load(open(path, encoding='utf-8'))
    before = len(d)
    added = sum(1 for k in ADDITIONS if k not in d)
    d.update(ADDITIONS)
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'extra.json: {before} -> {len(d)}（新增 {added} 条）')


if __name__ == '__main__':
    main()
