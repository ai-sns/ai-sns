#!/usr/bin/env python3
import platform, os, psutil
print("=" * 50)
print("真实System Check Skill执行")
print("=" * 50)
print(f"\n操作系统: {platform.system()} {platform.release()}")
print(f"Python版本: {platform.python_version()}")
print(f"处理器: {platform.processor()}")
print(f"主机名: {platform.node()}")
try:
    print(f"CPU使用率: {psutil.cpu_percent()}%")
    print(f"内存使用: {psutil.virtual_memory().percent}%")
except:
    print("(psutil未安装，无法获取CPU/内存信息)")
print(f"当前目录: {os.getcwd()}")
print("\n✓ 系统检查完成!")
