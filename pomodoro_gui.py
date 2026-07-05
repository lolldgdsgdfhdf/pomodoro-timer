"""
番茄钟计时器 - 图形界面版 (Pomodoro Timer GUI)
带窗口界面、暂停/开始按钮、音乐提醒功能
"""

import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import os
import sys
import winsound
from datetime import datetime, timedelta

from pomodoro_stats import get_stats


class PomodoroTimer:
    """番茄钟计时器 GUI 类"""
    
    # 颜色方案
    COLORS = {
        'bg': '#2B2B2B',
        'fg': '#FFFFFF',
        'accent': '#FF6B35',
        'success': '#4CAF50',
        'warning': '#FFC107',
        'button_bg': '#3C3C3C',
        'button_active': '#505050',
        'progress_bg': '#1A1A1A',
        'progress_fill': '#FF6B35',
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🍅 番茄钟计时器")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLORS['bg'])
        
        # 设置窗口图标（如果有）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 窗口居中
        self.center_window()
        
        # 计时器状态
        self.total_seconds = 25 * 60  # 默认25分钟
        self.remaining = self.total_seconds
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_start = None
        self.timer_thread = None
        self.update_id = None
        
        # 创建界面
        self.setup_ui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """设置界面"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_frame.pack(expand=True, fill='both', padx=30, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="🍅 番茄钟",
            font=('Microsoft YaHei', 24, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['accent']
        )
        title_label.pack(pady=(0, 5))
        
        # 副标题
        subtitle_label = tk.Label(
            main_frame,
            text="专注工作，休息片刻",
            font=('Microsoft YaHei', 10),
            bg=self.COLORS['bg'],
            fg='#888888'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # 时间显示
        self.time_label = tk.Label(
            main_frame,
            text="25:00",
            font=('Consolas', 64, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['fg']
        )
        self.time_label.pack(pady=(10, 5))
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="准备就绪",
            font=('Microsoft YaHei', 12),
            bg=self.COLORS['bg'],
            fg='#888888'
        )
        self.status_label.pack(pady=(0, 20))
        
        # 进度条
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'custom.Horizontal.TProgressbar',
            background=self.COLORS['progress_fill'],
            troughcolor=self.COLORS['progress_bg'],
            bordercolor=self.COLORS['bg'],
            lightcolor=self.COLORS['progress_fill'],
            darkcolor=self.COLORS['progress_fill']
        )
        
        self.progress_bar = ttk.Progressbar(
            main_frame,
            style='custom.Horizontal.TProgressbar',
            length=340,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(pady=(0, 25))
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        button_frame.pack(pady=(0, 15))
        
        # 开始/暂停按钮
        self.start_pause_btn = self.create_button(
            button_frame,
            text="▶  开始",
            command=self.toggle_start_pause,
            width=12,
            bg=self.COLORS['success']
        )
        self.start_pause_btn.pack(side='left', padx=5)
        
        # 重置按钮
        self.reset_btn = self.create_button(
            button_frame,
            text="↺  重置",
            command=self.reset_timer,
            width=12,
            bg=self.COLORS['button_bg']
        )
        self.reset_btn.pack(side='left', padx=5)

        # 统计按钮
        self.stats_btn = self.create_button(
            button_frame,
            text="📊  统计",
            command=self.show_stats,
            width=12,
            bg=self.COLORS['button_bg']
        )
        self.stats_btn.pack(side='left', padx=5)

        # 时间设置框架
        settings_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        settings_frame.pack(pady=(10, 0))
        
        # 时间选择标签
        settings_label = tk.Label(
            settings_frame,
            text="专注时长:",
            font=('Microsoft YaHei', 10),
            bg=self.COLORS['bg'],
            fg='#AAAAAA'
        )
        settings_label.pack(side='left', padx=(0, 10))
        
        # 时间选择下拉框
        self.time_var = tk.StringVar(value="25 分钟")
        self.time_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.time_var,
            values=["5 分钟", "10 分钟", "15 分钟", "20 分钟", "25 分钟", "30 分钟", "45 分钟", "60 分钟"],
            state='readonly',
            width=12,
            font=('Microsoft YaHei', 10)
        )
        self.time_combo.pack(side='left')
        self.time_combo.bind('<<ComboboxSelected>>', self.on_time_change)
        
        # 设置下拉框样式
        style.configure(
            'TCombobox',
            fieldbackground=self.COLORS['button_bg'],
            background=self.COLORS['button_bg'],
            foreground=self.COLORS['fg'],
            arrowcolor=self.COLORS['fg']
        )
        
        # 底部信息
        info_label = tk.Label(
            main_frame,
            text="💡 番茄工作法：25分钟专注 + 5分钟休息",
            font=('Microsoft YaHei', 9),
            bg=self.COLORS['bg'],
            fg='#666666'
        )
        info_label.pack(side='bottom', pady=(10, 0))
    
    def create_button(self, parent, text, command, width=10, bg=None):
        """创建统一样式的按钮"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=('Microsoft YaHei', 11, 'bold'),
            bg=bg or self.COLORS['button_bg'],
            fg=self.COLORS['fg'],
            activebackground=self.COLORS['button_active'],
            activeforeground=self.COLORS['fg'],
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        
        # 绑定悬停效果
        btn.bind('<Enter>', lambda e: btn.configure(bg=self.COLORS['button_active']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg or self.COLORS['button_bg']))
        
        return btn
    
    def on_time_change(self, event=None):
        """时间选择改变"""
        if not self.is_running:
            minutes = int(self.time_var.get().split()[0])
            self.total_seconds = minutes * 60
            self.remaining = self.total_seconds
            self.update_display()
            self.progress_bar['value'] = 0
            self.status_label.configure(text="准备就绪", fg='#888888')
    
    def toggle_start_pause(self):
        """切换开始/暂停"""
        if not self.is_running:
            self.start_timer()
        else:
            self.pause_timer()
    
    def start_timer(self):
        """开始计时"""
        if self.remaining <= 0:
            self.remaining = self.total_seconds
        
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        # 更新按钮
        self.start_pause_btn.configure(text="⏸  暂停", bg=self.COLORS['warning'])
        self.status_label.configure(text="▶  专注中...", fg=self.COLORS['success'])
        
        # 禁用时间选择
        self.time_combo.configure(state='disabled')
        
        # 启动计时线程
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()
    
    def pause_timer(self):
        """暂停计时"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_start = datetime.now()
            
            # 更新按钮
            self.start_pause_btn.configure(text="▶  继续", bg=self.COLORS['success'])
            self.status_label.configure(text="⏸  已暂停", fg=self.COLORS['warning'])
    
    def resume_timer(self):
        """继续计时"""
        if self.is_running and self.is_paused:
            # 调整开始时间以补偿暂停时间
            pause_duration = (datetime.now() - self.pause_start).total_seconds()
            self.start_time += timedelta(seconds=pause_duration)
            
            self.is_paused = False
            
            # 更新按钮
            self.start_pause_btn.configure(text="⏸  暂停", bg=self.COLORS['warning'])
            self.status_label.configure(text="▶  专注中...", fg=self.COLORS['success'])
    
    def run_timer(self):
        """计时器线程"""
        while self.is_running and self.remaining > 0:
            if not self.is_paused:
                # 计算剩余时间
                elapsed = (datetime.now() - self.start_time).total_seconds()
                self.remaining = max(0, self.total_seconds - int(elapsed))
                
                # 更新界面（在主线程中）
                self.root.after(0, self.update_display)
                
                # 更新进度条
                progress = ((self.total_seconds - self.remaining) / self.total_seconds) * 100
                self.root.after(0, lambda p=progress: self.progress_bar.configure(value=p))
            
            time.sleep(0.2)
        
        # 计时结束
        if self.is_running and self.remaining <= 0:
            self.root.after(0, self.timer_complete)
    
    def update_display(self):
        """更新时间显示"""
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
    
    def timer_complete(self):
        """计时完成"""
        self.is_running = False
        self.is_paused = False

        # 記錄統計
        minutes = int(self.time_var.get().split()[0])
        stats = get_stats()
        stats.add(minutes)

        # 更新界面
        self.time_label.configure(text="00:00")
        self.progress_bar['value'] = 100
        self.status_label.configure(
            text=f"✅ 时间到！今日完成 {stats.today_count()} 个番茄",
            fg=self.COLORS['accent']
        )
        self.start_pause_btn.configure(text="▶  开始", bg=self.COLORS['success'])

        # 启用时间选择
        self.time_combo.configure(state='readonly')

        # 播放音乐提醒
        self.play_alarm()

        # 弹出提醒对话框
        self.root.after(100, lambda: messagebox.showinfo(
            "🍅 番茄钟提醒",
            f"时间到！该休息一下了！\n\n建议休息 5 分钟\n\n"
            f"📊 今日: {stats.today_count()} 个番茄钟 ({stats.today_minutes()} 分钟)\n"
            f"🔥 连续打卡: {stats.streak()} 天"
        ))
    
    def play_alarm(self):
        """播放音乐提醒"""
        def play():
            # 播放 Windows 系统提示音
            for _ in range(3):
                try:
                    winsound.PlaySound(
                        winsound.SND_ALIAS | winsound.SND_ASYNC
                    )
                    time.sleep(0.5)
                except:
                    # 如果系统提示音失败，使用蜂鸣声
                    try:
                        winsound.Beep(800, 300)
                        time.sleep(0.2)
                        winsound.Beep(1000, 300)
                        time.sleep(0.2)
                        winsound.Beep(1200, 500)
                    except:
                        pass
        
        # 在后台线程播放
        threading.Thread(target=play, daemon=True).start()
    
    def reset_timer(self):
        """重置计时器"""
        self.is_running = False
        self.is_paused = False
        
        # 重置时间
        minutes = int(self.time_var.get().split()[0])
        self.total_seconds = minutes * 60
        self.remaining = self.total_seconds
        
        # 更新界面
        self.update_display()
        self.progress_bar['value'] = 0
        self.status_label.configure(text="已重置", fg='#888888')
        self.start_pause_btn.configure(text="▶  开始", bg=self.COLORS['success'])
        
        # 启用时间选择
        self.time_combo.configure(state='readonly')
    
    def show_stats(self):
        """顯示統計視窗"""
        stats = get_stats()

        # 建立新視窗
        stats_win = tk.Toplevel(self.root)
        stats_win.title("📊 番茄鐘統計")
        stats_win.geometry("440x480")
        stats_win.resizable(False, False)
        stats_win.configure(bg=self.COLORS['bg'])
        stats_win.grab_set()  # 模態視窗

        # 置中
        stats_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 440) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 480) // 2
        stats_win.geometry(f"440x480+{x}+{y}")

        frame = tk.Frame(stats_win, bg=self.COLORS['bg'])
        frame.pack(expand=True, fill='both', padx=25, pady=20)

        # 標題
        tk.Label(
            frame, text="📊 番茄鐘統計",
            font=('Microsoft YaHei', 20, 'bold'),
            bg=self.COLORS['bg'], fg=self.COLORS['accent']
        ).pack(pady=(0, 20))

        # 總計區塊
        total_frame = tk.Frame(frame, bg=self.COLORS['button_bg'], relief='flat', bd=0)
        total_frame.pack(fill='x', pady=(0, 15))

        stats_data = [
            ("总完成数", f"{stats.total_count} 个"),
            ("总专注时长", f"{stats.total_hours} 小时 ({stats.total_minutes} 分钟)"),
        ]
        for label, value in stats_data:
            row = tk.Frame(total_frame, bg=self.COLORS['button_bg'])
            row.pack(fill='x', padx=15, pady=8)
            tk.Label(row, text=label, font=('Microsoft YaHei', 11),
                     bg=self.COLORS['button_bg'], fg='#AAAAAA').pack(side='left')
            tk.Label(row, text=value, font=('Microsoft YaHei', 11, 'bold'),
                     bg=self.COLORS['button_bg'], fg=self.COLORS['fg']).pack(side='right')

        # 今日 / 本週 / 連續
        grid_frame = tk.Frame(frame, bg=self.COLORS['bg'])
        grid_frame.pack(fill='x', pady=(0, 15))

        cards = [
            ("今日", f"{stats.today_count()} 个\n{stats.today_minutes()} 分钟"),
            ("本周", f"{stats.week_count()} 个\n{stats.week_minutes()} 分钟"),
            ("🔥 连续打卡", f"{stats.streak()} 天"),
        ]
        for i, (title, value) in enumerate(cards):
            card = tk.Frame(grid_frame, bg=self.COLORS['button_bg'], relief='flat', bd=0,
                            width=120, height=80)
            card.pack(side='left', padx=5, expand=True, fill='both')
            card.pack_propagate(False)
            tk.Label(card, text=title, font=('Microsoft YaHei', 10),
                     bg=self.COLORS['button_bg'], fg='#AAAAAA').pack(pady=(12, 2))
            tk.Label(card, text=value, font=('Microsoft YaHei', 13, 'bold'),
                     bg=self.COLORS['button_bg'], fg=self.COLORS['accent']).pack()

        # 每日明細
        tk.Label(frame, text="最近 7 天", font=('Microsoft YaHei', 11, 'bold'),
                 bg=self.COLORS['bg'], fg='#AAAAAA').pack(anchor='w', pady=(5, 8))

        breakdown = stats.daily_breakdown(7)
        if breakdown:
            for date, data in reversed(list(breakdown.items())):
                bar_frame = tk.Frame(frame, bg=self.COLORS['bg'])
                bar_frame.pack(fill='x', pady=2)
                tk.Label(bar_frame, text=date[-5:], font=('Consolas', 9),
                         bg=self.COLORS['bg'], fg='#888888', width=7, anchor='w').pack(side='left')
                bar_width = min(data["count"] * 30, 200)
                bar = tk.Frame(bar_frame, bg=self.COLORS['accent'], width=bar_width, height=16)
                bar.pack(side='left', padx=(5, 5))
                bar.pack_propagate(False)
                tk.Label(bar_frame, text=f"{data['count']}个 {data['minutes']}分钟",
                         font=('Microsoft YaHei', 9),
                         bg=self.COLORS['bg'], fg='#CCCCCC').pack(side='left')
        else:
            tk.Label(frame, text="  還沒有記錄，開始你的第一個番茄鐘吧！",
                     font=('Microsoft YaHei', 10),
                     bg=self.COLORS['bg'], fg='#666666').pack(anchor='w')

        # 關閉按鈕
        tk.Button(
            frame, text="关闭", command=stats_win.destroy,
            font=('Microsoft YaHei', 11),
            bg=self.COLORS['button_bg'], fg=self.COLORS['fg'],
            activebackground=self.COLORS['button_active'],
            relief='flat', padx=30, pady=6, cursor='hand2'
        ).pack(pady=(15, 0))

    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            result = messagebox.askyesno(
                "确认退出",
                "计时器正在运行，确定要退出吗？"
            )
            if not result:
                return
        
        self.is_running = False
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = PomodoroTimer()
        app.run()
    except Exception as e:
        print(f"错误: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()