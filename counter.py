"""
计数器程序 - Counter Program
=============================
功能：
1. 加/减计数（支持自定义步长）
2. 重置归零
3. 退出程序
"""

def main():
    count = 0          # 当前计数值
    step = 1           # 加减步长（默认1）

    print("=" * 40)
    print("        欢迎使用计数器")
    print("=" * 40)
    print(f"\n当前计数: {count}")
    print(f"当前步长: {step}")
    print("\n--- 操作菜单 ---")
    print("  +   : 加一步长")
    print("  -   : 减一步长")
    print("  r   : 重置为0")
    print("  s   : 设置步长")
    print("  q   : 退出")
    print("-" * 40)

    while True:
        cmd = input("\n请输入操作: ").strip().lower()

        if cmd == '+':
            count += step
            print(f"计数 +{step} → 当前值: {count}")

        elif cmd == '-':
            count -= step
            print(f"计数 -{step} → 当前值: {count}")

        elif cmd == 'r':
            count = 0
            print(f"已重置 → 当前值: {count}")

        elif cmd == 's':
            try:
                new_step = input("请输入新的步长 (正整数): ").strip()
                new_step = int(new_step)
                if new_step <= 0:
                    print("步长必须为正整数，请重新输入。")
                else:
                    step = new_step
                    print(f"步长已设置为: {step}")
            except ValueError:
                print("输入无效，请输入正整数。")

        elif cmd == 'q':
            print(f"最终计数: {count}")
            print("程序已退出。")
            break

        else:
            print("无效操作，请重新输入。")

if __name__ == "__main__":
    main()