#!/usr/bin/env python3
"""
VPS本地检测脚本 - 调用check.sh并解析结果
在Nezha面板配置定时任务运行此脚本
"""
import json
import subprocess
import re
import os
import socket
from datetime import datetime

# 配置
SERVER_URL = os.getenv('MONITOR_SERVER', 'http://your-server.com:5000')
CHECK_SCRIPT = os.getenv('CHECK_SCRIPT', 'check.sh')
CHECK_ARGS = os.getenv('CHECK_ARGS', '')  # 默认检测IPv4和IPv6

def get_vps_name():
    try:
        return socket.gethostname()
    except:
        return 'VPS-Unknown'

VPS_NAME = get_vps_name()

def parse_check_result(line):
    """解析check.sh的输出行"""
    if 'Yes' in line:
        return {'status': 'unlocked', 'info': line.strip()}
    elif 'No' in line:
        return {'status': 'locked', 'info': line.strip()}
    elif 'Failed' in line:
        return {'status': 'error', 'info': line.strip()}
    return {'status': 'unknown', 'info': line.strip()}

def run_checks():
    """运行check.sh并解析所有结果"""
    result = {
        'name': VPS_NAME,
        'timestamp': datetime.now().isoformat(),
        'services': {}
    }
    
    try:
        cmd = f"bash {CHECK_SCRIPT} {CHECK_ARGS}"
        output = subprocess.run(cmd, shell=True, capture_output=True, timeout=120, text=True)
        lines = output.stdout.split('\n')
        
        # 动态解析所有服务检测结果
        for line in lines:
            # 匹配形如 "服务名: 状态" 的行
            match = re.match(r'^\s*(.+?):\s+(.+)$', line)
            if match:
                service_name = match.group(1).strip()
                status_info = match.group(2).strip()
                
                # 过滤掉分隔线和标题行
                if '=' in service_name or '[' in service_name:
                    continue
                
                # 只保留包含状态信息的行
                if any(keyword in status_info for keyword in ['Yes', 'No', 'Failed', 'Only']):
                    result['services'][service_name] = parse_check_result(status_info)
            
    except Exception as e:
        result['error'] = str(e)
    
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

