"""
Counter 的單元測試
用 pytest 跑：pytest test_counter.py -v
也可以直接跑：python test_counter.py
"""

from counter import Counter


def test_initial_value():
    """新計數器應該從 0 開始"""
    c = Counter()
    assert c.value == 0


def test_custom_start_value():
    """自訂起始值"""
    c = Counter(start=42)
    assert c.value == 42


def test_increment():
    """increment 應該加上步長"""
    c = Counter(step=3)
    assert c.increment() == 3
    assert c.increment() == 6
    assert c.value == 6


def test_decrement():
    """decrement 應該減去步長"""
    c = Counter(start=10, step=2)
    assert c.decrement() == 8
    assert c.decrement() == 6


def test_reset():
    """reset 應該回到指定值"""
    c = Counter(start=100)
    c.increment()
    c.increment()
    c.reset(50)
    assert c.value == 50


def test_reset_default_zero():
    """reset() 不加參數應該回到 0"""
    c = Counter(start=999)
    c.reset()
    assert c.value == 0


def test_str_repr():
    """字串表示應該正確"""
    c = Counter(start=5, step=2)
    assert str(c) == "5"
    assert repr(c) == "Counter(value=5, step=2)"


def test_negative_step():
    """負步長：increment 會減少、decrement 會增加"""
    c = Counter(start=10, step=-3)
    assert c.increment() == 7    # 10 + (-3) = 7
    assert c.decrement() == 10   # 7 - (-3) = 10


if __name__ == "__main__":
    # 簡易測試執行器（不依賴 pytest）
    tests = [
        test_initial_value, test_custom_start_value,
        test_increment, test_decrement, test_reset,
        test_reset_default_zero, test_str_repr, test_negative_step
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  [PASS] {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
