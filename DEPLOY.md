# 部署指南

## 架构说明

- **中心服务器**：运行 `app.py`，接收数据并提供Web界面
- **VPS端**：运行 `vps_check.py`，定时检测并上报数据到中心服务器
- 

## 一、中心服务器部署

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器

编辑 `config.json`：

```json
{
  "web_port": 5000
}
```

### 3. 启动服务

```bash
python app.py
```

或后台运行：

```bash
nohup python app.py > server.log 2>&1 &
```

访问 `http://your-server-ip:5000` 查看监控面板。

## 二、VPS端部署

### 1. 上传检测脚本

将 `vps_check.py` 上传到每台VPS：

```bash
scp vps_check.py root@vps-ip:/root/
```

### 2. 配置环境变量

在VPS上设置环境变量（或直接修改脚本中的配置）：

```bash
export MONITOR_SERVER="http://your-server-ip:5000"
export VPS_NAME="美国VPS"
```

### 3. 测试运行

```bash
python3 vps_check.py
```

### 4. 在Nezha面板配置定时任务

在Nezha v1面板中，为每台VPS添加定时任务：

**任务类型**：Shell脚本

**执行命令**：

```bash
export MONITOR_SERVER="http://your-server-ip:5000" && \
export VPS_NAME="美国VPS" && \
python3 /root/vps_check.py
```

**执行周期**：建议每30-60分钟执行一次

**示例配置**：

- VPS-1（美国）：

  ```bash
  export MONITOR_SERVER="http://monitor.example.com:5000" && \
  export VPS_NAME="美国VPS" && \
  python3 /root/vps_check.py
  ```
- VPS-2（日本）：

  ```bash
  export MONITOR_SERVER="http://monitor.example.com:5000" && \
  export VPS_NAME="日本VPS" && \
  python3 /root/vps_check.py
  ```

## 三、快速部署脚本

### 批量部署到VPS

创建 `deploy.sh`：

```bash
#!/bin/bash

# 配置
SERVER_URL="http://your-server-ip:5000"
VPS_LIST=(
  "root@us-vps.com:美国VPS"
  "root@jp-vps.com:日本VPS"
  "root@sg-vps.com:新加坡VPS"
)

for vps_info in "${VPS_LIST[@]}"; do
  IFS=':' read -r vps_host vps_name <<< "$vps_info"
  
  echo "部署到 $vps_name ($vps_host)..."
  
  # 上传脚本
  scp vps_check.py $vps_host:/root/
  
  # 修改配置
  ssh $vps_host "sed -i \"s|SERVER_URL = .*|SERVER_URL = '$SERVER_URL'|\" /root/vps_check.py"
  ssh $vps_host "sed -i \"s|VPS_NAME = .*|VPS_NAME = '$vps_name'|\" /root/vps_check.py"
  
  echo "✓ $vps_name 部署完成"
done
```

运行：

```bash
chmod +x deploy.sh
./deploy.sh
```

## 四、验证部署

1. 在VPS上手动运行一次：

   ```bash
   python3 /root/vps_check.py
   ```
2. 检查中心服务器日志，应该看到：

   ```
   ✓ 收到 美国VPS 的数据上报
   ```
3. 访问Web界面，查看是否显示数据

## 五、故障排查

### VPS无法上报数据

1. 检查网络连接：

   ```bash
   curl http://your-server-ip:5000/api/latest
   ```
2. 检查防火墙：

   ```bash
   # 中心服务器开放端口
   ufw allow 5000
   ```
3. 查看VPS执行日志（在Nezha面板中查看任务执行记录）

### 数据不更新

- 检查Nezha定时任务是否正常执行
- 查看中心服务器的 `results/latest.json` 文件
- 检查时间戳是否更新

## 六、自定义检测服务

编辑 `vps_check.py` 中的 `SERVICES` 字典：

```python
SERVICES = {
    'streaming': {
        'netflix': 'https://www.netflix.com',
        'tiktok': 'https://www.tiktok.com',
        # 添加更多...
    },
    'ai': {
        'chatgpt': 'https://chat.openai.com',
        'midjourney': 'https://www.midjourney.com',
        # 添加更多...
    }
}
```

重新部署到所有VPS即可。
