"""
PomodoroStats 單元測試
"""
import os
import json
import tempfile
from pomodoro_stats import PomodoroStats


def test_add_record():
    """新增記錄後總數增加"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s = PomodoroStats(filepath=tmp)
        assert s.total_count == 0
        s.add(25)
        assert s.total_count == 1
        assert s.total_minutes == 25
        s.add(15)
        assert s.total_count == 2
        assert s.total_minutes == 40
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_today_count():
    """今日記錄數正確"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s = PomodoroStats(filepath=tmp)
        s.add(25)
        s.add(30)
        assert s.today_count() == 2
        assert s.today_minutes() == 55
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_total_hours():
    """時長換算正確"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s = PomodoroStats(filepath=tmp)
        s.add(30)
        s.add(30)
        assert s.total_hours == 1.0
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_persistence():
    """記錄持久化：關掉重開還在"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s1 = PomodoroStats(filepath=tmp)
        s1.add(25)
        s1.add(50)

        s2 = PomodoroStats(filepath=tmp)
        assert s2.total_count == 2
        assert s2.total_minutes == 75
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_streak():
    """今日有記錄，streak >= 1"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s = PomodoroStats(filepath=tmp)
        s.add(25)
        assert s.streak() >= 1
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_summary():
    """summary 回傳字串包含關鍵資訊"""
    tmp = tempfile.mktemp(suffix=".json")
    try:
        s = PomodoroStats(filepath=tmp)
        s.add(25)
        output = s.summary()
        assert "总完成数" in output
        assert "总专注时长" in output
        assert "连续打卡" in output
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    tests = [
        test_add_record, test_today_count, test_total_hours,
        test_persistence, test_streak, test_summary
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  [PASS] {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
