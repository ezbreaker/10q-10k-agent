#!/usr/bin/env python3
"""
简化的测试运行器
"""

import subprocess
import sys
import os

def run_tests():
    """运行所有测试"""
    print("🧪 InsightAgent MVP 测试套件")
    print("=" * 50)
    
    # 确保在正确的目录
    os.chdir(os.path.dirname(__file__))
    
    # 运行测试
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v",
        "--tb=short"  # 简短的错误信息
    ]
    
    print("📋 运行命令:", " ".join(cmd))
    print("=" * 50)
    
    result = subprocess.run(cmd)
    
    print("=" * 50)
    if result.returncode == 0:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 