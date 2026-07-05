# 🍅 Pomodoro Timer 番茄鐘計時器

多功能番茄鐘，支援 CLI 命令列與 GUI 圖形界面。

## 功能

- ⏱️ **番茄鐘倒數計時** — 預設 25 分鐘，可自訂時長
- ▶️ **暫停 / 繼續** — 隨時中斷不影響計時
- 🔄 **重置** — 一鍵重新開始
- 📊 **統計記錄** — 自動記錄每次完成，追蹤每日/每週/總計
- 🔥 **連續打卡** — 激勵每天保持習慣
- 💾 **JSON 持久化** — 數據自動存檔
- 🎵 **音樂提醒** — GUI 版時間到自動響鈴
- 🖥️ **雙模式** — CLI 輕量版 + GUI 圖形版

## 快速開始

```bash
# CLI 版 — 預設 25 分鐘
python pomodoro_timer.py

# CLI 版 — 自訂時長（例如 10 分鐘）
python pomodoro_timer.py 10

# CLI 版 — 查看統計
python pomodoro_timer.py -s

# GUI 版 — 圖形界面
python pomodoro_gui.py
```

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `pomodoro_timer.py` | CLI 命令列番茄鐘 |
| `pomodoro_gui.py` | GUI 圖形界面番茄鐘 |
| `pomodoro_stats.py` | 統計模組（共用） |
| `counter.py` | 計數器工具 |
| `test_counter.py` | 計數器單元測試 |
| `test_pomodoro_stats.py` | 統計模組單元測試 |

## 技術棧

- Python 3
- tkinter（GUI）
- JSON（資料持久化）

## 最近更新

- 🆕 統計記錄功能（2026-07-05）
  - 每日/每週/總計完成數
  - 連續打卡天數
  - 最近 7 天明細（長條圖）
- Counter 類別重構 + 單元測試
