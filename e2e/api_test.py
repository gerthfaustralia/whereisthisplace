import json
import os
import sys
import urllib.request


def main():
    url = "http://localhost:8000/predict"
    # Assume repo root contains sample image 'me.jpg'
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root, "me.jpg")
    if not os.path.exists(file_path):
        print(f"Sample image not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "rb") as f:
        img_bytes = f.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    lines = []
    lines.append(f"--{boundary}".encode())
    lines.append(b'Content-Disposition: form-data; name="photo"; filename="me.jpg"')
    lines.append(b"Content-Type: image/jpeg")
    lines.append(b"")
    lines.append(img_bytes)
    lines.append(f"--{boundary}--".encode())

    body = b"\r\n".join(lines)

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, data=body, headers=headers)

    with urllib.request.urlopen(req) as resp:
        status = resp.status
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read().decode()

    print("Status:", status)
    print("Content-Type:", content_type)
    print("Body:", data)

    assert status == 200, f"Expected status 200, got {status}"
    assert "application/json" in content_type.lower(), "Response is not JSON"
    json.loads(data)
    print("JSON response validated")


if __name__ == "__main__":
    main()
