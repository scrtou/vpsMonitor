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
CHECK_REGION = os.getenv('CHECK_REGION', '66')  # 默认全部平台检测
CHECK_TIMEOUT = int(os.getenv('CHECK_TIMEOUT', '300'))  # 默认5分钟超时
CHECK_ARGS = os.getenv('CHECK_ARGS', f'-R {CHECK_REGION}')

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
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'services': {}
    }
    
    try:
        cmd = f"bash {CHECK_SCRIPT} {CHECK_ARGS}"
        output = subprocess.run(cmd, shell=True, capture_output=True, timeout=CHECK_TIMEOUT, text=True)
        lines = output.stdout.split('\n')
        
        # 分离IPv4和IPv6结果
        current_section = None
        ipv4_results = {}
        ipv6_results = {}
        
        for line in lines:
            # 检测IPv4/IPv6区段
            if 'IPv4' in line and '测试' in line:
                current_section = 'ipv4'
                continue
            elif 'IPv6' in line and '测试' in line:
                current_section = 'ipv6'
                continue
            
            # 匹配形如 "服务名: 状态" 的行
            match = re.match(r'^\s*(.+?):\s+(.+)$', line)
            if match:
                service_name = match.group(1).strip()
                status_info = match.group(2).strip()
                
                # 过滤掉分隔线和标题行
                if '=' in service_name or '[' in service_name:
                    continue
                
                # 只保留包含状态信息的行
                if any(keyword in status_info for keyword in ['Yes', 'No', 'Failed', 'Only', 'Supported']):
                    parsed = parse_check_result(status_info)
                    if current_section == 'ipv4':
                        ipv4_results[service_name] = parsed
                    elif current_section == 'ipv6':
                        ipv6_results[service_name] = parsed
        
        # 同时展示IPv4和IPv6结果
        for service, data in ipv4_results.items():
            result['services'][f"{service} (IPv4)"] = data
        
        for service, data in ipv6_results.items():
            result['services'][f"{service} (IPv6)"] = data
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def upload_result(data):
    """上报结果到中心服务器"""
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_file = f.name
        
        cmd = f"curl -X POST '{SERVER_URL}/api/report' -H 'Content-Type: application/json' -d @{temp_file} --max-time 10"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=15, text=True)
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print(f"✓ 数据已上报到 {SERVER_URL}")
        else:
            print(f"✗ 上报失败: {result.stderr}")
    except Exception as e:
        print(f"✗ 上报失败: {e}")

if __name__ == '__main__':
    print(f"开始检测 {VPS_NAME}...")
    result = run_checks()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    upload_result(result)

