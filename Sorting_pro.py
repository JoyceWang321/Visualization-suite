import tkinter as tk
from tkinter import ttk
import random
import copy

# --- 颜色配置 (模仿 Galles 网站风格) ---
COLOR_BG = "#F5F5F5"  # 背景: 浅灰/米色
COLOR_BAR_DEFAULT = "#87CEEB"  # 数据柱: 天蓝色
COLOR_BAR_COMPARE = "#DC143C"  # 比较中: 深红色
COLOR_BAR_SWAP = "#FFFF00"  # 交换/选中: 亮黄色
COLOR_BAR_SORTED = "#32CD32"  # 已归位: 柠檬绿
COLOR_TEXT = "#000000"  # 文字: 黑色


class Visualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Algorithm Visualization (Galles Style)")
        self.root.geometry("1000x650")
        self.root.config(bg=COLOR_BG)

        # 核心数据
        self.array_size = 30
        self.data = []

        # 动画帧系统
        # frames 存储每一步的快照: {'data': [...], 'colors': [...]}
        self.frames = []
        self.current_frame_index = 0
        self.is_playing = False
        self.animation_speed = 50  # 毫秒

        # 算法映射
        self.algorithms = {
            "Bubble Sort (冒泡排序)": self.generate_bubble_sort_frames,
            "Selection Sort (选择排序)": self.generate_selection_sort_frames,
            "Insertion Sort (插入排序)": self.generate_insertion_sort_frames,
            "Quick Sort (快速排序)": self.generate_quick_sort_frames,
            "Merge Sort (归并排序)": self.generate_merge_sort_frames
        }

        self._setup_ui()
        self.generate_new_data()

    def _setup_ui(self):
        """构建模仿网页版的布局"""

        # 1. 顶部：算法选择与设置
        top_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Algorithm:", bg=COLOR_BG, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        self.algo_combobox = ttk.Combobox(top_frame, values=list(self.algorithms.keys()), state="readonly", width=25)
        self.algo_combobox.current(0)
        self.algo_combobox.pack(side=tk.LEFT, padx=5)
        self.algo_combobox.bind("<<ComboboxSelected>>", self.on_algo_change)

        tk.Label(top_frame, text="Size:", bg=COLOR_BG, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        self.size_scale = tk.Scale(top_frame, from_=10, to=60, orient=tk.HORIZONTAL, bg=COLOR_BG,
                                   command=self.on_size_change, showvalue=0, length=100)
        self.size_scale.set(30)
        self.size_scale.pack(side=tk.LEFT)
        self.size_label = tk.Label(top_frame, text="30", bg=COLOR_BG, font=("Arial", 12), width=3)
        self.size_label.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Generate New Data", command=self.generate_new_data, bg="#E0E0E0").pack(side=tk.LEFT,
                                                                                                          padx=20)

        # 2. 中部：画布 (Canvas)
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 3. 底部：播放控制栏 (模仿 Galles 的 Animation Controls)
        control_frame = tk.Frame(self.root, bg=COLOR_BG, pady=15, padx=10, relief=tk.RAISED, borderwidth=1)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 居中放置控制按钮
        btn_container = tk.Frame(control_frame, bg=COLOR_BG)
        btn_container.pack(anchor=tk.CENTER)

        # 定义按钮样式 (使用 Unicode 符号)
        btn_width = 4
        self.btn_skip_back = tk.Button(btn_container, text="|<", width=btn_width, command=self.step_start)
        self.btn_step_back = tk.Button(btn_container, text="<", width=btn_width, command=self.step_back)
        self.btn_play = tk.Button(btn_container, text="Play", width=6, command=self.toggle_play, bg="#90EE90")
        self.btn_step_fwd = tk.Button(btn_container, text=">", width=btn_width, command=self.step_forward)
        self.btn_skip_fwd = tk.Button(btn_container, text=">|", width=btn_width, command=self.step_end)

        self.btn_skip_back.pack(side=tk.LEFT, padx=2)
        self.btn_step_back.pack(side=tk.LEFT, padx=2)
        self.btn_play.pack(side=tk.LEFT, padx=10)
        self.btn_step_fwd.pack(side=tk.LEFT, padx=2)
        self.btn_skip_fwd.pack(side=tk.LEFT, padx=2)

        # 速度控制
        tk.Label(btn_container, text="Speed:", bg=COLOR_BG).pack(side=tk.LEFT, padx=(20, 5))
        self.speed_scale = tk.Scale(btn_container, from_=200, to=1, orient=tk.HORIZONTAL, bg=COLOR_BG, showvalue=0,
                                    length=150)
        self.speed_scale.set(50)
        self.speed_scale.pack(side=tk.LEFT)
        self.speed_scale.bind("<Motion>", self.update_speed)  # 实时更新速度
        self.speed_label = tk.Label(btn_container, text="50", bg=COLOR_BG, font=("Arial", 10), width=4)
        self.speed_label.pack(side=tk.LEFT, padx=5)

        # 进度条/信息
        self.status_label = tk.Label(control_frame, text="Ready", bg=COLOR_BG, font=("Consolas", 10), fg="gray")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    # --- 核心逻辑: 数据生成与预计算 ---

    def generate_new_data(self):
        """生成随机数据，并立即预计算当前算法的所有帧"""
        self.is_playing = False
        self.btn_play.config(text="Play", bg="#90EE90")

        self.array_size = int(self.size_scale.get())
        self.data = [random.randint(5, 100) for _ in range(self.array_size)]

        # 根据当前选择的算法，生成所有动画帧
        self.precompute_frames()

        # 重置到第一帧
        self.current_frame_index = 0
        self.draw_current_frame()

    def on_algo_change(self, event):
        self.generate_new_data()

    def on_size_change(self, val):
        self.size_label.config(text=str(int(val)))
        self.generate_new_data()

    def update_speed(self, event):
        speed_val = int(self.speed_scale.get())
        self.animation_speed = speed_val
        self.speed_label.config(text=str(speed_val))

    def precompute_frames(self):
        """
        这是实现“后退”和流畅播放的关键。
        我们在后台对数据副本运行算法，记录每一步的状态。
        """
        algo_name = self.algo_combobox.get()
        generator_func = self.algorithms[algo_name]

        # 初始帧
        start_data = list(self.data)
        start_colors = [COLOR_BAR_DEFAULT] * len(self.data)

        self.frames = []
        # 添加第一帧
        self.add_frame(start_data, start_colors)

        # 运行算法生成器，收集所有帧
        # 注意：传入的是数据的副本，以免影响原始数据
        data_copy = list(self.data)
        generator_func(data_copy)

        # 添加最后一帧（全绿）
        self.add_frame(data_copy, [COLOR_BAR_SORTED] * len(data_copy))

        self.status_label.config(text=f"Total Steps: {len(self.frames)}")

    def add_frame(self, data, colors):
        """记录一个快照"""
        self.frames.append({
            'data': list(data),  # 必须深拷贝
            'colors': list(colors)  # 必须深拷贝
        })

    # --- 绘图逻辑 ---

    def draw_current_frame(self):
        if not self.frames: return

        frame = self.frames[self.current_frame_index]
        data = frame['data']
        colors = frame['colors']

        self.canvas.delete("all")
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()

        # 避免除以0错误
        if c_width < 10: c_width = 800
        if c_height < 10: c_height = 400

        bar_width = c_width / (len(data) + 2)
        spacing = 2
        max_val = 100  # 数据最大值约为100

        for i, val in enumerate(data):
            x0 = (i + 1) * bar_width
            y0 = c_height - (val / max_val * (c_height - 50))
            x1 = x0 + bar_width - spacing
            y1 = c_height - 10

            # 绘制柱子
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors[i], outline="black")

            # 在柱子顶部显示数值
            text_x = (x0 + x1) / 2
            text_y = y0 - 5  # 在柱子顶部上方5像素
            self.canvas.create_text(text_x, text_y, text=str(val), font=("Arial", 9), fill=COLOR_TEXT)

        # 更新状态文字
        self.status_label.config(text=f"Step: {self.current_frame_index + 1} / {len(self.frames)}")

    # --- 播放控制逻辑 ---

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="Play", bg="#90EE90")
        else:
            if self.current_frame_index >= len(self.frames) - 1:
                self.current_frame_index = 0  # 如果结束了，从头开始
            self.is_playing = True
            self.btn_play.config(text="Pause", bg="#FF6347")
            self.animate_loop()

    def animate_loop(self):
        if self.is_playing and self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.draw_current_frame()
            # 使用 after 实现递归调用，通过 speed_scale 控制速度
            self.root.after(self.animation_speed, self.animate_loop)
        elif self.current_frame_index >= len(self.frames) - 1:
            self.is_playing = False
            self.btn_play.config(text="Play", bg="#90EE90")

    def step_forward(self):
        self.is_playing = False
        self.btn_play.config(text="Play", bg="#90EE90")
        if self.current_frame_index < len(self.frames) - 1:
            self.current_frame_index += 1
            self.draw_current_frame()

    def step_back(self):
        self.is_playing = False
        self.btn_play.config(text="Play", bg="#90EE90")
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.draw_current_frame()

    def step_start(self):
        self.is_playing = False
        self.btn_play.config(text="Play", bg="#90EE90")
        self.current_frame_index = 0
        self.draw_current_frame()

    def step_end(self):
        self.is_playing = False
        self.btn_play.config(text="Play", bg="#90EE90")
        self.current_frame_index = len(self.frames) - 1
        self.draw_current_frame()

    # --- 算法实现 (生成器/Frame记录模式) ---

    # 辅助：设置所有颜色
    def get_colors(self, length, default=COLOR_BAR_DEFAULT):
        return [default] * length

    def generate_bubble_sort_frames(self, data):
        n = len(data)
        colors = self.get_colors(n)

        for i in range(n):
            for j in range(0, n - i - 1):
                # 比较: 变红
                colors[j] = COLOR_BAR_COMPARE
                colors[j + 1] = COLOR_BAR_COMPARE
                self.add_frame(data, colors)

                if data[j] > data[j + 1]:
                    # 交换
                    data[j], data[j + 1] = data[j + 1], data[j]
                    colors[j] = COLOR_BAR_SWAP
                    colors[j + 1] = COLOR_BAR_SWAP
                    self.add_frame(data, colors)

                # 恢复
                colors[j] = COLOR_BAR_DEFAULT
                colors[j + 1] = COLOR_BAR_DEFAULT

            # 这一轮结束，i位置（从后往前）已排序
            colors[n - i - 1] = COLOR_BAR_SORTED
            self.add_frame(data, colors)

    def generate_selection_sort_frames(self, data):
        n = len(data)
        colors = self.get_colors(n)

        for i in range(n):
            min_idx = i
            colors[i] = COLOR_BAR_SWAP  # 当前基准位置
            self.add_frame(data, colors)

            for j in range(i + 1, n):
                colors[j] = COLOR_BAR_COMPARE  # 正在查找
                self.add_frame(data, colors)

                if data[j] < data[min_idx]:
                    colors[min_idx] = COLOR_BAR_DEFAULT  # 旧的min恢复
                    min_idx = j
                    colors[min_idx] = COLOR_BAR_SWAP  # 新的min
                    self.add_frame(data, colors)
                else:
                    colors[j] = COLOR_BAR_DEFAULT

            data[i], data[min_idx] = data[min_idx], data[i]
            colors[min_idx] = COLOR_BAR_DEFAULT
            colors[i] = COLOR_BAR_SORTED
            self.add_frame(data, colors)

    def generate_insertion_sort_frames(self, data):
        n = len(data)
        colors = self.get_colors(n)

        # 0被认为是已排序
        colors[0] = COLOR_BAR_SORTED

        for i in range(1, n):
            key = data[i]
            j = i - 1

            # 抽出 key
            colors[i] = COLOR_BAR_SWAP
            self.add_frame(data, colors)

            while j >= 0 and key < data[j]:
                colors[j] = COLOR_BAR_COMPARE
                self.add_frame(data, colors)

                data[j + 1] = data[j]
                colors[j] = COLOR_BAR_SORTED  # 移位后属于"潜在已排序区"

                j -= 1

            data[j + 1] = key
            # 当前 i 之前都是有序的
            for k in range(i + 1):
                colors[k] = COLOR_BAR_SORTED
            self.add_frame(data, colors)

    def generate_quick_sort_frames(self, data):
        n = len(data)
        colors = self.get_colors(n)

        def partition(low, high):
            pivot = data[high]
            colors[high] = COLOR_BAR_SWAP  # Pivot
            i = low - 1

            for j in range(low, high):
                colors[j] = COLOR_BAR_COMPARE
                self.add_frame(data, colors)

                if data[j] < pivot:
                    i += 1
                    data[i], data[j] = data[j], data[i]
                    self.add_frame(data, colors)

                colors[j] = COLOR_BAR_DEFAULT

            data[i + 1], data[high] = data[high], data[i + 1]
            colors[high] = COLOR_BAR_DEFAULT
            self.add_frame(data, colors)
            return i + 1

        def quick_sort_recursive(low, high):
            if low < high:
                pi = partition(low, high)

                # 标记 pi 为已排序
                colors[pi] = COLOR_BAR_SORTED
                self.add_frame(data, colors)

                quick_sort_recursive(low, pi - 1)
                quick_sort_recursive(pi + 1, high)
            elif low == high:
                colors[low] = COLOR_BAR_SORTED
                self.add_frame(data, colors)

        quick_sort_recursive(0, n - 1)
        # 确保全部标绿
        for k in range(n): colors[k] = COLOR_BAR_SORTED
        self.add_frame(data, colors)

    def generate_merge_sort_frames(self, data):
        n = len(data)
        colors = self.get_colors(n)

        def merge(l, m, r):
            n1 = m - l + 1
            n2 = r - m
            L = data[l:m + 1]
            R = data[m + 1:r + 1]

            # 高亮当前归并区域
            for k in range(l, r + 1):
                colors[k] = COLOR_BAR_SWAP
            self.add_frame(data, colors)

            i = 0
            j = 0
            k = l

            while i < n1 and j < n2:
                # 比较
                if L[i] <= R[j]:
                    data[k] = L[i]
                    i += 1
                else:
                    data[k] = R[j]
                    j += 1

                # 标记正在放置的位置
                temp_color = colors[k]
                colors[k] = COLOR_BAR_COMPARE
                self.add_frame(data, colors)
                colors[k] = temp_color  # 恢复黄色

                k += 1

            while i < n1:
                data[k] = L[i]
                i += 1
                k += 1
                self.add_frame(data, colors)

            while j < n2:
                data[k] = R[j]
                j += 1
                k += 1
                self.add_frame(data, colors)

            # 归并完成的区域变回蓝色（或者绿色，如果是最后一步）
            for k in range(l, r + 1):
                colors[k] = COLOR_BAR_DEFAULT
            self.add_frame(data, colors)

        def merge_sort_recursive(l, r):
            if l < r:
                m = (l + r) // 2
                merge_sort_recursive(l, m)
                merge_sort_recursive(m + 1, r)
                merge(l, m, r)

        merge_sort_recursive(0, n - 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = Visualizer(root)
    root.mainloop()