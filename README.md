# VPS 解锁监控系统

自动监控多台VPS的流媒体和AI服务解锁状态，并提供可视化界面展示。

## 功能特性

- 🔍 自动检测流媒体服务解锁状态（Netflix、Disney+、YouTube、HBO等）
- 🤖 自动检测AI服务可用性（ChatGPT、Claude、Gemini等）
- ⏰ 配合Nezha面板定时任务，无需SSH密钥
- 📊 美观的Web可视化界面
- 📝 历史数据记录
- 🚀 轻量级架构，VPS端零依赖

## 架构说明

本系统采用**中心服务器 + VPS上报**的架构：

- **中心服务器**：运行 `app.py`，提供Web界面和接收数据
- **VPS端**：运行 `vps_check.py`，通过Nezha面板定时执行并上报数据

**优势**：
- ✅ 无需SSH密钥配置
- ✅ 适配Nezha v1探针
- ✅ VPS端脚本轻量，仅需Python3和curl
- ✅ 支持任意数量VPS

## 快速开始

### 一、中心服务器部署

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置

编辑 `config.json`：

```json
{
  "web_port": 5000
}
```

#### 3. 启动服务

```bash
python app.py
```

或后台运行：

```bash
nohup python app.py > server.log 2>&1 &
```

访问 `http://your-server-ip:5000` 查看监控面板。

### 二、VPS端部署

#### 1. 上传检测脚本

将 `vps_check.py` 上传到每台VPS：

```bash
scp vps_check.py root@vps-ip:/root/
```

#### 2. 在Nezha面板配置定时任务

在Nezha v1面板中，为每台VPS添加定时任务：

**任务类型**：Shell脚本

**执行命令**：

```bash
export MONITOR_SERVER="http://your-server-ip:5000" && \
export VPS_NAME="美国VPS" && \
python3 /root/vps_check.py
```

**执行周期**：建议每30-60分钟

#### 3. 验证

手动在VPS上运行一次：

```bash
python3 /root/vps_check.py
```

检查中心服务器是否收到数据。

## 详细部署指南

查看 [DEPLOY.md](DEPLOY.md) 获取完整的部署说明，包括：
- 批量部署脚本
- 自定义检测服务
- 故障排查指南

## 目录结构

```
vpsMonitor/
├── app.py              # 中心服务器
├── vps_check.py        # VPS端检测脚本
├── config.json         # 配置文件
├── requirements.txt    # Python依赖
├── DEPLOY.md          # 详细部署指南
├── templates/
│   └── index.html     # Web界面
└── results/           # 检测结果存储
    ├── latest.json    # 最新结果
    └── result_*.json  # 历史记录
```

## 注意事项

- ✅ 中心服务器需要公网访问（或VPS能访问的内网地址）
- ✅ VPS端仅需Python3和curl，无其他依赖
- ✅ 建议检测间隔30-60分钟
- ✅ Web界面每5分钟自动刷新

