"""
番茄钟计时器 (Pomodoro Timer)
每25分钟提醒一次，支持暂停、继续和重置功能。
"""

import time
import sys
import os
import io
from datetime import datetime, timedelta

# 设置标准输出为 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pomodoro_stats import get_stats


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """打印标题"""
    print("=" * 50)
    print("          🍅 番茄钟计时器 (Pomodoro Timer)")
    print("=" * 50)
    print()


def print_help():
    """打印帮助信息"""
    print("操作说明:")
    print("  [p] 暂停/继续")
    print("  [r] 重置")
    print("  [q] 退出")
    print()


def format_time(seconds):
    """将秒数格式化为 MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def show_notification():
    """显示系统通知（跨平台）"""
    message = "🍅 番茄钟时间到！该休息一下了！"
    
    if os.name == 'nt':  # Windows
        try:
            # 使用 Windows 原生通知
            from ctypes import windll
            windll.user32.MessageBoxW(0, message, "🍅 番茄钟提醒", 0x40 | 0x1000)
        except:
            # 使用控制台铃声
            print("\a")
    elif sys.platform == 'darwin':  # macOS
        os.system(f'osascript -e \'display notification "{message}" with title "🍅 番茄钟"\'')
    else:  # Linux
        try:
            os.system(f'notify-send "🍅 番茄钟" "{message}"')
        except:
            print("\a")
    
    print(f"\n{'=' * 50}")
    print(f"  ⏰ {message}")
    print(f"{'=' * 50}")


def pomodoro_timer(minutes=25):
    """
    番茄钟主函数
    
    Args:
        minutes: 专注时长（分钟），默认25分钟
    """
    total_seconds = minutes * 60
    remaining = total_seconds
    paused = False
    start_time = None
    
    clear_screen()
    print_header()
    print(f"  专注时长: {minutes} 分钟")
    print_help()
    
    try:
        while remaining > 0:
            if not paused:
                if start_time is None:
                    start_time = datetime.now()
                
                # 计算剩余时间
                elapsed = (datetime.now() - start_time).total_seconds()
                remaining = max(0, total_seconds - int(elapsed))
                
                # 显示进度条
                progress = (total_seconds - remaining) / total_seconds
                bar_length = 30
                filled = int(bar_length * progress)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                # 显示界面
                clear_screen()
                print_header()
                print(f"  ⏱️  剩余时间: {format_time(remaining)}")
                print(f"  📊 进度: [{bar}] {progress * 100:.1f}%")
                print()
                print_help()
                print(f"  状态: {'⏸️  已暂停' if paused else '▶️  运行中'}")
            
            # 检查用户输入（非阻塞）
            if os.name == 'nt':  # Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode().lower()
                    if key == 'p':
                        if not paused:
                            paused = True
                            pause_start = datetime.now()
                        else:
                            paused = False
                            # 调整开始时间以补偿暂停时间
                            pause_duration = (datetime.now() - pause_start).total_seconds()
                            start_time += timedelta(seconds=pause_duration)
                    elif key == 'r':
                        remaining = total_seconds
                        start_time = None
                        paused = False
                        clear_screen()
                        print_header()
                        print("  🔄 计时器已重置！")
                        time.sleep(1)
                    elif key == 'q':
                        print("\n  👋 已退出番茄钟")
                        return
            else:  # Unix-like
                import select
                import termios
                import tty
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'p':
                        if not paused:
                            paused = True
                            pause_start = datetime.now()
                        else:
                            paused = False
                            pause_duration = (datetime.now() - pause_start).total_seconds()
                            start_time += timedelta(seconds=pause_duration)
                    elif key == 'r':
                        remaining = total_seconds
                        start_time = None
                        paused = False
                        clear_screen()
                        print_header()
                        print("  🔄 计时器已重置！")
                        time.sleep(1)
                    elif key == 'q':
                        print("\n  👋 已退出番茄钟")
                        return
            
            time.sleep(0.5)
        
        # 时间到！
        clear_screen()
        print_header()
        show_notification()

        # 記錄統計
        stats = get_stats()
        stats.add(minutes)

        print()
        print(f"  ✅ 专注 {minutes} 分钟完成！")
        print(f"  💡 建议休息 5 分钟")
        print()
        print(f"  📊 今日已完成: {stats.today_count()} 个番茄钟 ({stats.today_minutes()} 分钟)")
        print(f"  🔥 连续打卡: {stats.streak()} 天")
        print()
        
        # 询问是否继续
        choice = input("  是否开始下一个番茄钟？(y/n): ").lower()
        if choice == 'y':
            pomodoro_timer(minutes)
        else:
            print("\n  👋 已退出番茄钟")
            
    except KeyboardInterrupt:
        print("\n\n  👋 已退出番茄钟")


def main():
    """主函数"""
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg in ("-s", "--stats"):
                # 顯示統計
                stats = get_stats()
                print(stats.summary())
                return 0
            elif arg in ("-h", "--help"):
                print("用法:")
                print("  python pomodoro_timer.py             开始 25 分钟番茄钟")
                print("  python pomodoro_timer.py [分钟数]     自定义时长")
                print("  python pomodoro_timer.py -s           查看统计")
                print("  python pomodoro_timer.py -h           查看帮助")
                return 0
            else:
                try:
                    minutes = int(arg)
                    if minutes <= 0:
                        raise ValueError
                except ValueError:
                    print("用法: python pomodoro_timer.py [分钟数]")
                    print("示例: python pomodoro_timer.py 25")
                    print("统计: python pomodoro_timer.py -s")
                    return 1
        else:
            minutes = 25

        pomodoro_timer(minutes)

    except Exception as e:
        print(f"错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())