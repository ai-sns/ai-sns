#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 API server 导入速度"""

import sys
import time

print('开始导入 api_server...')
start_time = time.time()

try:
    import api_server
    elapsed = time.time() - start_time
    print(f'导入成功，耗时: {elapsed:.2f} 秒')
    print('Agent 模块未在启动时导入，只会在首次调用 /api/chat 时导入')
except Exception as e:
    print(f'导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
