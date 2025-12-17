from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest')
def get_latest():
    try:
        with open('results/latest.json') as f:
            data = json.load(f)
        
        # 动态应用当前的 IP 映射配置
        config = load_config()
        vps_mappings = config.get('vps_mappings', {})
        
        for item in data:
            client_ip = item.get('ip', '')
            original_name = item.get('original_name', item.get('name', 'Unknown'))
            # 根据当前配置动态设置名称
            item['name'] = vps_mappings.get(client_ip, original_name)
        
        return jsonify(data)
    except:
        return jsonify([])

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    config = load_config()
    return jsonify({'vps_mappings': config.get('vps_mappings', {})})

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        new_mappings = request.get_json()
        config = load_config()
        config['vps_mappings'] = new_mappings
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 更新现有数据中的VPS名称
        results_file = Path('results/latest.json')
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
            
            # 根据新的IP映射更新每个VPS的名称
            for result in all_results:
                client_ip = result.get('ip', '')
                original_name = result.get('original_name', result.get('name', 'Unknown'))
                new_name = new_mappings.get(client_ip, original_name)
                result['name'] = new_name
            
            # 保存更新后的数据
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def report():
    """接收VPS上报的检测数据"""
    try:
        data = request.get_json()
        original_name = data.get('name', 'Unknown')
        
        # 获取上报者的IP地址
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # 根据IP映射查找自定义名称
        config = load_config()
        vps_mappings = config.get('vps_mappings', {})
        vps_name = vps_mappings.get(client_ip, original_name)
        
        # 更新数据中的名称
        data['name'] = vps_name
        data['original_name'] = original_name
        data['ip'] = client_ip
        
        # 读取现有数据
        results_file = Path('results/latest.json')
        if results_file.exists():
            with open(results_file) as f:
                all_results = json.load(f)
        else:
            all_results = []
        
        # 更新或添加该VPS的数据
        updated = False
        for i, result in enumerate(all_results):
            if result.get('ip') == client_ip or result['name'] == vps_name:
                all_results[i] = data
                updated = True
                break
        
        if not updated:
            all_results.append(data)
        
        # 保存更新后的数据
        Path('results').mkdir(exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        # 保存历史记录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history_file = Path('results') / f'result_{timestamp}_{vps_name}.json'
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 收到 {vps_name} ({client_ip}) 的数据上报")
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"✗ 处理上报数据失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    Path('results').mkdir(exist_ok=True)
    config = load_config()
    port = config.get('web_port', 5000)
    print(f"\n中心服务器启动在 http://0.0.0.0:{port}")
    print(f"等待VPS上报数据...\n")
    app.run(host='0.0.0.0', port=port, debug=False)

