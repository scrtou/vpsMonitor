#!/usr/bin/env python3
"""
VPS本地检测脚本 - 部署到每台VPS上
在Nezha面板配置定时任务运行此脚本
"""
import json
import subprocess
import sys
import os
import socket
from datetime import datetime

# 配置：中心服务器地址
SERVER_URL = os.getenv('MONITOR_SERVER', 'http://your-server.com:5000')

# 自动获取VPS名称（使用主机名）
def get_vps_name():
    try:
        return socket.gethostname()
    except:
        return 'VPS-Unknown'

VPS_NAME = get_vps_name()

SERVICES = {
    'streaming': {
        'netflix': 'https://www.netflix.com',
        'disney': 'https://www.disneyplus.com',
        'youtube': 'https://www.youtube.com/premium',
        'hbo': 'https://www.hbomax.com'
    },
    'ai': {
        'chatgpt': 'https://chat.openai.com',
        'claude': 'https://claude.ai',
        'gemini': 'https://gemini.google.com'
    }
}

def check_url(url):
    """检测URL访问状态"""
    try:
        cmd = f"curl -sL -w '%{{http_code}}' '{url}' -o /dev/null --max-time 10"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
        code = result.stdout.decode().strip()
        return code
    except:
        return 'timeout'

def run_checks():
    """执行所有检测"""
    result = {
        'name': VPS_NAME,
        'timestamp': datetime.now().isoformat(),
        'streaming': {},
        'ai': {}
    }
    
    for service, url in SERVICES['streaming'].items():
        code = check_url(url)
        status = 'unlocked' if code in ['200', '301', '302'] else 'locked' if code != 'timeout' else 'error'
        result['streaming'][service] = {'status': status, 'code': code}
    
    for service, url in SERVICES['ai'].items():
        code = check_url(url)
        status = 'unlocked' if code not in ['403', '451', 'timeout'] else 'locked' if code != 'timeout' else 'error'
        result['ai'][service] = {'status': status, 'code': code}
    
    return result

def upload_result(data):
    """上报结果到中心服务器"""
    try:
        cmd = f"curl -X POST '{SERVER_URL}/api/report' -H 'Content-Type: application/json' -d '{json.dumps(data)}' --max-time 10"
        subprocess.run(cmd, shell=True, timeout=15)
        print(f"✓ 数据已上报到 {SERVER_URL}")
    except Exception as e:
        print(f"✗ 上报失败: {e}")

if __name__ == '__main__':
    print(f"开始检测 {VPS_NAME}...")
    result = run_checks()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    upload_result(result)

