"""
番茄钟计时器 (Pomodoro Timer)
支援自動循環模式：工作 → 休息 → 工作 → ... 直到完成指定循環數。
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


def print_header(title=None):
    """打印标题"""
    print("=" * 50)
    print(f"          {title or '🍅 番茄钟计时器 (Pomodoro Timer)'}")
    print("=" * 50)
    print()


def print_help(extra_keys=None):
    """打印帮助信息"""
    print("操作说明:")
    print("  [p] 暂停/继续")
    print("  [r] 重置")
    print("  [q] 退出")
    if extra_keys:
        for key, desc in extra_keys:
            print(f"  [{key}] {desc}")
    print()


def format_time(seconds):
    """将秒数格式化为 MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def show_notification(msg=None):
    """显示系统通知（跨平台）"""
    message = msg or "🍅 番茄钟时间到！该休息一下了！"

    if os.name == 'nt':  # Windows
        try:
            from ctypes import windll
            windll.user32.MessageBoxW(0, message, "🍅 番茄钟提醒", 0x40 | 0x1000)
        except:
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


def _run_one_timer(minutes, title, extra_help=None):
    """
    执行一个计时阶段，返回 True 表示正常完成，False 表示用户退出。
    不处理统计记录——由调用者决定。
    """
    total_seconds = minutes * 60
    remaining = total_seconds
    paused = False
    start_time = None

    clear_screen()
    print_header(title)
    print(f"  时长: {minutes} 分钟")
    print_help(extra_help)

    try:
        while remaining > 0:
            if not paused:
                if start_time is None:
                    start_time = datetime.now()

                elapsed = (datetime.now() - start_time).total_seconds()
                remaining = max(0, total_seconds - int(elapsed))

                progress = (total_seconds - remaining) / total_seconds
                bar_length = 30
                filled = int(bar_length * progress)
                bar = "█" * filled + "░" * (bar_length - filled)

                clear_screen()
                print_header(title)
                print(f"  ⏱️  剩余时间: {format_time(remaining)}")
                print(f"  📊 进度: [{bar}] {progress * 100:.1f}%")
                print()
                print_help(extra_help)
                print(f"  状态: {'⏸️  已暂停' if paused else '▶️  运行中'}")

            # 检查用户输入（非阻塞）
            if os.name == 'nt':  # Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode().lower()
                    result = _handle_key(key, paused, start_time, total_seconds, remaining)
                    if result == 'quit':
                        return False
                    elif result == 'skip':
                        return True
                    elif isinstance(result, tuple):
                        paused, start_time, remaining = result[0], result[1], result[2]
            else:  # Unix-like
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                    result = _handle_key(key, paused, start_time, total_seconds, remaining)
                    if result == 'quit':
                        return False
                    elif result == 'skip':
                        return True
                    elif isinstance(result, tuple):
                        paused, start_time, remaining = result[0], result[1], result[2]

            time.sleep(0.5)

        # 时间到
        clear_screen()
        print_header(title)
        show_notification(f"⏰ {title} 时间到！")
        return True

    except KeyboardInterrupt:
        print("\n\n  👋 已退出番茄钟")
        return False


def _handle_key(key, paused, start_time, total_seconds, remaining):
    """处理按键输入，返回 ('quit'|'skip'|(paused, start_time, remaining)|None)"""
    if key == 'p':
        if not paused:
            return True, start_time, remaining
        else:
            return False, start_time, remaining
    elif key == 'r':
        clear_screen()
        print_header()
        print("  🔄 计时器已重置！")
        time.sleep(1)
        return False, None, total_seconds
    elif key == 'q':
        print("\n  👋 已退出番茄钟")
        return 'quit'
    elif key == 's':
        # 跳过当前阶段（仅在循环模式有意义）
        return 'skip'
    return None


def pomodoro_timer(minutes=25):
    """单次番茄钟（保持向后兼容）"""
    title = f"🍅 番茄钟 ({minutes} 分钟)"
    _run_one_timer(minutes, title)
    stats = get_stats()
    stats.add(minutes)
    print()
    print(f"  ✅ 专注 {minutes} 分钟完成！")
    print(f"  📊 今日已完成: {stats.today_count()} 个番茄钟 ({stats.today_minutes()} 分钟)")
    print(f"  🔥 连续打卡: {stats.streak()} 天")
    print()


