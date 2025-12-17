# VPS 解锁监控系统

自动监控多台VPS的流媒体和AI服务解锁状态，并提供可视化界面展示。

## 功能特性

- 🔍 自动检测流媒体服务解锁状态（Netflix、Disney+、YouTube、HBO等）
- 🤖 自动检测AI服务可用性（ChatGPT、Claude、Gemini等）
- ⏰ 配合Nezha面板定时任务，无需SSH密钥
- 📊 美观的Web可视化界面
- 📝 历史数据记录
- 🚀 轻量级架构，VPS端零依赖
- ✨ 现代化UI界面，支持状态图标
 
## 界面图例

Web界面使用以下SVG图标来表示不同的解锁状态：

| 图标 | 状态 | 描述 |
| :---: | :--- | :--- |
| <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7" /></svg> | **解锁 (Unlocked)** | 服务访问正常。 |
| <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18L18 6M6 6l12 12" /></svg> | **锁定 (Locked)** | 服务被限制或无法访问。 |
| <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg> | **错误 (Error)** | 检测过程中发生错误。 |
| <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /></svg> | **未知 (Unknown)** | 未获取到状态信息。 |
 
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

