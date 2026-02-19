#!/usr/bin/env python3
"""
Antigravity OAuth 授权演示 - 简化版
仅演示：授权 → 获取 token
"""

import secrets
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import requests

# ============== OAuth 配置 ==============
CLIENT_ID = "YOUR_GOOGLE_OAUTH_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"
CALLBACK_PORT = 51121
REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/oauth-callback"

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs",
]


# ============== 回调服务器 ==============
class CallbackHandler(BaseHTTPRequestHandler):
    code = None
    state = None
    
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        CallbackHandler.code = query.get("code", [None])[0]
        CallbackHandler.state = query.get("state", [None])[0]
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Done! Close this window.</h1>")
    
    def log_message(self, *args):
        pass


# ============== 主流程 ==============
def main():
    # 1. 生成 state
    state = secrets.token_urlsafe(32)
    
    # 2. 启动回调服务器
    server = HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)
    Thread(target=server.handle_request, daemon=True).start()
    
    # 3. 构建授权 URL
    params = {
        "access_type": "offline",
        "client_id": CLIENT_ID,
        "prompt": "consent",
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": state,
    }
    auth_url = f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
    
    print(f"授权 URL:\n{auth_url}\n")
    print("正在打开浏览器...")
    webbrowser.open(auth_url)
    
    # 4. 等待回调
    print("等待授权回调...")
    server.handle_request()
    
    if not CallbackHandler.code or CallbackHandler.state != state:
        print("授权失败")
        return
    
    print(f"授权码: {CallbackHandler.code[:30]}...")
    
    # 5. 换取 token
    print("\n正在换取 token...")
    resp = requests.post(TOKEN_ENDPOINT, data={
        "code": CallbackHandler.code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    
    if resp.status_code != 200:
        print(f"换取失败: {resp.text}")
        return
    
    tokens = resp.json()
    print(f"\n✅ 授权成功!")
    print(f"access_token:  {tokens['access_token'][:50]}...")
    print(f"refresh_token: {tokens.get('refresh_token', 'N/A')[:50]}...")
    print(f"expires_in:    {tokens.get('expires_in')} 秒")


if __name__ == "__main__":
    main()
