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

## 快速开始

请参考 [Wiki](https://github.com/vttc08/insta-v2ray/wiki) 获取详细的提供商特定设置和二进制安装说明。

#### [Wiki 文档](https://github.com/vttc08/insta-v2ray/wiki)

### Linux/虚拟机/LXC

项目设置（克隆仓库和安装依赖）：

```bash
git clone https://github.com/vttc08/insta-v2ray
cd insta-v2ray
pip install -r requirements.txt
# 可选的辅助工具来获取隧道二进制文件
python -m helper.downloader cloudflared
python -m helper.downloader zrok
```

#### 快速开始

快速开始会以默认配置运行应用程序，包括环境中硬编码的 V2Ray 服务器配置。建议您设置自己的配置。

```bash
sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install # 安装 Xray 核心
cp .env.example .env # 设置默认环境
```

`xray.json` 文件是一个在端口 8080 上运行的 VLESS+WS 的示例服务器配置，UUID 是硬编码的，同样在 `.env.example` 中 `TUNNEL_URLS` 变量已设置为相应的 V2Ray URL。建议您检查配置。运行 Xray：

```bash
xray -c xray.json &
```

运行应用程序：

```bash
gunicorn -b 0.0.0.0:5000 'main:app' # 您可以相应地更改端口
```

应用程序运行后，导航到仪表板并使用 `your_secure_api_password_here`（来自 `.env.example`）登录：

[http://localhost:5000/your_secure_api_password_here/login](http://localhost:5000/your_secure_api_password_here/login)

### Docker

稍后实现。

## 配置

请参考 [Wiki](https://github.com/vttc08/insta-v2ray/wiki) 获取详细的配置说明。以下是一些快速开始示例。

配置通过环境变量完成。您可以将 `.env.example` 文件复制为 `.env` 并编辑它来设置您的配置。确保为 API 和订阅访问设置强密码。

要添加您的 V2Ray 隧道，请将 V2Ray URL 格式 `vless://、vmess://` 添加到 `.env` 文件中的 `TUNNEL_URLS` 环境变量，用逗号分隔。目前仅支持 VLESS 和 VMess 协议。

### 提供商二进制文件

许多隧道提供商依赖于配套的二进制文件。您可以使用辅助脚本为您的平台获取正确的构建版本：

```bash
python -m helper.downloader cloudflared
python -m helper.downloader zrok --version 0.4.29  # 可选的特定版本
```

文件安装到 `BIN_PATH` 指向的目录（默认为 `./bin`）。

- 您必须使用 WebSocket 或 gRPC 传输。
- 如果您的 V2Ray URL 不在本机或 localhost 上，您可能需要使用 SSH 隧道或其他解决方案。

有关如何根据要求设置 V2Ray 节点的详细配置，请参考 [Wiki](https://github.com/vttc08/insta-v2ray/wiki)。

## 开发

如果您想贡献代码，请 fork 仓库并提交拉取请求。我们欢迎各种形式的贡献，如错误修复、新功能、前端和提供商支持。

### 实现您自己的提供商

如果您想实现自己的提供商，请参考 `tunnels` 目录中的现有实现。`tunnels/provider.py` 文件是实现您自己提供商的模板，复制模板并按照说明进行操作。您也可以参考现有的提供商。

您可以使用 ChatGPT 或其他 AI 工具的帮助来实现您自己的提供商，ChatGPT 对话示例如下：

https://chatgpt.com/share/6892d752-9ca8-800b-91b7-d9882794ec1c