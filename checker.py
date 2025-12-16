#!/usr/bin/env python3
import json
import subprocess
import datetime
import os
from pathlib import Path

class VPSChecker:
    def __init__(self, config_path='config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
    
    def check_vps(self, vps):
        """检查单个VPS的解锁状态"""
        result = {
            'name': vps['name'],
            'host': vps['host'],
            'timestamp': datetime.datetime.now().isoformat(),
            'streaming': {},
            'ai': {},
            'status': 'success'
        }
        
        try:
            # 测试流媒体解锁
            for service in self.config['services']['streaming']:
                result['streaming'][service] = self._check_streaming(vps, service)
            
            # 测试AI服务解锁
            for service in self.config['services']['ai']:
                result['ai'][service] = self._check_ai(vps, service)
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _check_streaming(self, vps, service):
        """检查流媒体服务解锁状态"""
        test_urls = {
            'netflix': 'https://www.netflix.com',
            'disney': 'https://www.disneyplus.com',
            'youtube': 'https://www.youtube.com/premium',
            'hbo': 'https://www.hbomax.com'
        }
        
        cmd = f"ssh -o StrictHostKeyChecking=no {vps['user']}@{vps['host']} -p {vps['port']} \"curl -sL -w '%{{http_code}}' {test_urls.get(service, '')} -o /dev/null --max-time 10\""
        
        try:
            output = subprocess.check_output(cmd, shell=True, timeout=15, stderr=subprocess.DEVNULL)
            code = output.decode().strip()
            return {'status': 'unlocked' if code in ['200', '301', '302'] else 'locked', 'code': code}
        except:
            return {'status': 'error', 'code': 'timeout'}
    
    def _check_ai(self, vps, service):
        """检查AI服务解锁状态"""
        test_urls = {
            'chatgpt': 'https://chat.openai.com',
            'claude': 'https://claude.ai',
            'gemini': 'https://gemini.google.com'
        }
        
        cmd = f"ssh -o StrictHostKeyChecking=no {vps['user']}@{vps['host']} -p {vps['port']} \"curl -sL -w '%{{http_code}}' {test_urls.get(service, '')} -o /dev/null --max-time 10\""
        
        try:
            output = subprocess.check_output(cmd, shell=True, timeout=15, stderr=subprocess.DEVNULL)
            code = output.decode().strip()
            return {'status': 'unlocked' if code not in ['403', '451'] else 'locked', 'code': code}
        except:
            return {'status': 'error', 'code': 'timeout'}
    
    def run_all_checks(self):
        """运行所有VPS检查"""
        results = []
        for vps in self.config['vps_list']:
            print(f"检查 {vps['name']}...")
            result = self.check_vps(vps)
            results.append(result)
        
        # 保存结果
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = self.results_dir / f'result_{timestamp}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 更新最新结果
        with open('results/latest.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"检查完成，结果保存至 {result_file}")
        return results

if __name__ == '__main__':
    checker = VPSChecker()
    checker.run_all_checks()
