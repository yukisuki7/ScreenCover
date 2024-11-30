import tkinter as tk
from tkinter import ttk

class SubtitleMask:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("字幕遮罩")
        
        # 设置窗口属性
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        
        # 获取屏幕尺寸
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # 创建遮罩框
        self.mask = tk.Frame(
            self.root, 
            bg='black',
            width=600,
            height=50
        )
        self.mask.pack(fill='both', expand=True)
        
        # 设置初始窗口大小和位置
        x = (self.screen_width - 600) // 2
        y = (self.screen_height - 50) // 2
        self.root.geometry(f"600x50+{x}+{y}")
        
        # 控制变量
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        self.start_w = 0
        self.start_h = 0
        
        # 最小尺寸
        self.min_width = 200
        self.min_height = 50
        
        # 创建透明的调整边框
        self.create_resize_borders()
        
        # 绑定事件
        self.mask.bind('<Button-1>', self.start_drag)
        self.mask.bind('<B1-Motion>', self.on_drag)
        self.mask.bind('<ButtonRelease-1>', self.stop_drag)
        
        # 创建控制面板
        self.create_control_window()
        
        # 绑定ESC键退出
        self.root.bind('<Escape>', lambda e: self.quit_app())

    def create_resize_borders(self):
        """创建透明的调整边框"""
        border_width = 4
        
        self.resize_frames = {
            'n':  tk.Frame(self.root, cursor='sb_v_double_arrow'),
            's':  tk.Frame(self.root, cursor='sb_v_double_arrow'),
            'e':  tk.Frame(self.root, cursor='sb_h_double_arrow'),
            'w':  tk.Frame(self.root, cursor='sb_h_double_arrow'),
            'nw': tk.Frame(self.root, cursor='size_nw_se'),
            'ne': tk.Frame(self.root, cursor='size_ne_sw'),
            'sw': tk.Frame(self.root, cursor='size_ne_sw'),
            'se': tk.Frame(self.root, cursor='size_nw_se')
        }
        
        for frame in self.resize_frames.values():
            frame.configure(
                bg='black',
                width=border_width,
                height=border_width
            )
            frame.bind('<Button-1>', self.start_resize)
            frame.bind('<B1-Motion>', self.on_resize)
            frame.bind('<ButtonRelease-1>', self.stop_resize)
        
        def update_borders(event=None):
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            b = border_width
            
            # 确保窗口尺寸不小于最小值
            if w < self.min_width or h < self.min_height:
                w = max(self.min_width, w)
                h = max(self.min_height, h)
                self.root.geometry(f"{w}x{h}")
            
            # 更新边框位置
            self.resize_frames['n'].place(x=b, y=0, width=w-2*b, height=b)
            self.resize_frames['s'].place(x=b, y=h-b, width=w-2*b, height=b)
            self.resize_frames['e'].place(x=w-b, y=b, width=b, height=h-2*b)
            self.resize_frames['w'].place(x=0, y=b, width=b, height=h-2*b)
            self.resize_frames['nw'].place(x=0, y=0, width=b, height=b)
            self.resize_frames['ne'].place(x=w-b, y=0, width=b, height=b)
            self.resize_frames['sw'].place(x=0, y=h-b, width=b, height=b)
            self.resize_frames['se'].place(x=w-b, y=h-b, width=b, height=b)
        
        self.root.bind('<Configure>', update_borders)
        update_borders()

    def start_resize(self, event):
        """开始调整大小"""
        self.resizing = True
        self.resize_edge = event.widget
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_w = self.root.winfo_width()
        self.start_h = self.root.winfo_height()
        # 记录初始窗口位置
        self.start_window_x = self.root.winfo_x()
        self.start_window_y = self.root.winfo_y()

    def on_resize(self, event):
        """调整大小"""
        if not self.resizing:
            return
            
        try:
            dx = event.x_root - self.start_x
            dy = event.y_root - self.start_y
            new_w = self.start_w
            new_h = self.start_h
            new_x = self.start_window_x
            new_y = self.start_window_y
            
            edge = [k for k, v in self.resize_frames.items() if v == self.resize_edge][0]
            
            # 调整宽度
            if 'e' in edge:  # 右边
                new_w = max(self.min_width, self.start_w + dx)
            if 'w' in edge:  # 左边
                width_change = min(dx, self.start_w - self.min_width)
                new_w = self.start_w - width_change
                new_x = self.start_window_x + width_change
            
            # 调整高度
            if 's' in edge:  # 下边
                new_h = max(self.min_height, self.start_h + dy)
            if 'n' in edge:  # 上边
                height_change = min(dy, self.start_h - self.min_height)
                new_h = self.start_h - height_change
                new_y = self.start_window_y + height_change
            
            # 确保窗口不会移出屏幕
            new_x = max(0, min(self.screen_width - new_w, new_x))
            new_y = max(0, min(self.screen_height - new_h, new_y))
            
            # 更新窗口大小和位置
            self.root.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")
            
        except Exception as e:
            print(f"调整大小时出错: {e}")

    def stop_resize(self, event):
        """停止调整大小"""
        self.resizing = False
        self.resize_edge = None

    def start_drag(self, event):
        """开始拖动"""
        if not self.resizing:
            self.dragging = True
            self.start_x = event.x_root - self.root.winfo_x()
            self.start_y = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        """拖动中"""
        if self.dragging:
            x = event.x_root - self.start_x
            y = event.y_root - self.start_y
            # 确保窗口不会移出屏幕
            x = max(0, min(self.screen_width - self.root.winfo_width(), x))
            y = max(0, min(self.screen_height - self.root.winfo_height(), y))
            self.root.geometry(f"+{int(x)}+{int(y)}")

    def stop_drag(self, event):
        """停止拖动"""
        self.dragging = False

    def create_control_window(self):
        """创建控制面板"""
        self.control_window = tk.Toplevel(self.root)
        self.control_window.title("透明度控制")
        self.control_window.geometry("200x50")
        self.control_window.attributes('-topmost', True)
        
        control_frame = ttk.Frame(self.control_window)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="透明度:").pack(side='left')
        alpha_scale = ttk.Scale(
            control_frame,
            from_=0.1,
            to=1.0,
            value=0.8,
            orient='horizontal',
            length=100,
            command=self.adjust_alpha
        )
        alpha_scale.pack(side='left', padx=5)

    def adjust_alpha(self, value):
        """调整透明度"""
        self.root.attributes('-alpha', float(value))

    def quit_app(self):
        """退出程序"""
        self.control_window.destroy()
        self.root.destroy()

    def run(self):
        """运行程序"""
        print("""
        使用说明：
        - 拖动中央区域移动位置
        - 拖动边缘调整大小
        - 使用滑块调整透明度
        - ESC键退出
        """)
        self.root.mainloop()

if __name__ == "__main__":
    app = SubtitleMask()
    app.run()
