"""
本地AI聊天室 - Local AI Chat Room
==================================
功能：
1. 左侧显示聊天记录（气泡样式）
2. 底部输入框和发送按钮
3. 调用本地 Ollama 服务 (deepseek-r1:7b)
4. 清空记录和导出聊天记录为 txt
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import json
import urllib.request
import urllib.error
import datetime


class ChatBubble(tk.Frame):
    """聊天气泡组件"""

    def __init__(self, parent, text, is_user=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#f0f0f0")
        self.pack(fill="x", padx=10, pady=4, anchor="e" if is_user else "w")

        # 气泡颜色
        bubble_color = "#95ec69" if is_user else "#ffffff"
        text_color = "#000000"
        align = "e" if is_user else "w"
        label_text = "你" if is_user else "AI"

        # 标签行（显示 你 / AI）
        label_frame = tk.Frame(self, bg="#f0f0f0")
        label_frame.pack(fill="x", anchor=align)

        tk.Label(
            label_frame,
            text=label_text,
            font=("Microsoft YaHei", 9, "bold"),
            fg="#666666",
            bg="#f0f0f0",
        ).pack(anchor=align, padx=4)

        # 气泡内容
        bubble_frame = tk.Frame(self, bg=bubble_color, highlightbackground="#d0d0d0",
                                highlightthickness=1, padx=10, pady=6)
        bubble_frame.pack(anchor=align, pady=(2, 0))

        msg_label = tk.Label(
            bubble_frame,
            text=text,
            font=("Microsoft YaHei", 10),
            fg=text_color,
            bg=bubble_color,
            wraplength=400,
            justify="left",
        )
        msg_label.pack()


class LocalAIChat:
    """本地AI聊天室主程序"""

    def __init__(self, root):
        self.root = root
        self.root.title("涛子 顺子")
        self.root.geometry("700x550")
        self.root.minsize(600, 400)
        self.root.configure(bg="#f0f0f0")

        # LM Studio 配置（OpenAI 兼容格式）
        self.api_url = "http://127.0.0.1:1234/v1/chat/completions"
        self.model_name = "deepseek-r1"

        # 聊天记录（用于导出）
        self.chat_history = []

        # 构建界面
        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg="#2b2b2b", height=40)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="🤖 本地AI聊天室",
            font=("Microsoft YaHei", 12, "bold"),
            fg="#ffffff",
            bg="#2b2b2b",
        ).pack(side="left", padx=15, pady=5)

        # 操作按钮框架
        btn_frame = tk.Frame(title_frame, bg="#2b2b2b")
        btn_frame.pack(side="right", padx=10)

        tk.Button(
            btn_frame,
            text="🗑 清空记录",
            font=("Microsoft YaHei", 9),
            bg="#555555",
            fg="#ffffff",
            relief="flat",
            padx=8,
            command=self.clear_chat,
        ).pack(side="left", padx=3)

        tk.Button(
            btn_frame,
            text="📥 导出为TXT",
            font=("Microsoft YaHei", 9),
            bg="#555555",
            fg="#ffffff",
            relief="flat",
            padx=8,
            command=self.export_chat,
        ).pack(side="left", padx=3)

        # 聊天记录显示区域（带滚动条）
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        # 使用 Canvas + Scrollbar 实现滚动
        self.canvas = tk.Canvas(self.chat_frame, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 底部输入区域
        input_frame = tk.Frame(self.root, bg="#e0e0e0", height=60)
        input_frame.pack(fill="x", padx=5, pady=(5, 5))
        input_frame.pack_propagate(False)

        self.input_entry = tk.Text(
            input_frame,
            font=("Microsoft YaHei", 10),
            height=2,
            wrap="word",
            relief="flat",
            padx=8,
            pady=5,
        )
        self.input_entry.pack(side="left", fill="both", expand=True, padx=(5, 5), pady=5)
        self.input_entry.bind("<Return>", self._on_enter_key)
        self.input_entry.bind("<Shift-Return>", lambda e: None)  # 允许 Shift+Enter 换行

        self.send_btn = tk.Button(
            input_frame,
            text="发送",
            font=("Microsoft YaHei", 10, "bold"),
            bg="#4a90d9",
            fg="#ffffff",
            relief="flat",
            padx=15,
            command=self.send_message,
        )
        self.send_btn.pack(side="right", padx=(0, 5), pady=5)

        # 状态栏
        self.status_bar = tk.Label(
            self.root,
            text="就绪 芜湖~ | 模型: DeepSeek-R1 (LM Studio)",
            font=("Microsoft YaHei", 8),
            fg="#888888",
            bg="#f0f0f0",
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=10, pady=(0, 3))

        # 欢迎消息
        self._add_bubble("你好！我是肖顺的顺子和涛哥的涛子，有什么可以帮你的吗？", is_user=False)

    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_enter_key(self, event):
        """回车键发送消息（Shift+Enter 换行）"""
        if not (event.state & 0x0001):  # 没有按住 Shift
            self.send_message()
            return "break"  # 阻止默认换行

    def _add_bubble(self, text, is_user=True):
        """添加聊天气泡"""
        bubble = ChatBubble(self.scrollable_frame, text, is_user=is_user)
        # 记录聊天历史
        role = "user" if is_user else "assistant"
        self.chat_history.append({"role": role, "content": text, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        # 滚动到底部
        self.root.after(100, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """滚动到底部"""
        self.canvas.yview_moveto(1.0)

    def _set_status(self, text):
        """设置状态栏文字"""
        self.status_bar.config(text=text)

    def send_message(self):
        """发送消息"""
        user_input = self.input_entry.get("1.0", tk.END).strip()
        if not user_input:
            return

        # 清空输入框
        self.input_entry.delete("1.0", tk.END)

        # 显示用户消息
        self._add_bubble(user_input, is_user=True)

        # 禁用发送按钮，防止重复发送
        self.send_btn.config(state="disabled", text="发送中...")
        self._set_status("AI 思考中...")

        # 在后台线程调用 LM Studio
        threading.Thread(target=self._call_lmstudio, args=(user_input,), daemon=True).start()

    def _call_lmstudio(self, user_input):
        """调用 LM Studio API（OpenAI 兼容格式）"""
        try:
            # 构建消息列表（带上下文，实现多轮对话）
            messages = []
            for msg in self.chat_history[-20:]:  # 保留最近20条对话作为上下文
                role = msg["role"]
                content = msg["content"]
                messages.append({"role": role, "content": content})

            # 构建请求数据（OpenAI 兼容格式）
            data = json.dumps({
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            # 发送请求（设置超时 120 秒）
            response = urllib.request.urlopen(req, timeout=120)
            result = json.loads(response.read().decode("utf-8"))

            # 解析 OpenAI 格式的响应
            ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "（AI 返回了空响应）")

            # 在主线程更新 UI
            self.root.after(0, self._display_ai_response, ai_response)

        except urllib.error.URLError as e:
            error_msg = f"⚠️ 连接 LM Studio 失败：{e.reason}\n请确保 LM Studio 已启动并加载模型（http://127.0.0.1:1234）"
            self.root.after(0, self._display_ai_response, error_msg)
        except json.JSONDecodeError:
            error_msg = "⚠️ AI 返回了无效的响应格式"
            self.root.after(0, self._display_ai_response, error_msg)
        except Exception as e:
            error_msg = f"⚠️ 发生错误：{str(e)}"
            self.root.after(0, self._display_ai_response, error_msg)

    def _display_ai_response(self, text):
        """显示 AI 响应"""
        self._add_bubble(text, is_user=False)
        self.send_btn.config(state="normal", text="发送")
        self._set_status("就绪 | 模型: deepseek-r1-distill-qwen-7b (LM Studio)")

    def clear_chat(self):
        """清空聊天记录"""
        if not self.chat_history:
            return

        if messagebox.askyesno("确认清空", "确定要清空所有聊天记录吗？"):
            # 清除所有气泡
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.chat_history.clear()
            self._add_bubble("聊天记录已清空，开始新的对话吧！", is_user=False)

    def export_chat(self):
        """导出聊天记录为 TXT 文件"""
        if not self.chat_history:
            messagebox.showinfo("提示", "没有聊天记录可以导出。")
            return

        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出聊天记录",
            initialfile=f"AI聊天记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("          本地AI聊天室 - 聊天记录\n")
                f.write("=" * 60 + "\n\n")

                for msg in self.chat_history:
                    role_name = "你" if msg["role"] == "user" else "AI"
                    f.write(f"[{msg['time']}] {role_name}:\n")
                    f.write(f"{msg['content']}\n")
                    f.write("-" * 40 + "\n\n")

                f.write("=" * 60 + "\n")
                f.write(f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"共 {len(self.chat_history)} 条消息\n")

            messagebox.showinfo("导出成功", f"聊天记录已导出到：\n{file_path}")

        except Exception as e:
            messagebox.showerror("导出失败", f"导出文件时发生错误：\n{str(e)}")


def main():
    root = tk.Tk()
    app = LocalAIChat(root)
    root.mainloop()


if __name__ == "__main__":
    main()