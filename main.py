"""
送外卖模拟器 - 主启动文件
Food Delivery Simulator - Main Entry Point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')  # 设置matplotlib后端

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_system import GameGUI
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖文件都在同一目录下")
    sys.exit(1)

def check_dependencies():
    """检查依赖库"""
    required_packages = [
        'tkinter',
        'matplotlib',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"缺少以下依赖包: {', '.join(missing_packages)}\n"
        error_msg += "请使用以下命令安装:\n"
        error_msg += f"pip install {' '.join(missing_packages)}"
        
        print(error_msg)
        
        # 尝试显示GUI错误信息
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("依赖缺失", error_msg)
            root.destroy()
        except:
            pass
        
        return False
    
    return True

def main():
    """主函数"""
    print("启动送外卖模拟器...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # 创建并运行游戏
        game = GameGUI()
        print("游戏界面初始化完成")
        game.run()
        
    except Exception as e:
        error_msg = f"游戏启动失败: {e}"
        print(error_msg)
        
        # 显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动失败", error_msg)
            root.destroy()
        except:
            pass
        
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()