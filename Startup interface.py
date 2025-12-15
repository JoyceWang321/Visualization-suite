import tkinter as tk
from tkinter import ttk, messagebox
import BFS1
import DFS
import Sorting

class AlgorithmVisualizationSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("算法可视化套件 - 小组项目")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题和小组信息
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(title_frame, 
                               text="算法可视化套件", 
                               font=("Arial", 24, "bold"),
                               foreground="#2c3e50")
        title_label.pack()
        
        team_label = ttk.Label(title_frame,
                              text="开发团队：汪萌萌（组长）、房盈杉、蓝冰云、罗建然",
                              font=("Arial", 12),
                              foreground="#7f8c8d")
        team_label.pack(pady=10)
        
        # 算法选择区域
        algo_frame = ttk.LabelFrame(self.root, text="选择算法模块", padding="30")
        algo_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # 创建三个算法模块的卡片
        self.create_algorithm_card(algo_frame, "BFS算法可视化", 
                                 "广度优先搜索算法\n实现者：房盈杉", 
                                 self.open_bfs, 0)
        
        self.create_algorithm_card(algo_frame, "DFS算法可视化", 
                                 "深度优先搜索算法\n实现者：罗建然", 
                                 self.open_dfs, 1)
        
        self.create_algorithm_card(algo_frame, "排序算法可视化", 
                                 "三种比较排序算法\n实现者：蓝冰云", 
                                 self.open_sorting, 2)
        
        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_var = tk.StringVar(value="就绪 - 请选择要运行的算法模块")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(status_frame, text="版本 1.0 - 汪萌萌（界面整合）")
        version_label.pack(side=tk.RIGHT)
    
    def create_algorithm_card(self, parent, title, description, command, column):
        card_frame = ttk.Frame(parent, relief='raised', borderwidth=2)
        card_frame.grid(row=0, column=column, padx=20, pady=20, sticky='nsew')
        
        title_label = ttk.Label(card_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        desc_label = ttk.Label(card_frame, text=description, justify=tk.CENTER)
        desc_label.pack(pady=10, padx=20)
        
        open_btn = ttk.Button(card_frame, text="启动", command=command)
        open_btn.pack(pady=20)
        
        parent.columnconfigure(column, weight=1)
    
    def open_bfs(self):
        self.status_var.set("正在启动BFS算法可视化模块...")
        self.root.withdraw()  # 隐藏主窗口
        bfs_window = tk.Toplevel(self.root)
        bfs_window.title("BFS算法可视化 - 房盈杉")
        BFS1.BFSVisualizer(bfs_window)
        bfs_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(bfs_window))
    
    def open_dfs(self):
        self.status_var.set("正在启动DFS算法可视化模块...")
        self.root.withdraw()
        dfs_window = tk.Toplevel(self.root)
        dfs_window.title("DFS算法可视化 - 罗建然")
        DFS.DFSVisualizer(dfs_window)
        dfs_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(dfs_window))
    
    def open_sorting(self):
        self.status_var.set("正在启动排序算法可视化模块...")
        self.root.withdraw()
        sorting_window = tk.Toplevel(self.root)
        sorting_window.title("排序算法可视化 - 蓝冰云")
        Sorting.SortingVisualizer(sorting_window)
        sorting_window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(sorting_window))
    
    def on_subwindow_close(self, window):
        window.destroy()
        self.root.deiconify()  # 重新显示主窗口
        self.status_var.set("模块已关闭 - 请选择要运行的算法模块")

def main():
    root = tk.Tk()
    app = AlgorithmVisualizationSuite(root)
    root.mainloop()

if __name__ == "__main__":
    main()