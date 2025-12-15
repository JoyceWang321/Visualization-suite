import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, FancyBboxPatch, ConnectionPatch
import numpy as np
import random
import time
from threading import Thread
from collections import deque
import math


class BFSVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Breadth-First Search Visualization")
        self.root.geometry("1000x700")

        # 图数据结构
        self.graph = {}
        self.nodes = {}  # 节点位置信息
        self.edges = []  # 边信息
        self.node_radius = 30
        self.node_count = 8  # 默认节点数量

        # 算法状态
        self.speed = 0.5
        self.is_running = False
        self.paused = False
        self.stop_flag = False
        self.start_node = None
        self.visited_order = []
        self.visited = set()
        self.queue = deque()

        # 创建UI
        self.setup_ui()

        # 初始化图
        self.generate_graph()

    def setup_ui(self):
        # 创建主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="Breadth-First Search (BFS) Visualization",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 算法控制部分
        algo_control_frame = ttk.LabelFrame(main_frame, text="Algorithm Controls", padding="10")
        algo_control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 节点数量控制
        ttk.Label(algo_control_frame, text="Number of Nodes:").grid(row=0, column=0, sticky=tk.W)
        self.node_var = tk.IntVar(value=self.node_count)
        node_scale = ttk.Scale(algo_control_frame, from_=5, to=15, variable=self.node_var,
                               orient=tk.HORIZONTAL, command=self.on_node_count_change)
        node_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        self.node_label = ttk.Label(algo_control_frame, text=str(self.node_count))
        self.node_label.grid(row=0, column=2, padx=(0, 10))

        # 生成新图按钮
        ttk.Button(algo_control_frame, text="Generate New Graph",
                   command=self.generate_graph).grid(row=0, column=3, padx=(10, 0))

        # 起点选择
        ttk.Label(algo_control_frame, text="Start Node:").grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
        self.start_node_var = tk.StringVar(value="0")
        self.start_node_combo = ttk.Combobox(algo_control_frame, textvariable=self.start_node_var,
                                             state="readonly", width=5)
        self.start_node_combo.grid(row=0, column=5, padx=(5, 10))

        # 画布区域
        self.figure = plt.Figure(figsize=(10, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, main_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

        # 通用动画控制
        control_frame = ttk.LabelFrame(main_frame, text="Animation Controls", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # 速度控制
        ttk.Label(control_frame, text="Speed:").grid(row=0, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=self.speed)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.speed_var,
                                orient=tk.HORIZONTAL, command=self.on_speed_change)
        speed_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        self.speed_label = ttk.Label(control_frame, text=f"{self.speed:.1f}x")
        self.speed_label.grid(row=0, column=2, padx=(0, 20))

        # 控制按钮
        self.start_button = ttk.Button(control_frame, text="Start BFS", command=self.start_bfs)
        self.start_button.grid(row=0, column=3, padx=(10, 5))

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_bfs, state="disabled")
        self.pause_button.grid(row=0, column=4, padx=5)

        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=5, padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="Ready - Click a node to set as start node")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=6, padx=(20, 0))

        # 算法说明
        explanation = """
BFS Algorithm:
1. Start from the selected node
2. Visit all neighbors at the current depth before moving to the next level
3. Use a queue to keep track of nodes to visit
4. Mark visited nodes to avoid revisiting

Colors:
- Blue: Unvisited nodes
- Red: Currently processing node
- Green: Visited nodes
- Yellow: Nodes in the queue
        """
        explanation_label = ttk.Label(main_frame, text=explanation, justify=tk.LEFT)
        explanation_label.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)

        # 配置列权重
        algo_control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(1, weight=1)

    def generate_graph(self):
        """生成随机图"""
        self.node_count = self.node_var.get()
        self.graph = {}
        self.nodes = {}
        self.edges = []

        # 生成节点位置（圆形排列）
        center_x, center_y = 500, 250
        radius = 200

        for i in range(self.node_count):
            angle = 2 * math.pi * i / self.node_count
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.nodes[i] = (x, y)

        # 生成随机边（确保图是连通的）
        # 首先创建一个环保证连通性
        for i in range(self.node_count):
            self.graph[i] = []
            next_node = (i + 1) % self.node_count
            self.graph[i].append(next_node)
            self.edges.append((i, next_node))

        # 添加一些随机边
        for i in range(self.node_count):
            # 每个节点额外添加1-2条边
            extra_edges = random.randint(1, 2)
            for _ in range(extra_edges):
                target = random.randint(0, self.node_count - 1)
                if target != i and target not in self.graph[i] and (i, target) not in self.edges:
                    self.graph[i].append(target)
                    self.edges.append((i, target))

        # 更新起点选择框
        self.start_node_combo['values'] = list(str(i) for i in range(self.node_count))
        self.start_node_var.set("0")
        self.start_node = 0

        # 重置算法状态
        self.reset()

    def draw_graph(self, current_node=None, visited=None, queue=None):
        """绘制图"""
        self.ax.clear()
        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(0, 500)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        if visited is None:
            visited = set()
        if queue is None:
            queue = set()

        # 绘制边
        for edge in self.edges:
            node1, node2 = edge
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]

            # 检查是否是有向边（这里我们假设是无向图）
            if (node2, node1) in self.edges and node1 > node2:
                continue  # 避免重复绘制双向边

            # 绘制边
            line = plt.Line2D([x1, x2], [y1, y2], color='black', linewidth=2)
            self.ax.add_line(line)

            # 添加边的权重（随机）
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            self.ax.text(mid_x, mid_y, str(random.randint(1, 10)),
                         fontsize=10, ha='center', va='center',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        # 绘制节点
        for node, (x, y) in self.nodes.items():
            # 确定节点颜色
            if node == current_node:
                color = 'red'  # 当前正在处理的节点
            elif node in visited:
                color = 'green'  # 已访问的节点
            elif node in queue:
                color = 'yellow'  # 队列中的节点
            else:
                color = 'lightblue'  # 未访问的节点

            # 绘制节点
            circle = plt.Circle((x, y), self.node_radius, color=color, ec='black', linewidth=2)
            self.ax.add_patch(circle)

            # 添加节点标签
            self.ax.text(x, y, str(node), fontsize=14, ha='center', va='center', fontweight='bold')

        # 添加标题
        self.ax.set_title(f"Breadth-First Search - Graph with {self.node_count} nodes", fontsize=16)

        self.canvas.draw()

    def on_node_count_change(self, value):
        self.node_count = int(float(value))
        self.node_label.config(text=str(self.node_count))
        self.generate_graph()

    def on_speed_change(self, value):
        self.speed = float(value)
        self.speed_label.config(text=f"{self.speed:.1f}x")

    def on_canvas_click(self, event):
        """处理画布点击事件，选择起点"""
        if self.is_running:
            return

        # 检查是否点击了节点
        for node, (x, y) in self.nodes.items():
            distance = math.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
            if distance <= self.node_radius:
                self.start_node = node
                self.start_node_var.set(str(node))
                self.status_var.set(f"Start node set to {node}. Click 'Start BFS' to begin.")
                self.draw_graph()
                break

    def start_bfs(self):
        if self.is_running or self.start_node is None:
            return

        self.is_running = True
        self.paused = False
        self.stop_flag = False
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.status_var.set("Running BFS...")

        # 初始化BFS状态
        self.visited = set()
        self.queue = deque([self.start_node])
        self.visited_order = []

        # 在新线程中运行BFS算法
        self.bfs_thread = Thread(target=self.run_bfs)
        self.bfs_thread.daemon = True
        self.bfs_thread.start()

    def pause_bfs(self):
        if self.paused:
            self.paused = False
            self.pause_button.config(text="Pause")
            self.status_var.set("Running BFS...")
        else:
            self.paused = True
            self.pause_button.config(text="Resume")
            self.status_var.set("Paused")

    def reset(self):
        self.stop_flag = True
        self.is_running = False
        self.paused = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause")
        self.status_var.set("Ready - Click a node to set as start node")
        self.draw_graph()

    def run_bfs(self):
        """执行BFS算法并更新可视化"""
        try:
            while self.queue and not self.stop_flag:
                # 处理暂停
                while self.paused and not self.stop_flag:
                    time.sleep(0.1)

                if self.stop_flag:
                    break

                # 从队列中取出当前节点
                current_node = self.queue.popleft()

                # 标记为已访问
                self.visited.add(current_node)
                self.visited_order.append(current_node)

                # 更新可视化 - 显示当前节点
                queue_set = set(self.queue)
                self.root.after(0, self.draw_graph, current_node, self.visited, queue_set)
                self.root.after(0, self.status_var.set, f"Visiting node {current_node}")
                time.sleep(1.0 / self.speed)

                # 处理暂停
                while self.paused and not self.stop_flag:
                    time.sleep(0.1)

                if self.stop_flag:
                    break

                # 将未访问的邻居加入队列
                for neighbor in self.graph[current_node]:
                    if neighbor not in self.visited and neighbor not in self.queue:
                        self.queue.append(neighbor)

                # 更新可视化 - 显示队列中的节点
                queue_set = set(self.queue)
                self.root.after(0, self.draw_graph, current_node, self.visited, queue_set)
                self.root.after(0, self.status_var.set,
                                f"Visited node {current_node}. Queue: {list(self.queue)}")
                time.sleep(1.0 / self.speed)

            if not self.stop_flag:
                self.root.after(0, self.bfs_completed)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset)

    def bfs_completed(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.status_var.set(f"BFS completed! Visited order: {self.visited_order}")
        self.draw_graph(visited=self.visited)


def main():
    root = tk.Tk()
    app = BFSVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()