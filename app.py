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
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route('/api/report', methods=['POST'])
def report():
    """接收VPS上报的检测数据"""
    try:
        data = request.get_json()
        vps_name = data.get('name', 'Unknown')
        
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
            if result['name'] == vps_name:
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
        
        print(f"✓ 收到 {vps_name} 的数据上报")
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

