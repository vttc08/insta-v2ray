> 我想远程访问位于 CG-NAT 后面的 Node.js 服务器。不，我想远程访问 16,776,960 台位于 CG-NAT 后面的 Node.js 服务器。

**🌐 语言版本:** [English](README.md) | **中文**

<p align="center">
    <img src="iv2ray.png" alt="Insta-V2Ray Logo" width="150"/>
    <h1 style="text-align: center;">Insta-V2Ray</h1>
</p>

> ⚠️ **警告：** 本项目**不适用于在中国或伊朗**绕过防火长城 (GFW)。它仅用于访问 NAT 后面的本地托管资源。

> ⚠️ **Warning:** This project is **not intended for use in China or Iran** to bypass the Great Firewall (GFW). It is intended for accessing locally hosted resources behind NAT.

> ⚠️ **هشدار:** این پروژه **برای استفاده در ایران** جهت دور زدن فیلترینگ (GFW) **در نظر گرفته نشده است** و فقط برای دسترسی به منابع میزبانی‌شده محلی پشت NAT طراحی شده است.

Insta-V2Ray 是一个 Python-Flask 全栈应用程序，专为那些位于 CG-NAT 后面或没有公共 IPv4 地址或端口转发的用户设计，用于创建 V2Ray 节点。它利用 Cloudflare、Pinggy、Tailscale 等隧道提供商来隧道化 WebSocket 或 gRPC 传输的 V2Ray 节点，处理端口 443 上的 TLS 终端和公共域名。

## � 演示视频

[![观看演示](https://img.youtube.com/vi/VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID_HERE)

*点击上方图片观看 Insta-V2Ray 的快速演示。*

## 快速开始

请参考 Wiki 获取详细的提供商特定设置和二进制安装说明。您还需要按照特定要求创建 V2Ray 节点，推荐使用 [3x-ui](https://github.com/MHSanaei/3x-ui) 创建，详细文档可在 Wiki 中找到。

### 裸机/虚拟机/LXC

简单，只需克隆仓库，安装 Python 依赖并运行应用程序。

```bash
git clone
cd insta-v2ray
pip install -r requirements.txt
python -m helper.downloader cloudflared
python -m helper.downloader zrok
python main.py
```

### Docker

稍后实现。

## 配置

请参考 Wiki 获取详细的配置说明。以下是一些快速开始示例。

配置通过环境变量完成。您可以将 `.env.example` 文件复制为 `.env` 并编辑它来设置您的配置。确保为 API 和订阅访问设置强密码。

要添加您的 V2Ray 隧道，请将 V2Ray URL 格式 `vless://,vmess://` 添加到 `.env` 文件中的 `TUNNEL_URLS` 环境变量，用逗号分隔。目前仅支持 VLESS 和 VMess 协议。

### 隧道二进制文件

某些隧道提供商需要额外的二进制程序。可以使用该辅助脚本为当前平台下载对应版本：

```bash
python -m helper.downloader cloudflared
python -m helper.downloader zrok --version 0.4.29  # 可选指定版本
```

下载后的文件会放在 `BIN_PATH` 指定的目录（默认 `./bin`）。

- 您必须使用 WebSocket 或 gRPC 传输。
- 如果您的 V2Ray URL 不在本机或 localhost 上，您可能需要使用 SSH 隧道或其他解决方案。

有关如何根据要求设置 V2Ray 节点的详细配置，请参考 Wiki。

## 使用方法

应用程序运行后，您可以在 `http://app_host:app_port/dashboard` 访问 Web 界面。应用程序还会在 `/{your_subscription_password}/subscription` 下为 V2Ray 客户端公开订阅 URL。内置前端将允许您管理隧道节点。稍后将添加更多前端。要登录仪表板，请使用 `.env` 文件中设置的 API 密码。

如果您需要远程访问应用程序，特别是在受限网络环境中，您可能需要查阅 Wiki 获取额外的设置说明。

## 开发

如果您想贡献代码，请 fork 仓库并提交 PR。我们欢迎各种形式的贡献，如错误修复、新功能、前端和提供商支持。

### 实现您自己的提供商

如果您想实现自己的提供商，请参考 `tunnels` 目录中的现有实现。`tunnels/provider.py` 文件是实现您自己提供商的模板，复制模板并按照说明进行操作。您也可以参考现有的提供商。

您可以使用 ChatGPT 或其他 AI 工具的帮助来实现您自己的提供商，ChatGPT 对话示例如下。

https://chatgpt.com/share/6892d752-9ca8-800b-91b7-d9882794ec1c
