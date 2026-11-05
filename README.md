# ALVR 简体中文汉化

把 [ALVR](https://github.com/alvr-org/ALVR)（PC 端面板 + 头显端 HUD）完整汉化，**保持与官方版本一一对应**，不改动串流协议、不影响与官方客户端的互通。

## 下载

| 版本 | 说明 | 串流端（PC） | 头显端（APK） |
|---|---|---|---|
| **v20.14.1-cn** | 官方**最新正式版**，稳定，推荐日常使用 | 见 Releases | 见 Releases |
| **v21.0.0-dev14-cn** | 官方开发中的 v21（nightly），功能新但可能有 bug | 见 Releases | 见 Releases |

> ⚠️ **串流端和头显端必须用同一版本**。v20 的串流端配 v21 的客户端会握手失败（ALVR 的协议绑定大版本号）。

## 安装

### PC 端

1. 解压 `alvr_streamer_windows_zh-*.zip` 到任意目录（路径别有中文）；
2. 双击 `ALVR Dashboard.exe`；
3. 首次使用进「安装」页 → 「注册 ALVR 驱动」→ 「添加防火墙规则」；
4. SteamVR 需要单独安装。

### 头显端（Pico / Quest）

```bash
adb uninstall alvr.client.dev        # 因为签名与官方不同，必须先卸载官方版
adb install -r alvr_client_android_zh-*.apk
```

打开头显里的「**ALVR 客户端**」，PC 面板会出现待信任的设备，点「信任」即可。

## 汉化了什么

- 侧边栏、所有设置项名称、帮助提示、下拉选项
- 「预设」页的档位名（`中（宽 4288）`、`速度优先/均衡/画质优先` 等）
- 黄色警示框、底部轮换提示、安装页按钮
- 头显里的 HUD：`正在搜索串流端…` / `连接成功！` / `串流端已断开连接。` 等
- APK 显示名：**ALVR 客户端**

**保留英文的部分**：`H264/HEVC/AV1`、`60Hz/72Hz` 这类标准写法，`VoiceMeeter/VB Cable` 等软件专名，以及运行日志（方便对照上游 issue）。

## 自己编译

```bash
git clone --depth 1 --branch v20.14.1 https://github.com/alvr-org/ALVR.git alvr-src   # 或 v21 用 master
cd alvr-src

python ../tools/catalog.py  --src . --out ../catalog.json
python ../tools/build_dict.py --catalog ../catalog.json --dir ../translations
python ../tools/apply.py    --src . --dict ../translations/zh-CN.json
python ../tools/verify.py
```

Windows 编译还需要：rustup、VS2022「使用 C++ 的桌面开发」+ **ATL 组件**、LLVM（只要 `libclang.dll`）。
`cargo xtask prepare-deps --platform windows --ci` + `cargo xtask build-streamer --release --gpl`。

细节见 [docs/汉化实现.md](docs/汉化实现.md)。

## 版本跟进

词表按「完整路径 / 英文原文」索引，升级 ALVR 后重跑一遍脚本即可，新增条目会在
`build_dict.py` 的输出里列出来，补翻译后重新打包。

## 许可

- 补丁与词表：跟随 ALVR，MIT
- 内嵌字体：Noto Sans SC，SIL Open Font License 1.1
