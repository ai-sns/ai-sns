#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""演示延迟导入的性能"""

import time
import sys

def test_first_import():
    """模拟第一次导入"""
    print("\n=== 测试 1: 首次导入（会慢）===")
    start = time.time()

    # 模拟我们的代码逻辑
    if 'Agent' not in sys.modules:
        print("首次导入 Agent 模块...")
        from Agent import Agent
        print(f"导入耗时: {time.time() - start:.2f} 秒")
    else:
        print("Agent 模块已在缓存中")

    return time.time() - start

def test_second_import():
    """模拟第二次导入"""
    print("\n=== 测试 2: 第二次导入（应该很快）===")
    start = time.time()

    # 再次导入同一个模块
    from Agent import Agent
    elapsed = time.time() - start
    print(f"导入耗时: {elapsed:.6f} 秒 (从缓存中获取)")

    return elapsed

def test_third_import():
    """模拟第三次导入"""
    print("\n=== 测试 3: 第三次导入（应该很快）===")
    start = time.time()

    # 再次导入
    from Agent import Agent
    elapsed = time.time() - start
    print(f"导入耗时: {elapsed:.6f} 秒 (从缓存中获取)")

    return elapsed

def main():
    print("=" * 60)
    print("Python import 缓存机制演示")
    print("=" * 60)

    # 检查是否已经导入过
    if 'Agent' in sys.modules:
        print("\n警告: Agent 模块已经被导入过了，清理缓存后重新测试...")
        del sys.modules['Agent']

    try:
        # 第一次导入
        time1 = test_first_import()

        # 第二次导入
        time2 = test_second_import()

        # 第三次导入
        time3 = test_third_import()

        # 总结
        print("\n" + "=" * 60)
        print("性能对比总结:")
        print("=" * 60)
        print(f"首次导入耗时: {time1:.2f} 秒")
        print(f"第二次导入耗时: {time2:.6f} 秒 (快 {time1/time2:.0f} 倍)")
        print(f"第三次导入耗时: {time3:.6f} 秒 (快 {time1/time3:.0f} 倍)")
        print("\n结论: 延迟导入只在首次慢，后续都是微秒级！")

    except Exception as e:
        print(f"\n错误: {e}")
        print("(如果在非虚拟环境中运行，可能缺少依赖)")

if __name__ == "__main__":
    main()
