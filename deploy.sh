#!/bin/bash

# VPS批量部署脚本
# 用法: ./deploy.sh

echo "================================"
echo "VPS监控系统 - 批量部署工具"
echo "================================"
echo ""

# 配置中心服务器地址
read -p "请输入中心服务器地址 (例如: http://monitor.example.com:5000): " SERVER_URL

if [ -z "$SERVER_URL" ]; then
    echo "错误: 服务器地址不能为空"
    exit 1
fi

echo ""
echo "请输入VPS信息 (格式: 用户@主机:VPS名称，输入空行结束):"
echo "示例: root@us.vps.com:美国VPS"
echo ""

VPS_LIST=()
while true; do
    read -p "VPS #$((${#VPS_LIST[@]} + 1)): " vps_info
    if [ -z "$vps_info" ]; then
        break
    fi
    VPS_LIST+=("$vps_info")
done

if [ ${#VPS_LIST[@]} -eq 0 ]; then
    echo "错误: 至少需要一台VPS"
    exit 1
fi

echo ""
echo "================================"
echo "开始部署到 ${#VPS_LIST[@]} 台VPS..."
echo "================================"
echo ""

for vps_info in "${VPS_LIST[@]}"; do
    IFS=':' read -r vps_host vps_name <<< "$vps_info"
    
    echo ">>> 部署到 $vps_name ($vps_host)..."
    
    # 上传脚本
    if scp -o ConnectTimeout=10 vps_check.py $vps_host:/root/; then
        echo "  ✓ 脚本上传成功"
    else
        echo "  ✗ 脚本上传失败，跳过"
        continue
    fi
    
    # 修改配置
    ssh -o ConnectTimeout=10 $vps_host "sed -i \"s|SERVER_URL = .*|SERVER_URL = os.getenv('MONITOR_SERVER', '$SERVER_URL')|\" /root/vps_check.py"
    ssh -o ConnectTimeout=10 $vps_host "sed -i \"s|VPS_NAME = .*|VPS_NAME = os.getenv('VPS_NAME', '$vps_name')|\" /root/vps_check.py"
    
    echo "  ✓ 配置已更新"
    echo ""
    echo "  在Nezha面板中添加以下定时任务:"
    echo "  ----------------------------------------"
    echo "  export MONITOR_SERVER=\"$SERVER_URL\" && \\"
    echo "  export VPS_NAME=\"$vps_name\" && \\"
    echo "  python3 /root/vps_check.py"
    echo "  ----------------------------------------"
    echo ""
done

echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "下一步操作:"
echo "1. 在Nezha面板为每台VPS配置上述定时任务"
echo "2. 建议执行周期: 30-60分钟"
echo "3. 访问 $SERVER_URL 查看监控面板"
echo ""

