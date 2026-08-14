#!/usr/bin/env python3
"""Download the current GitHub avatar for the profile owner."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


API = "https://api.github.com/users/{login}"
TARGET = Path(__file__).resolve().parents[1] / "assets" / "avatar.png"


def fetch_json(url: str, token: str | None, user_agent: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> None:
    login = os.environ.get("GH_LOGIN")
    if not login:
        raise SystemExit("GH_LOGIN is required")

    token = os.environ.get("GITHUB_TOKEN")
    user_agent = f"{login}-profile-avatar-sync"
    profile = fetch_json(API.format(login=login), token, user_agent)
    avatar_url = profile.get("avatar_url")
    if not avatar_url:
        raise SystemExit(f"GitHub did not return an avatar URL for {login}")

    separator = "&" if "?" in avatar_url else "?"
    avatar_url = f"{avatar_url}{separator}s=1200"
    request = Request(
        avatar_url,
        headers={
            "Accept": "image/*",
            "User-Agent": user_agent,
        },
    )
    with urlopen(request, timeout=30) as response:
        image = Image.open(io.BytesIO(response.read())).convert("RGB")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    image.save(TARGET, format="PNG", optimize=True)
    print(f"downloaded {avatar_url} -> {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
