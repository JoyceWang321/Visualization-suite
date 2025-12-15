import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import time
from threading import Thread


class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparison Sorting Visualization")
        self.root.geometry("1000x700")

        # 算法列表
        self.algorithms = {
            "Bubble Sort": self.bubble_sort,
            "Selection Sort": self.selection_sort,
            "Insertion Sort": self.insertion_sort
        }

        # 默认值
        self.original_data = []  # 保存原始数据用于重置
        self.data = []  # 当前正在排序的数据
        self.data_size = 30
        self.speed = 0.1
        self.is_sorting = False
        self.current_algorithm = "Bubble Sort"
        self.paused = False
        self.stop_flag = False

        # 创建UI
        self.setup_ui()

        # 初始化数据
        self.generate_data()

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
        title_label = ttk.Label(main_frame, text="Comparison Sorting Algorithms",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 算法控制部分
        algo_control_frame = ttk.LabelFrame(main_frame, text="Algorithm Controls", padding="10")
        algo_control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 算法选择
        ttk.Label(algo_control_frame, text="Select Algorithm:").grid(row=0, column=0, sticky=tk.W)
        self.algo_var = tk.StringVar(value=self.current_algorithm)
        algo_combo = ttk.Combobox(algo_control_frame, textvariable=self.algo_var,
                                  values=list(self.algorithms.keys()), state="readonly")
        algo_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        # 数据大小控制
        ttk.Label(algo_control_frame, text="Data Size:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.size_var = tk.IntVar(value=self.data_size)
        size_scale = ttk.Scale(algo_control_frame, from_=10, to=100, variable=self.size_var,
                               orient=tk.HORIZONTAL, command=self.on_size_change)
        size_scale.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 10))
        self.size_label = ttk.Label(algo_control_frame, text=str(self.data_size))
        self.size_label.grid(row=0, column=4, padx=(0, 10))

        # 生成数据按钮
        ttk.Button(algo_control_frame, text="Generate New Data",
                   command=self.generate_data).grid(row=0, column=5, padx=(10, 0))

        # 画布区域
        self.figure = plt.Figure(figsize=(10, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, main_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 通用动画控制
        control_frame = ttk.LabelFrame(main_frame, text="Animation Controls", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # 速度控制
        ttk.Label(control_frame, text="Speed:").grid(row=0, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=self.speed)
        speed_scale = ttk.Scale(control_frame, from_=0.01, to=1.0, variable=self.speed_var,
                                orient=tk.HORIZONTAL, command=self.on_speed_change)
        speed_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        self.speed_label = ttk.Label(control_frame, text=f"{self.speed:.2f}s")
        self.speed_label.grid(row=0, column=2, padx=(0, 20))

        # 控制按钮
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_sorting)
        self.start_button.grid(row=0, column=3, padx=(10, 5))

        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_sorting, state="disabled")
        self.pause_button.grid(row=0, column=4, padx=5)

        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=5, padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=6, padx=(20, 0))

        # 使用说明
        instructions = """
Instructions for Use:

Select Sorting Algorithm: Choose the algorithm to visualize from the dropdown menu.

Adjust Data Size: Use the slider to modify the number of elements to be sorted.

Adjust Speed: Control the speed of the sorting animation.

Start Sorting: Click the 'Start' button to begin the visualization process.

Pause/Resume: You can pause and resume the sorting process.

Reset: Stop the current sorting and generate new random data.

Note: During sorting, elements highlighted in red indicate those being compared or swapped.
        """
        instructions_label = ttk.Label(main_frame, text=instructions, justify=tk.LEFT)
        instructions_label.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)

        # 配置列权重
        algo_control_frame.columnconfigure(1, weight=1)
        algo_control_frame.columnconfigure(3, weight=1)
        control_frame.columnconfigure(1, weight=1)

    def generate_data(self):
        self.original_data = [random.randint(1, 100) for _ in range(self.data_size)]
        self.data = self.original_data.copy()  # 使用副本进行排序
        self.update_plot()

    def update_plot(self, highlights=None):
        self.ax.clear()

        if highlights is None:
            colors = ['blue'] * len(self.data)
        else:
            colors = ['blue'] * len(self.data)
            for i in highlights:
                if 0 <= i < len(colors):  # 确保索引有效
                    colors[i] = 'red'

        x = list(range(len(self.data)))
        self.ax.bar(x, self.data, color=colors)
        self.ax.set_title(f"{self.current_algorithm} - Data Size: {len(self.data)}")
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")

        # 设置y轴范围固定，避免图表缩放
        self.ax.set_ylim(0, max(self.data) * 1.1)

        self.canvas.draw()

    def on_algorithm_change(self, event):
        self.current_algorithm = self.algo_var.get()
        self.reset()

    def on_size_change(self, value):
        self.data_size = int(float(value))
        self.size_label.config(text=str(self.data_size))
        self.generate_data()

    def on_speed_change(self, value):
        self.speed = float(value)
        self.speed_label.config(text=f"{self.speed:.2f}s")

    def start_sorting(self):
        if self.is_sorting:
            return

        self.is_sorting = True
        self.paused = False
        self.stop_flag = False
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.status_var.set("Sorting...")

        # 在新线程中运行排序算法
        self.sort_thread = Thread(target=self.run_sorting_algorithm)
        self.sort_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        self.sort_thread.start()

    def pause_sorting(self):
        if self.paused:
            self.paused = False
            self.pause_button.config(text="Pause")
            self.status_var.set("Sorting...")
        else:
            self.paused = True
            self.pause_button.config(text="Resume")
            self.status_var.set("Paused")

    def reset(self):
        self.stop_flag = True
        self.is_sorting = False
        self.paused = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause")
        self.status_var.set("Ready")
        # 恢复原始数据
        self.data = self.original_data.copy()
        self.update_plot()

    def run_sorting_algorithm(self):
        algorithm_func = self.algorithms[self.current_algorithm]

        try:
            # 调用排序算法，传入数据的副本
            for step in algorithm_func(self.data.copy()):
                if self.stop_flag:
                    break

                while self.paused and not self.stop_flag:
                    time.sleep(0.1)

                if self.stop_flag:
                    break

                # 更新可视化
                self.root.after(0, self.update_plot, step)
                time.sleep(self.speed)

            if not self.stop_flag:
                self.root.after(0, self.sorting_completed)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset)

    def sorting_completed(self):
        self.is_sorting = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.status_var.set("Sorting Completed!")
        # 最终更新一次可视化，确保显示排序完成后的状态
        self.update_plot()

    # 修复后的排序算法实现
    def bubble_sort(self, data):
        """冒泡排序算法"""
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                # 高亮显示当前比较的两个元素
                yield [j, j + 1]

                if data[j] > data[j + 1]:
                    # 交换元素
                    data[j], data[j + 1] = data[j + 1], data[j]
                    # 更新主数据，以便可视化反映变化
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]
                    # 再次高亮显示交换后的元素
                    yield [j, j + 1]

    def selection_sort(self, data):
        """选择排序算法"""
        n = len(data)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                # 高亮显示当前比较的元素
                yield [i, j, min_idx]

                if data[j] < data[min_idx]:
                    min_idx = j
                    # 高亮显示新的最小值
                    yield [i, j, min_idx]

            # 交换找到的最小元素
            if min_idx != i:
                data[i], data[min_idx] = data[min_idx], data[i]
                self.data[i], self.data[min_idx] = self.data[min_idx], self.data[i]
                yield [i, min_idx]

    def insertion_sort(self, data):
        """插入排序算法"""
        for i in range(1, len(data)):
            key = data[i]
            j = i - 1

            # 高亮显示当前处理的元素
            yield [i, j + 1]

            while j >= 0 and key < data[j]:
                data[j + 1] = data[j]
                self.data[j + 1] = self.data[j]
                j -= 1
                # 高亮显示移动过程
                yield [i, j + 1]

            data[j + 1] = key
            self.data[j + 1] = key
            yield [i, j + 1]


def main():
    root = tk.Tk()
    app = SortingVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()