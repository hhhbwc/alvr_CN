"""第四批词条：枚举显示名、连接页/色彩校正的字段名等。

用法：python tools/add_v4.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TDIR = os.path.join(HERE, '..', 'translations')

ADDITIONS = {
    # ---------- 枚举显示名 ----------
    'Constant': '恒定码率',
    'Adaptive': '自适应码率',
    'By index': '按索引',
    'By name (substring)': '按名称（子串匹配）',
    'HSV Chroma Key': 'HSV 抠像',
    'RGB Chroma Key': 'RGB 抠像',
    'Object Tracking': '对象追踪',
    'VRChat Body OSC': 'VRChat 身体 OSC',
    'SteamVR input 2.0': 'SteamVR 输入 2.0',
    'SteamVR Launcher': 'SteamVR 启动',
    'Power Saving': '省电',
    'Client-side foveation': '客户端注视点编码',
    'Eye-tracked foveated encoding': '眼动注视点编码',
    'Eye tracking OSC override': '眼动追踪 OSC 覆盖',
    'Allow remote dashboard access': '允许远程访问面板',
    'Allow untrusted HTTP': '允许不受信任的 HTTP',
    'DSCP (packet prio hints)': 'DSCP（包优先级提示）',
    'Extra OpenVR properties': '额外 OpenVR 属性',
    'Local OSC port': '本地 OSC 端口',
    'Map non-held controllers to SteamVR trackers': '未握持的手柄映射到 SteamVR 追踪器',
    'Open and close SteamVR automatically': '自动开关 SteamVR',
    'Center region size': '中心区域大小',
    'Center shift': '中心偏移',
    'Receive size': '接收缓冲区大小',
    'Send size': '发送缓冲区大小',

    # ---------- 连接页 / 有线连接字段 ----------
    'Device': '设备',
    'Devices': '设备',
    'Host': '主机',
    'Port': '端口',
    'Mode': '模式',
    'Type': '类型',
    'Value': '数值',
    'Width': '宽度',
    'Height': '高度',
    'Level': '级别',
    'Publish': '发布',
    'Sink': '输出端',
    'Source': '来源',
    'Sources': '来源',
    'Sockets': '套接字',
    'Tracked': '已追踪',
    'Class': '类别',
    'Connection': '连接',

    # ---------- 色彩校正 / 画面 ----------
    'Brightness': '亮度',
    'Contrast': '对比度',
    'Gamma': '伽马',
    'Saturation': '饱和度',
    'Sharpening': '锐化',
    'Feathering': '羽化',
    'Deviation': '偏差',
    'Threshold': '阈值',
    'Red': '红',
    'Green': '绿',
    'Blue': '蓝',
    'Encoder': '编码端',
    'Decoder': '解码端',
    'Buffering': '缓冲',
    'Haptics': '震动',
    'Predict': '预测',
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
