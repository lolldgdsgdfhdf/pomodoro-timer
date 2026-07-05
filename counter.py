"""
计数器程序 - Counter Program
=============================
功能：
1. Counter 類別：可重複使用的計數器（加/減/重置/自訂步長）
2. 互動式 CLI：終端機操作介面
"""


class Counter:
    """一個多功能計數器類別，支援自訂步長與重置"""

    def __init__(self, start: int = 0, step: int = 1):
        self._count = start
        self._step = step

    @property
    def value(self) -> int:
        return self._count

    def increment(self) -> int:
        self._count += self._step
        return self._count

    def decrement(self) -> int:
        self._count -= self._step
        return self._count

    def reset(self, value: int = 0) -> None:
        self._count = value

    def __str__(self) -> str:
        return str(self._count)

    def __repr__(self) -> str:
        return f"Counter(value={self._count}, step={self._step})"


def main():
    """互動式 CLI 介面"""
    c = Counter()

    print("=" * 40)
    print("        欢迎使用计数器")
    print("=" * 40)
    print(f"\n当前计数: {c.value}")
    print("--- 操作菜单 ---")
    print("  +   : 加一步长")
    print("  -   : 减一步长")
    print("  r   : 重置为0")
    print("  q   : 退出")
    print("-" * 40)

    while True:
        cmd = input("\n请输入操作: ").strip().lower()

        if cmd == '+':
            c.increment()
            print(f"计数 + → 当前值: {c.value}")

        elif cmd == '-':
            c.decrement()
            print(f"计数 - → 当前值: {c.value}")

        elif cmd == 'r':
            c.reset()
            print(f"已重置 → 当前值: {c.value}")

        elif cmd == 'q':
            print(f"最终计数: {c.value}")
            print("程序已退出。")
            break

        else:
            print("无效操作，请重新输入。")


if __name__ == "__main__":
    main()