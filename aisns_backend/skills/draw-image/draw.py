"""
Draw Image Skill

Generates an image using the OpenAI-compatible images/generations API.
Reads the default LLM config from the local SQLite database to obtain
api_endpoint and api_key, then calls the image generation endpoint.

Input (stdin JSON):
  prompt   - Text description of the image to generate (required)
  size     - Image dimensions, e.g. "1024x1024" (optional, default "1024x1024")
  model    - Image generation model name (optional, default "gpt-image-1-mini")
  quality  - "low","medium","high" (optional, default "low")
  n        - Number of images (optional, default 1)

After generating the image, it is uploaded to the gofile.io public file
sharing service (cross-platform, no curl dependency) and only the public
download page URL is returned.

Output (stdout JSON):
  ok             - bool
  download_page  - Public gofile.io download page URL of the generated image
  note           - How to use the download_page URL
  error          - Error message on failure
"""

import sys
import json
import os
import re
import sqlite3
import uuid
import urllib.request
import urllib.error
import ssl
from pathlib import Path


def main():
    # Parse input params from stdin
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            _output(False, error="No input provided")
            return
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        _output(False, error=f"Invalid JSON input: {e}")
        return

    prompt = (params.get("prompt") or "").strip()
    if not prompt:
        _output(False, error="'prompt' is required")
        return

    size = (params.get("size") or "1024x1024").strip()
    model = (params.get("model") or "gpt-image-1-mini").strip()
    quality = (params.get("quality") or "low").strip()
    n = int(params.get("n") or 1)

    # Read default LLM config from database
    config = _get_default_llm_config()
    if not config:
        _output(False, error="No default LLM config found. Please set a default LLM in Settings.")
        return

    api_endpoint = (config.get("api_endpoint") or "").strip()
    api_key = (config.get("api_key") or "").strip()

    if not api_endpoint:
        _output(False, error="Default LLM config has no api_endpoint configured")
        return
    if not api_key:
        _output(False, error="Default LLM config has no api_key configured")
        return

    # Derive the images/generations endpoint from the chat completions endpoint
    images_url = _derive_images_endpoint(api_endpoint)

    # Build request body
    body = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
    }

    # Call the image generation API
    try:
        body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

        # Create SSL context that does not verify certificates (for local/dev setups)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            images_url,
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            resp_text = resp.read().decode("utf-8")

        resp_json = json.loads(resp_text)

    except urllib.error.HTTPError as e:
        resp_body = ""
        try:
            resp_body = e.read().decode("utf-8")[:1000]
        except Exception:
            pass
        _output(False, error=f"API HTTP {e.code}: {resp_body or e.reason}")
        return
    except urllib.error.URLError as e:
        _output(False, error=f"API URL error: {e.reason}")
        return
    except Exception as e:
        _output(False, error=f"API request failed: {e}")
        return

    # Extract image data from the response
    data_list = resp_json.get("data")
    if not data_list or not isinstance(data_list, list) or len(data_list) == 0:
        _output(False, error=f"Unexpected API response: {json.dumps(resp_json)[:500]}")
        return

    first_image = data_list[0]
    image_url = (first_image.get("url") or "").strip()
    b64_json = first_image.get("b64_json")
    revised_prompt = (first_image.get("revised_prompt") or "").strip()

    if not image_url and not b64_json:
        _output(False, error="API response contains neither url nor b64_json")
        return

    # Determine save directory
    project_root = Path(__file__).resolve().parent.parent.parent
    save_dir = project_root / "uploads" / "generated_images"
    save_dir.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4().hex[:16]
    filename = f"{file_id}.png"
    save_path = save_dir / filename

    # Download or decode the image
    try:
        if b64_json:
            import base64
            image_bytes = base64.b64decode(b64_json)
            with open(save_path, "wb") as f:
                f.write(image_bytes)
        elif image_url:
            img_req = urllib.request.Request(image_url, method="GET")
            img_ctx = ssl.create_default_context()
            img_ctx.check_hostname = False
            img_ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(img_req, timeout=120, context=img_ctx) as img_resp:
                with open(save_path, "wb") as f:
                    f.write(img_resp.read())
    except Exception as e:
        _output(False, error=f"Failed to save image: {e}")
        return

    # Upload the saved image to gofile.io and return only the download page URL
    try:
        download_page = _upload_to_gofile(str(save_path))
    except Exception as e:
        _output(False, error=f"Failed to upload image to gofile: {e}")
        return

    result = {
        "ok": True,
        "download_page": download_page,
        "note": "Use this URL to download the generated image.",
    }

    print(json.dumps(result, ensure_ascii=False))


