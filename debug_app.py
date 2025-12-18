#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本，用于查看app.py的错误信息
"""

import traceback

# 尝试导入app模块，并捕获错误
if __name__ == "__main__":
    try:
        import app
        print("✅ 成功导入app模块")
    except Exception as e:
        print("❌ 导入app模块失败")
        print("错误信息:")
        traceback.print_exc()
