import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== 配置区 ==========
WORKER_URL = "https://cloudflare_temp_email.wenxuanhe.workers.dev"
ADMIN_PASSWORD = "changsheng252403"
TARGET_EMAIL = "snebp9@cquservice.edu.kg"
# ============================

def extract_verification_code(content):
    """提取8位验证码"""
    # 匹配8位大写字母和数字的组合
    match = re.search(r'\b([A-Z0-9]{8})\b', content)
    if match:
        return match.group(1)
    return None

def get_mails_by_address(address, limit=20, offset=0):
    """查询指定邮箱的邮件"""
    url = f"{WORKER_URL}/admin/mails"
    params = {
        "limit": str(limit),
        "offset": str(offset),
        "address": address
    }
    headers = {"x-admin-auth": ADMIN_PASSWORD}
    
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()

# 查询邮件
result = get_mails_by_address(TARGET_EMAIL, limit=10)

if result:
    mails = result.get('results', [])
    
    for i, mail in enumerate(mails, 1):
        content = mail.get('raw', '')
        verification_code = extract_verification_code(content)
        
        print(f"{'='*70}")
        print(f"邮件 {i}/{len(mails)}")
        print(f"{'='*70}")
        print(f"发件人: {mail.get('source', 'N/A')}")
        print(f"主题: {mail.get('subject', 'N/A')}")
        print(f"时间: {mail.get('created_at')}")
        
        if verification_code:
            print(f"验证码: {verification_code}")
        else:
            print(f"验证码: 未找到")
        
        print(f"{'='*70}\n")