"""
番茄鐘統計模組 - Pomodoro Statistics
=====================================
記錄完成的番茄鐘，支援每日/每週/總計統計，資料存為 JSON。
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# 安全取得 stats 檔案路徑：fallback 到使用者家目錄
try:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _BASE_DIR = os.path.expanduser("~")
STATS_FILE = os.path.join(_BASE_DIR, "pomodoro_stats.json")


class PomodoroStats:
    """番茄鐘統計追蹤器"""

    def __init__(self, filepath: str = STATS_FILE):
        self.filepath = filepath
        self.records = self._load()

    def _load(self) -> list:
        """從 JSON 讀取歷史記錄"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        """原子寫入 JSON（先寫暫存檔再更名，避免當機損毀資料）"""
        tmp = self.filepath + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.filepath)

    def add(self, minutes: int, task: str = ""):
        """新增一筆完成記錄"""
        now = datetime.now()
        record = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "duration_minutes": minutes,
            "task": task or "未命名任務",
        }
        self.records.append(record)
        self._save()
        return record

    # ── 屬性 ──────────────────────────────────

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def total_minutes(self) -> int:
        return sum(r["duration_minutes"] for r in self.records)

    @property
    def total_hours(self) -> float:
        return round(self.total_minutes / 60, 1)

    # ── 輔助：篩選記錄 ────────────────────────

    def _today_records(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return [r for r in self.records if r["date"] == today]

    def _week_records(self):
        today = datetime.now().date()
        monday_str = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        return [r for r in self.records if monday_str <= r["date"] <= today_str]

    # ── 單日 / 單週統計 ──────────────────────

    def today_count(self) -> int:
        return len(self._today_records())

    def today_minutes(self) -> int:
        return sum(r["duration_minutes"] for r in self._today_records())

    def week_count(self) -> int:
        return len(self._week_records())

    def week_minutes(self) -> int:
        return sum(r["duration_minutes"] for r in self._week_records())

    # ── 明細 / 連續 ──────────────────────────

    def daily_breakdown(self, days: int = 7) -> dict:
        """最近 N 天的每日明細"""
        cutoff = (datetime.now().date() - timedelta(days=days)).strftime("%Y-%m-%d")
        breakdown = defaultdict(lambda: {"count": 0, "minutes": 0})
        for r in self.records:
            if r["date"] >= cutoff:
                breakdown[r["date"]]["count"] += 1
                breakdown[r["date"]]["minutes"] += r["duration_minutes"]
        return dict(sorted(breakdown.items()))

    def streak(self) -> int:
        """連續打卡天數（從今天往回算）"""
        today = datetime.now().date()
        days_with_records = {r["date"] for r in self.records}

        streak = 0
        check = today
        while check.strftime("%Y-%m-%d") in days_with_records:
            streak += 1
            check -= timedelta(days=1)
        return streak

    # ── 聚合快照：一次迭代取得所有統計 ──────

    def snapshot(self) -> dict:
        """單次迭代計算所有統計值"""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        monday_str = (now.date() - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        cutoff_7d = (now.date() - timedelta(days=7)).strftime("%Y-%m-%d")

        snap = {
            "total_count": 0,
            "total_minutes": 0,
            "today_count": 0,
            "today_minutes": 0,
            "week_count": 0,
            "week_minutes": 0,
            "streak_dates": set(),
            "daily": defaultdict(lambda: {"count": 0, "minutes": 0}),
        }

        for r in self.records:
            mins = r["duration_minutes"]
            snap["total_count"] += 1
            snap["total_minutes"] += mins

            if r["date"] == today_str:
                snap["today_count"] += 1
                snap["today_minutes"] += mins

            if r["date"] >= monday_str:
                snap["week_count"] += 1
                snap["week_minutes"] += mins

            if r["date"] >= cutoff_7d:
                snap["daily"][r["date"]]["count"] += 1
                snap["daily"][r["date"]]["minutes"] += mins

            snap["streak_dates"].add(r["date"])

        # 計算連續天數
        today_date = now.date()
        streak = 0
        check = today_date
        while check.strftime("%Y-%m-%d") in snap["streak_dates"]:
            streak += 1
            check -= timedelta(days=1)
        snap["streak"] = streak
        snap["total_hours"] = round(snap["total_minutes"] / 60, 1)

        return snap

    # ── CLI 展示（純字串格式化） ─────────────

    def summary(self) -> str:
        """文字摘要"""
        s = self.snapshot()
        lines = [
            "=" * 50,
            "          📊 番茄鐘統計",
            "=" * 50,
            f"  總完成數：{s['total_count']} 個番茄鐘",
            f"  總專注時長：{s['total_hours']} 小時 ({s['total_minutes']} 分鐘)",
            f"  今日完成：{s['today_count']} 個 ({s['today_minutes']} 分鐘)",
            f"  本週完成：{s['week_count']} 個 ({s['week_minutes']} 分鐘)",
            f"  🔥 連續打卡：{s['streak']} 天",
            "-" * 50,
        ]
        if s["daily"]:
            lines.append("  最近 7 天：")
            for date, data in sorted(s["daily"].items()):
                bar = "█" * min(data["count"], 20)
                lines.append(f"    {date}  {bar} {data['count']}個 ({data['minutes']}分鐘)")
        lines.append("=" * 50)
        return "\n".join(lines)


# 模組級單例（Python 保證只初始化一次）
_stats = PomodoroStats()


def get_stats() -> PomodoroStats:
    return _stats
