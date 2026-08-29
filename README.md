> I want to access a Node.js server behind CG-NAT remotely. No, I want to access 16,776,960 Node.js servers behind CG-NAT remotely. 

**🌐 Languages:** **English** | [中文](README.zh.md) 

<p align="center">
    <img src="iv2ray.png" alt="Insta-V2Ray Logo" width="150"/>
    <h1 style="text-align: center;">Insta-V2Ray</h1>
</p>

> ⚠️ **Warning:** This project is **not intended for use in China or Iran** to bypass the Great Firewall (GFW). It is intended for accessing locally hosted resources behind NAT.

> ⚠️ **警告：** 本项目**不适用于在没有公网环境下绕过GFW**，仅用于在没有公网的情况下访问本地服务。

> ⚠️ **هشدار:** این پروژه **برای استفاده در ایران** جهت دور زدن فیلترینگ (GFW) **در نظر گرفته نشده است** و فقط برای دسترسی به منابع میزبانی‌شده محلی پشت NAT طراحی شده است.

Insta-V2Ray is a Python-Flask full-stack application designed to create V2Ray nodes for people behind a CG-NAT or without a public IPv4 address or port-forwarding. It utilizes tunnel providers such as Cloudflare, Pinggy, Tailscale and more for tunneling WebSocket or gRPC transport V2Ray nodes behind NAT, handling TLS termination on port 443 and a a public domain name.

## Quickstart

Please refer to the [Wiki](https://github.com/vttc08/insta-v2ray/wiki) for detailed instructions for provider specific setup and binary installation.

#### [Wiki Documentation](https://github.com/vttc08/insta-v2ray/wiki)

### Bare Metal/VM/LXC

Project setup (cloning repository and installing dependencies):

```bash
git clone https://github.com/vttc08/insta-v2ray
cd insta-v2ray
pip install -r requirements.txt
# optional helper to fetch tunnel binaries
python -m helper.downloader cloudflared
python -m helper.downloader zrok
```

Python3/pip may not be available in some Linux environment. You may need to install Python/pip/venv, it's also recommended to use a virtual environment for the project.

```bash
sudo apt install python3 python3-venv # Depending on Python version, you may need to specify python3.13-venv
python3 -m venv .venv
source .venv/bin/activate
```

#### Very Quick Start

The very quick start runs the app with default configuration, including a V2Ray server configuration hardcoded in the enviromnent. It's recommended you setup your own.

```bash
sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install # Install Xray core
cp .env.example .env # Setup default environments
```

The `xray.json` file in an example server configuration for VLESS+WS running on port 8080, the UUID is hardcoded, simiarly in the `.env.example` the `TUNNEL_URLS` variable has been set to the corresponding V2Ray URL. It's recommended to review the configuration. To run Xray.

```bash
xray -c xray.json &
```

Running the app:

```bash
gunicorn -b 0.0.0.0:5000 'main:app' # you can change the port accordingly
```

Once the app is running, navigate to the dashboard and login with `your_secure_api_password_here` (from `.env.example`):


[http://localhost:5000/your_secure_api_password_here/login](http://localhost:5000/your_secure_api_password_here/login)


### Docker

To be implemented later.

## Configuration

Please refer to the [Wiki](https://github.com/vttc08/insta-v2ray/wiki) for detailed configuration instructions. Below are some quickstart examples.

Configuration is done via environment variables. You can copy the `.env.example` file to `.env` and edit it to set your configuration. Ensure you set a strong password for API and subscription access.

To add your V2Ray tunnels, add the V2Ray URL format `vless://, vmess://` to the `TUNNEL_URLS` environment variable in the `.env` file, separated by commas. Currently, only VLESS and VMess protocols are supported.

### Provider binaries

Many tunnel providers rely on a companion binary. You can fetch the correct build for your platform with the helper script:

```bash
python -m helper.downloader cloudflared
python -m helper.downloader zrok --version 0.4.29  # optional specific release
```

The files are installed into the directory pointed to by `BIN_PATH` (defaults to `./bin`).

- You must use transport WebSocket or gRPC.
- You may need to use SSH tunneling or other solutions if your V2Ray URL is not on this machine or localhost.

For detailed configuration on how to setup V2Ray nodes based on requirement, please refer to the [Wiki](https://github.com/vttc08/insta-v2ray/wiki).

## Development

If you would like to contribute, please fork the repository and submit a pull request. We welcome contributions of all kinds such as bug fixes, new features, frontend and provider support.

### Implementing your own provider

If you would like to implement your own provider, please refer to the `tunnels` directory for existing implementations. The file in `tunnels/provider.py` is a template for implementing your own provider, copy the template and follow the instructions accordingly. You can also refer to the existing providers.

You can use the help of ChatGPT or other AI tools to help you implement your own provider, example of ChatGPT conversation here.

https://chatgpt.com/share/6892d752-9ca8-800b-91b7-d9882794ec1c