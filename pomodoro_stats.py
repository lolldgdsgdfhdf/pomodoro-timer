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

    @staticmethod
    def _parse_date(record: dict):
        """安全解析 timestamp，失敗回傳 epoch"""
        try:
            return datetime.fromisoformat(record.get("timestamp", "")).date()
        except (ValueError, TypeError):
            return datetime(1970, 1, 1).date()

    def add(self, minutes: int, task: str = ""):
        """新增一筆完成記錄"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "duration_minutes": minutes,
            "task": task or "未命名任務",
        }
        self.records.append(record)
        self._save()
        return record

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def total_minutes(self) -> int:
        return sum(r["duration_minutes"] for r in self.records)

    @property
    def total_hours(self) -> float:
        return round(self.total_minutes / 60, 1)

    def today_count(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(1 for r in self.records if r["date"] == today)

    def today_minutes(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(r["duration_minutes"] for r in self.records if r["date"] == today)

    def week_count(self) -> int:
        """本週（週一到今天）"""
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        count = 0
        for r in self.records:
            d = self._parse_date(r)
            if monday <= d <= today:
                count += 1
        return count

    def week_minutes(self) -> int:
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        total = 0
        for r in self.records:
            d = self._parse_date(r)
            if monday <= d <= today:
                total += r["duration_minutes"]
        return total

    def daily_breakdown(self, days: int = 7) -> dict:
        """最近 N 天的每日明細"""
        today = datetime.now().date()
        breakdown = defaultdict(lambda: {"count": 0, "minutes": 0})
        for r in self.records:
            d = self._parse_date(r)
            if (today - d).days < days:
                breakdown[r["date"]]["count"] += 1
                breakdown[r["date"]]["minutes"] += r["duration_minutes"]
        return dict(sorted(breakdown.items()))

    def streak(self) -> int:
        """連續打卡天數（從今天往回算）"""
        today = datetime.now().date()
        days_with_records = set()
        for r in self.records:
            days_with_records.add(self._parse_date(r))

        streak = 0
        check = today
        while check in days_with_records:
            streak += 1
            check -= timedelta(days=1)
        return streak

    def summary(self) -> str:
        """文字摘要"""
        lines = []
        lines.append("=" * 50)
        lines.append("          📊 番茄鐘統計")
        lines.append("=" * 50)
        lines.append(f"  總完成數：{self.total_count} 個番茄鐘")
        lines.append(f"  總專注時長：{self.total_hours} 小時 ({self.total_minutes} 分鐘)")
        lines.append(f"  今日完成：{self.today_count()} 個 ({self.today_minutes()} 分鐘)")
        lines.append(f"  本週完成：{self.week_count()} 個 ({self.week_minutes()} 分鐘)")
        lines.append(f"  🔥 連續打卡：{self.streak()} 天")
        lines.append("-" * 50)

        breakdown = self.daily_breakdown(7)
        if breakdown:
            lines.append("  最近 7 天：")
            for date, data in breakdown.items():
                bar = "█" * min(data["count"], 20)
                lines.append(f"    {date}  {bar} {data['count']}個 ({data['minutes']}分鐘)")
        lines.append("=" * 50)
        return "\n".join(lines)


# 全域單例
_stats_instance = None


def get_stats() -> PomodoroStats:
    global _stats_instance
    if _stats_instance is None:
        _stats_instance = PomodoroStats()
    return _stats_instance
