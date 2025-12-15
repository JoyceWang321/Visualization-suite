# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import BFS1
import DFS
import Sorting_pro


class AlgorithmVisualizationSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("算法可视化套件 - 小组项目")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')  # 修改背景色为深蓝色
        
        # 设置主题样式
        self.setup_style()
        self.setup_ui()
        
    def setup_style(self):
        """配置自定义样式"""
        style = ttk.Style()
        
        # 配置不同样式
        style.configure('Title.TLabel', 
                       font=('微软雅黑', 28, 'bold'),
                       foreground='#ecf0f1',  # 浅灰色文字
                       background='#2c3e50')
        
        style.configure('Subtitle.TLabel',
                       font=('微软雅黑', 14),
                       foreground='#bdc3c7',  # 中灰色文字
                       background='#2c3e50')
        
        style.configure('Card.TFrame',
                       relief='raised',
                       borderwidth=3)
        
        style.configure('CardTitle.TLabel',
                       font=('微软雅黑', 16, 'bold'),
                       foreground='#2c3e50')  # 深蓝色文字
        
        style.configure('CardDesc.TLabel',
                       font=('微软雅黑', 11),
                       foreground='#7f8c8d',  # 深灰色文字
                       wraplength=200)
        
        style.configure('Accent.TButton',
                       font=('微软雅黑', 12, 'bold'),
                       foreground='#ffffff',
                       background='#e74c3c',  # 红色按钮
                       padding=(20, 10))
        
        style.configure('Status.TLabel',
                       font=('微软雅黑', 10),
                       foreground='#95a5a6',  # 浅灰色
                       background='#34495e')  # 稍浅的背景色
        
    def setup_ui(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding="0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域（深色背景）
        title_frame = ttk.Frame(main_frame, style='Title.TFrame')
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # 渐变背景效果（使用Canvas模拟）
        self.canvas = tk.Canvas(title_frame, height=200, bg='#2c3e50', highlightthickness=0)
        self.canvas.pack(fill=tk.X)
        
        # 在Canvas上绘制渐变和内容
        self.draw_gradient()
        
        # 标题文字
        self.canvas.create_text(450, 80, 
                               text="算法可视化套件", 
                               font=('微软雅黑', 32, 'bold'),
                               fill='#ecf0f1')  # 白色文字
        
        # 副标题
        self.canvas.create_text(450, 130, 
                               text="经典算法图形化演示平台", 
                               font=('微软雅黑', 16),
                               fill='#bdc3c7')  # 浅灰色文字
        
        # 团队信息
        team_frame = ttk.Frame(title_frame, style='Title.TFrame')
        team_frame.pack(fill=tk.X, pady=(0, 20))
        
        team_label = ttk.Label(team_frame, 
                              text="开发团队：汪萌萌（组长） • 蓝冰云 • 房盈杉 • 罗建然",
                              style='Subtitle.TLabel')
        team_label.pack(pady=10)
        
        # 主要内容区域（浅色背景）
        content_frame = ttk.Frame(main_frame, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 算法选择区域
        algo_frame = ttk.LabelFrame(content_frame, 
                                   text="🎯 选择算法模块", 
                                   padding="30",
                                   style='Card.TFrame')
        algo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建三个算法模块的卡片
        self.create_algorithm_card(algo_frame, "🔍 BFS算法可视化", 
                                 "广度优先搜索算法\n\n实现者：房盈杉\n班级：生信C2302", 
                                 self.open_bfs, 0, '#3498db')  # 蓝色
        
        self.create_algorithm_card(algo_frame, "🌳 DFS算法可视化", 
                                 "深度优先搜索算法\n\n实现者：罗建然\n班级：生信C2302", 
                                 self.open_dfs, 1, '#2ecc71')  # 绿色
        
        self.create_algorithm_card(algo_frame, "📊 排序算法可视化", 
                                 "三种比较排序算法\n\n实现者：蓝冰云\n优化：全体\n班级：生信C2301", 
                                 self.open_sorting, 2, '#e74c3c')  # 红色
        
        # 状态栏（深色背景）
        status_frame = ttk.Frame(main_frame, style='Title.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 0))
        
        self.status_var = tk.StringVar(value="🟢 就绪 - 请选择要运行的算法模块")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        version_label = ttk.Label(status_frame, 
                                 text="版本 2.0 • 界面整合：汪萌萌 • 2025年12月",
                                 style='Status.TLabel')
        version_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # 配置网格权重
        algo_frame.columnconfigure(0, weight=1)
        algo_frame.columnconfigure(1, weight=1)
        algo_frame.columnconfigure(2, weight=1)
    
    def draw_gradient(self):
        """绘制渐变背景"""
        width = 900
        height = 200
        for i in range(height):
            # 从深蓝到稍浅的蓝色渐变
            r = int(44 + (52 - 44) * i / height)    # 2c to 34 (red)
            g = int(62 + (73 - 62) * i / height)    # 3e to 49 (green)
            b = int(80 + (94 - 80) * i / height)     # 50 to 5e (blue)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, width, i, fill=color)
    
    def create_algorithm_card(self, parent, title, description, command, column, color):
        """创建算法卡片"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=0, column=column, padx=15, pady=20, sticky='nsew')
        card_frame.configure(relief='raised', borderwidth=2)
        
        # 卡片头部（带颜色的标题栏）
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill=tk.X, pady=(0, 0))
        
        # 标题标签
        title_label = ttk.Label(header_frame, 
                               text=title, 
                               font=('微软雅黑', 16, 'bold'),
                               foreground='white',
                               background=color,
                               padding=(20, 15))
        title_label.pack(fill=tk.X)
        
        # 内容区域
        content_frame = ttk.Frame(card_frame, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 描述文本
        desc_label = ttk.Label(content_frame, 
                              text=description, 
                              font=('微软雅黑', 11),
                              foreground='#2c3e50',
                              justify=tk.CENTER,
                              wraplength=200)
        desc_label.pack(pady=15)
        
        # 启动按钮
        open_btn = tk.Button(content_frame, 
                            text="🚀 启动模块", 
                            command=command,
                            font=('微软雅黑', 12, 'bold'),
                            bg=color,
                            fg='white',
                            padx=30,
                            pady=10,
                            borderwidth=0,
                            cursor='hand2')
        open_btn.pack(pady=10)
        
        # 添加悬停效果
        open_btn.bind('<Enter>', lambda e: open_btn.config(bg=self.lighten_color(color)))
        open_btn.bind('<Leave>', lambda e: open_btn.config(bg=color))
    
    def lighten_color(self, color, factor=0.2):
        """使颜色变亮"""
        # 移除#号并转换为RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # 增加亮度
        light_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        
        # 转换回十六进制
        return f'#{light_rgb[0]:02x}{light_rgb[1]:02x}{light_rgb[2]:02x}'
    
    def open_bfs(self):
        self.status_var.set("🔵 正在启动BFS算法可视化模块...")
        self.root.withdraw()
        bfs_window = tk.Toplevel(self.root)
        bfs_window.title("BFS算法可视化")
        bfs_window.geometry("1000x700")
        BFS1.BFSVisualizer(bfs_window)
        bfs_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(bfs_window))
    
    def open_dfs(self):
        self.status_var.set("🟢 正在启动DFS算法可视化模块...")
        self.root.withdraw()
        dfs_window = tk.Toplevel(self.root)
        dfs_window.title("DFS算法可视化")
        dfs_window.geometry("1000x700")
        DFS.DFSVisualizer(dfs_window)
        dfs_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(dfs_window))
    
    def open_sorting(self):
        self.status_var.set("🔴 正在启动排序算法可视化模块...")
        self.root.withdraw()
        sorting_window = tk.Toplevel(self.root)
        sorting_window.title("排序算法可视化")
        sorting_window.geometry("1000x700")
        Sorting_pro.SortingVisualizer(sorting_window)
        sorting_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(sorting_window))
    
    def on_subwindow_close(self, window):
        window.destroy()
        self.root.deiconify()
        self.status_var.set("🟢 模块已关闭 - 请选择要运行的算法模块")

def main():
    root = tk.Tk()
    app = AlgorithmVisualizationSuite(root)
    root.mainloop()

if __name__ == "__main__":
    main()