def run_cycle(work_minutes=25, break_minutes=5, count=4):
    """
    自动循环模式：工作 → 休息 → 工作 → ... 共 count 个循环。
    每个循环 = 1 个工作阶段 + 1 个休息阶段（最后一个循环只有工作）。
    """
    stats = get_stats()
    print_header("🍅 番茄钟 - 自动循环模式")
    print(f"  工作: {work_minutes} 分钟  |  休息: {break_minutes} 分钟  |  循环: {count} 次")
    print()
    input("  按 Enter 开始...")

    cycle = 1
    while cycle <= count:
        # ── 工作阶段 ──
        title = f"🍅 工作 #{cycle}/{count} ({work_minutes} 分钟)"
        extra = [("s", "跳过休息")]
        ok = _run_one_timer(work_minutes, title, extra)
        if not ok:
            print(f"\n  👋 循环中断于第 {cycle} 个工作阶段")
            return
        stats.add(work_minutes, task="工作")
        clear_screen()
        print_header(title)
        print(f"  ✅ 工作 {cycle}/{count} 完成！")
        print(f"  📊 今日: {stats.today_count()} 个番茄钟 ({stats.today_minutes()} 分钟)")
        print()

        if cycle >= count:
            break  # 最后一個循環不需要休息

        # ── 休息阶段 ──
        title = f"☕ 休息 #{cycle}/{count} ({break_minutes} 分钟)"
        extra = [("s", "跳过休息")]
        ok = _run_one_timer(break_minutes, title, extra)
        if not ok:
            print(f"\n  👋 循环中断于第 {cycle} 个休息阶段")
            return
        stats.add(break_minutes, task="休息")
        clear_screen()
        print_header(title)
        print(f"  ✅ 休息 {cycle}/{count} 完成！开始下一个工作...")
        time.sleep(1.5)
        cycle += 1

    print()
    print("=" * 50)
    print(f"  🎉 全部 {count} 个循环完成！")
    print(f"  📊 今日: {stats.today_count()} 个阶段 ({stats.today_minutes()} 分钟)")
    print(f"  🔥 连续打卡: {stats.streak()} 天")
    print("=" * 50)
    print()


def main():
    """主函数"""
    try:
        args = sys.argv[1:]

        # 解析具名参数
        auto_cycle = False
        break_minutes = 5
        cycle_count = 4
        positional = []

        i = 0
        while i < len(args):
            a = args[i]
            if a in ("-c", "--cycle"):
                auto_cycle = True
            elif a in ("-b", "--break"):
                i += 1
                if i < len(args):
                    break_minutes = int(args[i])
            elif a in ("-n", "--count"):
                i += 1
                if i < len(args):
                    cycle_count = int(args[i])
            elif a in ("-s", "--stats"):
                stats = get_stats()
                print(stats.summary())
                return 0
            elif a in ("-h", "--help"):
                print("用法:")
                print("  python pomodoro_timer.py                    25 分钟番茄钟")
                print("  python pomodoro_timer.py [分钟数]            自定义时长")
                print("  python pomodoro_timer.py -c [-b 休息] [-n 次数]  自动循环")
                print("  python pomodoro_timer.py -s                  查看统计")
                print("  python pomodoro_timer.py -h                  查看帮助")
                print()
                print("自动循环示例:")
                print("  python pomodoro_timer.py 25 -c               4 循环, 5 分钟休息")
                print("  python pomodoro_timer.py 25 -c -b 10 -n 6    6 循环, 10 分钟休息")
                return 0
            else:
                try:
                    positional.append(int(a))
                except ValueError:
                    print(f"未知参数: {a}")
                    return 1
            i += 1

        work_minutes = positional[0] if positional else 25
        if work_minutes <= 0:
            print("分钟数必须为正整数")
            return 1

        if auto_cycle:
            run_cycle(work_minutes, break_minutes, cycle_count)
        else:
            pomodoro_timer(work_minutes)

    except Exception as e:
        print(f"错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())