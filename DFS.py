# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import numpy as np
import random
import time
from threading import Thread
import math


class DFSVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Depth-First Search Visualization")
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
        self.stack = []  # DFS使用栈而不是队列
        self.current_path = []  # 当前路径

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
        title_label = ttk.Label(main_frame, text="Depth-First Search (DFS) Visualization",
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
        self.start_button = ttk.Button(control_frame, text="Start DFS", command=self.start_dfs)
        self.start_button.grid(row=0, column=3, padx=(10, 5))

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_dfs, state="disabled")
        self.pause_button.grid(row=0, column=4, padx=5)

        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=5, padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="Ready - Click a node to set as start node")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=6, padx=(20, 0))

        # 算法说明
        explanation = """
DFS Algorithm:
1. Start from the selected node
2. Explore as far as possible along each branch before backtracking
3. Use a stack to keep track of nodes to visit (or recursion)
4. Mark visited nodes to avoid revisiting

DFS vs BFS:
- DFS goes deep into the graph, BFS explores level by level
- DFS uses a stack, BFS uses a queue
- DFS is better for pathfinding in deep graphs, BFS for shortest path

Colors:
- Blue: Unvisited nodes
- Red: Currently processing node
- Green: Visited nodes
- Yellow: Nodes in the stack
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

    def draw_graph(self, current_node=None, visited=None, stack=None, path=None):
        """绘制图"""
        self.ax.clear()
        self.ax.set_xlim(0, 1000)
        self.ax.set_ylim(0, 500)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        if visited is None:
            visited = set()
        if stack is None:
            stack = set()
        if path is None:
            path = []

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

        # 绘制节点
        for node, (x, y) in self.nodes.items():
            # 确定节点颜色
            if node == current_node:
                color = 'red'  # 当前正在处理的节点
            elif node in visited:
                color = 'green'  # 已访问的节点
            elif node in stack:
                color = 'yellow'  # 栈中的节点
            else:
                color = 'lightblue'  # 未访问的节点

            # 绘制节点
            circle = plt.Circle((x, y), self.node_radius, color=color, ec='black', linewidth=2)
            self.ax.add_patch(circle)

            # 添加节点标签
            self.ax.text(x, y, str(node), fontsize=14, ha='center', va='center', fontweight='bold')

            # 如果节点在当前路径中，添加路径标记
            if node in path:
                # 在节点周围添加一个橙色圆圈表示路径
                path_circle = plt.Circle((x, y), self.node_radius + 5, color='orange', fill=False, linewidth=2)
                self.ax.add_patch(path_circle)

        # 绘制当前路径（如果有）
        if len(path) > 1:
            for i in range(len(path) - 1):
                node1, node2 = path[i], path[i + 1]
                x1, y1 = self.nodes[node1]
                x2, y2 = self.nodes[node2]

                # 绘制路径边（橙色，更粗）
                path_line = plt.Line2D([x1, x2], [y1, y2], color='orange', linewidth=4, alpha=0.7)
                self.ax.add_line(path_line)

        # 添加标题
        self.ax.set_title(f"Depth-First Search - Graph with {self.node_count} nodes", fontsize=16)

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
            if event.xdata is None or event.ydata is None:
                continue

            distance = math.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
            if distance <= self.node_radius:
                self.start_node = node
                self.start_node_var.set(str(node))
                self.status_var.set(f"Start node set to {node}. Click 'Start DFS' to begin.")
                self.draw_graph()
                break

    def start_dfs(self):
        if self.is_running or self.start_node is None:
            return

        self.is_running = True
        self.paused = False
        self.stop_flag = False
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.status_var.set("Running DFS...")

        # 初始化DFS状态
        self.visited = set()
        self.stack = [self.start_node]
        self.visited_order = []
        self.current_path = [self.start_node]

        # 在新线程中运行DFS算法
        self.dfs_thread = Thread(target=self.run_dfs)
        self.dfs_thread.daemon = True
        self.dfs_thread.start()

    def pause_dfs(self):
        if self.paused:
            self.paused = False
            self.pause_button.config(text="Pause")
            self.status_var.set("Running DFS...")
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

    def run_dfs(self):
        """执行DFS算法并更新可视化"""
        try:
            while self.stack and not self.stop_flag:
                # 处理暂停
                while self.paused and not self.stop_flag:
                    time.sleep(0.1)

                if self.stop_flag:
                    break

                # 从栈中取出当前节点
                current_node = self.stack[-1]

                # 如果当前节点尚未访问，标记为已访问
                if current_node not in self.visited:
                    self.visited.add(current_node)
                    self.visited_order.append(current_node)

                    # 更新可视化 - 显示当前节点
                    stack_set = set(self.stack)
                    self.root.after(0, self.draw_graph, current_node, self.visited, stack_set, self.current_path)
                    self.root.after(0, self.status_var.set, f"Visiting node {current_node}")
                    time.sleep(1.0 / self.speed)

                # 处理暂停
                while self.paused and not self.stop_flag:
                    time.sleep(0.1)

                if self.stop_flag:
                    break

                # 查找未访问的邻居
                unvisited_neighbors = []
                for neighbor in self.graph[current_node]:
                    if neighbor not in self.visited:
                        unvisited_neighbors.append(neighbor)

                if unvisited_neighbors:
                    # 选择第一个未访问的邻居
                    next_node = unvisited_neighbors[0]

                    # 将邻居加入栈和路径
                    if next_node not in self.stack:
                        self.stack.append(next_node)

                    # 更新当前路径
                    if next_node not in self.current_path:
                        self.current_path.append(next_node)

                    # 更新可视化 - 显示栈中的节点和当前路径
                    stack_set = set(self.stack)
                    self.root.after(0, self.draw_graph, current_node, self.visited, stack_set, self.current_path)
                    self.root.after(0, self.status_var.set,
                                    f"Moving to neighbor {next_node}. Stack: {self.stack}")
                    time.sleep(1.0 / self.speed)
                else:
                    # 没有未访问的邻居，回溯
                    popped_node = self.stack.pop()

                    # 更新当前路径
                    if popped_node in self.current_path and len(self.current_path) > 1:
                        self.current_path.pop()

                    # 更新可视化 - 显示回溯
                    stack_set = set(self.stack)
                    next_current = self.stack[-1] if self.stack else None
                    self.root.after(0, self.draw_graph, next_current, self.visited, stack_set, self.current_path)
                    self.root.after(0, self.status_var.set,
                                    f"Backtracking from {popped_node}. Stack: {self.stack}")
                    time.sleep(1.0 / self.speed)

            if not self.stop_flag:
                self.root.after(0, self.dfs_completed)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset)

    def dfs_completed(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.status_var.set(f"DFS completed! Visited order: {self.visited_order}")
        self.draw_graph(visited=self.visited)


def main():
    root = tk.Tk()
    app = DFSVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()