"""Utility helpers to download and install provider binaries.

This helper fetches latest (or specified) releases from GitHub and extracts
binaries into the configured ``BIN_PATH`` directory. The goal is to help users
quickly provision dependencies such as ``cloudflared`` or ``zrok`` without
manually visiting release pages.

Usage from the repository root::

    python -m helper.downloader cloudflared
    python -m helper.downloader zrok --version 0.4.29
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import stat
import tarfile
import zipfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from configuration import bin_path

USER_AGENT = "insta-v2ray-downloader/1.0"
GITHUB_API = "https://api.github.com/repos/{repo}/releases/{suffix}"


@dataclass
class TargetAsset:
    match: str  # substring that must appear in the asset name
    archive: str  # "binary", "zip" or "tar.gz"
    executable: str  # expected executable name in archive or final file


@dataclass
class BinaryConfig:
    repo: str  # GitHub repo in org/name form
    targets: Dict[tuple, TargetAsset]  # mapping from (os, arch) → asset meta


# Supported binaries and how to discover their release assets.
SUPPORTED_BINARIES: Dict[str, BinaryConfig] = {
    "cloudflared": BinaryConfig(
        repo="cloudflare/cloudflared",
        targets={
            ("linux", "amd64"): TargetAsset("linux-amd64", "binary", "cloudflared"),
            ("linux", "arm64"): TargetAsset("linux-arm64", "binary", "cloudflared"),
            ("darwin", "amd64"): TargetAsset("darwin-amd64.tgz", "tar.gz", "cloudflared"),
            ("darwin", "arm64"): TargetAsset("darwin-arm64.tgz", "tar.gz", "cloudflared"),
            ("windows", "amd64"): TargetAsset("windows-amd64.exe", "binary", "cloudflared.exe"),
            ("windows", "arm64"): TargetAsset("windows-arm64.exe", "binary", "cloudflared.exe"),
        },
    ),
    "zrok": BinaryConfig(
        repo="openziti/zrok",
        targets={
            ("linux", "amd64"): TargetAsset("linux_amd64.tar.gz", "tar.gz", "zrok"),
            ("linux", "arm64"): TargetAsset("linux_arm64.tar.gz", "tar.gz", "zrok"),
            ("darwin", "amd64"): TargetAsset("darwin_amd64.tar.gz", "tar.gz", "zrok"),
            ("darwin", "arm64"): TargetAsset("darwin_arm64.tar.gz", "tar.gz", "zrok"),
            ("windows", "amd64"): TargetAsset("windows_amd64.zip", "zip", "zrok.exe"),
            ("windows", "arm64"): TargetAsset("windows_arm64.zip", "zip", "zrok.exe"),
        },
    ),
}


def detect_target() -> tuple:
    """Detect the platform key used for asset lookups."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    os_key = {
        "linux": "linux",
        "darwin": "darwin",
        "windows": "windows",
    }.get(system)
    if not os_key:
        raise RuntimeError(f"Unsupported operating system: {system}")

    if machine in ("x86_64", "amd64"):
        arch_key = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch_key = "arm64"
    elif machine.startswith("armv7"):
        arch_key = "armv7"
    else:
        arch_key = machine

    return os_key, arch_key


def fetch_release(repo: str, version: Optional[str] = None) -> dict:
    """Fetch release metadata from GitHub."""
    if version:
        # Accept raw tag ("v0.4.0") or plain version ("0.4.0")
        version_tag = version if version.startswith("v") else f"v{version}"
        suffix = f"tags/{version_tag}"
    else:
        suffix = "latest"

    url = GITHUB_API.format(repo=repo, suffix=suffix)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    with urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data


def select_asset(assets: Iterable[dict], target: TargetAsset) -> dict:
    """Find the best matching asset from GitHub release assets."""
    for asset in assets:
        name = asset.get("name", "")
        if target.match in name:
            return asset
    raise RuntimeError(f"No release asset matches '{target.match}'.")


def download_file(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request) as response, open(destination, "wb") as f:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            f.write(chunk)
    return destination


def extract_archive(archive_path: Path, target: TargetAsset, destination_dir: Path) -> Path:
    """Extract only the binary from an archive."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / target.executable

    if target.archive == "tar.gz":
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                if Path(member.name).name == target.executable:
                    fileobj = archive.extractfile(member)
                    if fileobj is None:
                        break
                    with closing(fileobj) as fh:
                        _write_file(fh, destination)
                    archive_path.unlink(missing_ok=True)
                    return destination
        raise RuntimeError(f"Executable '{target.executable}' not found in tar archive.")

    if target.archive == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if Path(name).name == target.executable:
                    with archive.open(name) as fileobj:
                        _write_file(fileobj, destination)
                    archive_path.unlink(missing_ok=True)
                    return destination
        raise RuntimeError(f"Executable '{target.executable}' not found in zip archive.")

    raise RuntimeError(f"Unsupported archive type '{target.archive}'.")


def _write_file(fileobj, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with open(destination, "wb") as out:
        for chunk in iter(lambda: fileobj.read(8192), b""):
            out.write(chunk)


def install_binary(binary: str, version: Optional[str] = None, destination_dir: Optional[str] = None) -> Path:
    """Download and install a supported binary into BIN_PATH."""
    if binary not in SUPPORTED_BINARIES:
        supported = ", ".join(sorted(SUPPORTED_BINARIES))
        raise RuntimeError(f"Unknown binary '{binary}'. Supported options: {supported}")

    destination_dir = Path(destination_dir or bin_path).expanduser().resolve()
    config = SUPPORTED_BINARIES[binary]
    os_key, arch_key = detect_target()

    if (os_key, arch_key) not in config.targets:
        raise RuntimeError(f"Binary '{binary}' does not provide builds for {os_key}/{arch_key}.")

    target = config.targets[(os_key, arch_key)]
    try:
        release = fetch_release(config.repo, version)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Unable to fetch release metadata: {exc}") from exc

    asset = select_asset(release.get("assets", []), target)

    asset_url = asset.get("browser_download_url")
    if not asset_url:
        raise RuntimeError("Selected asset does not include a download URL.")

    print(f"Downloading {binary} from {asset_url}")

    file_name = asset.get("name")
    download_path = destination_dir / file_name
    download_file(asset_url, download_path)

    if target.archive == "binary":
        final_path = destination_dir / target.executable
        if final_path.exists():
            final_path.unlink()
        download_path.rename(final_path)
    else:
        final_path = extract_archive(download_path, target, destination_dir)

    _ensure_executable(final_path)
    print(f"Installed {binary} to {final_path}")
    return final_path


def _ensure_executable(path: Path) -> None:
    """Ensure the downloaded file has executable permissions."""
    current_mode = path.stat().st_mode
    path.chmod(current_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Download provider binaries into BIN_PATH.")
    parser.add_argument("binary", choices=sorted(SUPPORTED_BINARIES.keys()), help="Name of the binary to download")
    parser.add_argument("--version", help="Specific release tag to download (defaults to latest release)")
    parser.add_argument("--dest", help="Custom destination directory (defaults to BIN_PATH)")

    args = parser.parse_args(argv)
    install_binary(args.binary, version=args.version, destination_dir=args.dest)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
