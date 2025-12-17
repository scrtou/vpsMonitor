#!/bin/bash

# VPS 监控服务管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"
APP_FILE="$SCRIPT_DIR/app.py"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "服务已在运行中 (PID: $PID)"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    echo "正在启动 VPS 监控服务..."
    cd "$SCRIPT_DIR"
    nohup python3 "$APP_FILE" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ 服务启动成功 (PID: $PID)"
        echo "✓ 日志文件: $LOG_FILE"
        tail -n 5 "$LOG_FILE"
    else
        echo "✗ 服务启动失败，请查看日志: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "服务未运行"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "服务未运行 (PID 文件存在但进程不存在)"
        rm -f "$PID_FILE"
        return 1
    fi
    
    echo "正在停止服务 (PID: $PID)..."
    kill "$PID"
    
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            rm -f "$PID_FILE"
            echo "✓ 服务已停止"
            return 0
        fi
        sleep 1
    done
    
    echo "强制停止服务..."
    kill -9 "$PID"
    rm -f "$PID_FILE"
    echo "✓ 服务已强制停止"
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "服务未运行"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ 服务运行中 (PID: $PID)"
        echo ""
        ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime
        return 0
    else
        echo "✗ 服务未运行 (PID 文件存在但进程不存在)"
        rm -f "$PID_FILE"
        return 1
    fi
}

restart() {
    echo "重启服务..."
    stop
    sleep 2
    start
}

logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo "日志文件不存在"
        return 1
    fi
    
    if [ "$1" = "-f" ]; then
        tail -f "$LOG_FILE"
    else
        tail -n 50 "$LOG_FILE"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs [-f]}"
        echo ""
        echo "命令说明:"
        echo "  start    - 启动服务"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  status   - 查看服务状态"
        echo "  logs     - 查看最近 50 行日志"
        echo "  logs -f  - 实时查看日志"
        exit 1
        ;;
esac

