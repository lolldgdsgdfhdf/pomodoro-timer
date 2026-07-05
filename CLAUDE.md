# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用指令

```bash
# 執行所有測試（無需 pytest，直接用 Python 跑）
python test_counter.py
python test_pomodoro_stats.py

# CLI 番茄鐘 — 開始 / 自訂時長 / 查看統計
python pomodoro_timer.py
python pomodoro_timer.py 10
python pomodoro_timer.py -s

# GUI 番茄鐘
python pomodoro_gui.py

# 計數器 CLI
python counter.py
```

**注意**：Windows 中文終端使用 GBK 編碼，執行含 emoji 的輸出時需加 `PYTHONIOENCODING=utf-8`：

```bash
PYTHONIOENCODING=utf-8 python pomodoro_timer.py -s
```

## 架構

```
pomodoro_stats.py         ← 共用資料層（單例：get_stats()）
    ├── JSON 原子讀寫 (_load / _save)
    ├── 統計查詢 (today_count, week_count, streak, daily_breakdown)
    └── snapshot() — 單次迭代聚合所有統計值

pomodoro_timer.py (CLI)   ← 命令列番茄鐘
    └── 依賴 get_stats() 記錄完成 + 顯示統計

pomodoro_gui.py (GUI)     ← tkinter 圖形界面番茄鐘 (PomodoroTimer 類別)
    └── 依賴 get_stats() 記錄完成 + show_stats() 統計視窗

counter.py                ← Counter 類別 + 獨立 CLI（與番茄鐘無關）
```

**核心模式**：
- `get_stats()` 回傳模組級 `PomodoroStats` 單例，所有模組共用同一個 JSON 檔案
- `snapshot()` 是效能關鍵：一次迭代取得所有統計，避免 `today_count` + `week_count` + `streak` + `daily_breakdown` 各自迭代（7 次 → 1 次）
- `_save()` 使用暫存檔 + `os.replace()` 做原子寫入，防止當機損毀資料
- `_load()` 驗證 JSON root 必須是 list，非 list 則回傳 `[]`
- CLI 和 GUI 各自實作計時邏輯（while 迴圈 vs threading.Thread），沒有共用計時引擎

## Git 工作流

```bash
# 標準流程：開分支 → 改 → 測試 → 提交 → 合併 main
git checkout -b feature/xxx
# ... 修改 ...
python test_counter.py && python test_pomodoro_stats.py
git add -A && git commit -m "描述"
git checkout main && git merge feature/xxx --no-ff -m "合併"
```

遠端：`origin` → `lolldgdsgdfhdf/pomodoro-timer`（GitHub）