def _get_default_llm_config():
    """Read the default LLM config from the SQLite database."""
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "db" / "db.sqlite"

    if not db_path.exists():
        return None

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT api_endpoint, api_key, model_name, provider "
            "FROM llm_config "
            "WHERE is_default = 1 AND is_active = 1 AND is_delete = 0 "
            "LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "api_endpoint": row["api_endpoint"],
            "api_key": row["api_key"],
            "model_name": row["model_name"],
            "provider": row["provider"],
        }
    except Exception as e:
        return None


def _derive_images_endpoint(api_endpoint):
    """
    Derive the images/generations URL from the LLM config api_endpoint.

    Common patterns:
      https://api.openai.com/v1/chat/completions -> https://api.openai.com/v1/images/generations
      https://api.openai.com/v1                   -> https://api.openai.com/v1/images/generations
      https://some-proxy.com/v1                   -> https://some-proxy.com/v1/images/generations
    """
    base = api_endpoint.strip()

    # Remove trailing /chat/completions or /completions
    base = re.sub(r"/chat/completions/?$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"/completions/?$", "", base, flags=re.IGNORECASE)
    base = base.rstrip("/")

    # Ensure /v1 is present
    if not re.search(r"/v1/?$", base, flags=re.IGNORECASE):
        base = base + "/v1"

    return base + "/images/generations"


# gofile.io upload servers to try in order (fallbacks if the API lookup fails)
_GOFILE_FALLBACK_SERVERS = ["store1", "store2", "store3", "store4"]


def _get_gofile_servers():
    """
    Query gofile.io for available upload servers.
    Returns a list of server names, falling back to a static list on failure.
    """
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request("https://api.gofile.io/servers", method="GET")
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        servers = (data.get("data") or {}).get("servers") or []
        names = [s.get("name") for s in servers if s.get("name")]
        if names:
            return names
    except Exception:
        pass
    return list(_GOFILE_FALLBACK_SERVERS)


def _upload_to_gofile(file_path):
    """
    Upload a local file to gofile.io using a manually built multipart/form-data
    request (no curl dependency, works on Windows/macOS/Linux).
    Returns the public download page URL.
    """
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    last_error = None
    for server in _get_gofile_servers():
        upload_url = f"https://{server}.gofile.io/uploadFile"

        boundary = uuid.uuid4().hex
        crlf = "\r\n"
        body = b""
        body += (f"--{boundary}{crlf}").encode("utf-8")
        body += (
            f'Content-Disposition: form-data; name="file"; filename="{filename}"{crlf}'
        ).encode("utf-8")
        body += (f"Content-Type: application/octet-stream{crlf}{crlf}").encode("utf-8")
        body += file_bytes
        body += (f"{crlf}--{boundary}--{crlf}").encode("utf-8")

        req = urllib.request.Request(
            upload_url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
                resp_text = resp.read().decode("utf-8")
            resp_json = json.loads(resp_text)
            if resp_json.get("status") != "ok":
                last_error = f"gofile returned status != ok: {resp_text[:300]}"
                continue
            download_page = ((resp_json.get("data") or {}).get("downloadPage") or "").strip()
            if download_page:
                return download_page
            last_error = f"gofile response missing downloadPage: {resp_text[:300]}"
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(last_error or "all gofile servers failed")


def _output(ok, error=""):
    """Write error result JSON to stdout."""
    out = {"ok": ok}
    if error:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
