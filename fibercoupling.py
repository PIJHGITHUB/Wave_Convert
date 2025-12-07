import tkinter as tk
from tkinter import ttk
import math

class FiberCouplerCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("耦合头焦距计算器")
        
        # 设置窗口大小和位置
        self.root.geometry("800x600+200+200")  # 宽800，高600，位置(200,200)
        self.root.minsize(700, 500)  # 最小尺寸
        
        # 配置主窗口的权重，使其可以自适应
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置主框架的列权重
        main_frame.columnconfigure(0, weight=1)
        
        # 创建输入框架
        input_frame = ttk.LabelFrame(main_frame, text="输入参数", padding="15")
        input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # 配置输入框架的列权重
        input_frame.columnconfigure(1, weight=1)
        
        # 波长输入 - 增大字体和输入框
        ttk.Label(input_frame, text="波长 (nm):", font=('微软雅黑', 12)).grid(row=0, column=0, sticky="w", pady=10)
        self.wavelength_entry = ttk.Entry(input_frame, width=15, font=('Consolas', 12))
        self.wavelength_entry.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        ttk.Label(input_frame, text="nm", font=('微软雅黑', 12)).grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        # 光斑直径输入
        ttk.Label(input_frame, text="入射光斑直径 (mm):", font=('微软雅黑', 12)).grid(row=1, column=0, sticky="w", pady=10)
        self.spot_entry = ttk.Entry(input_frame, width=15, font=('Consolas', 12))
        self.spot_entry.grid(row=1, column=1, padx=15, pady=10, sticky="ew")
        ttk.Label(input_frame, text="mm", font=('微软雅黑', 12)).grid(row=1, column=2, sticky="w", padx=(0, 10))
        
        # MFD输入
        ttk.Label(input_frame, text="模场直径MFD (μm):", font=('微软雅黑', 12)).grid(row=2, column=0, sticky="w", pady=10)
        self.mfd_entry = ttk.Entry(input_frame, width=15, font=('Consolas', 12))
        self.mfd_entry.grid(row=2, column=1, padx=15, pady=10, sticky="ew")
        ttk.Label(input_frame, text="μm", font=('微软雅黑', 12)).grid(row=2, column=2, sticky="w", padx=(0, 10))
        
        # 计算按钮 - 增大按钮
        calc_btn = ttk.Button(main_frame, text="计算焦距", command=self.calculate, style='Big.TButton')
        calc_btn.grid(row=1, column=0, pady=20)
        
        # 创建按钮样式
        style = ttk.Style()
        style.configure('Big.TButton', font=('微软雅黑', 14, 'bold'), padding=10)
        
        # 结果显示框架
        result_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="15")
        result_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        # 结果显示标签
        self.result_var = tk.StringVar()
        result_label = ttk.Label(result_frame, textvariable=self.result_var, 
                                font=('Arial', 16, 'bold'), foreground="blue")
        result_label.pack(pady=20)
        
        # 添加说明文字
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        info_text = (
            "使用说明：\n"
            "• 输入波长（纳米）、光斑直径（毫米）、模场直径（微米）\n"
            "• 点击计算焦距按钮获取最佳耦合焦距\n"
            "• 计算公式：f = (π × D × MFD) / (4 × λ)"
        )
        ttk.Label(info_frame, text=info_text, font=('微软雅黑', 10), 
                 foreground="gray", justify="left").pack(pady=10)

    def calculate(self):
        try:
            # 获取输入值并转换单位到米
            λ = float(self.wavelength_entry.get()) * 1e-9   # nm → m
            D = float(self.spot_entry.get()) * 1e-3         # mm → m
            MFD = float(self.mfd_entry.get()) * 1e-6        # μm → m

            # 执行计算
            f = (math.pi * D * MFD) / (4 * λ)
            
            # 转换结果为毫米并显示
            self.result_var.set(f"所需焦距: {f*1e3:.3f} mm")
        except ValueError:
            self.result_var.set("错误: 请输入有效的数字")
        except ZeroDivisionError:
            self.result_var.set("错误: 波长不能为零")

if __name__ == "__main__":
    root = tk.Tk()
    app = FiberCouplerCalculator(root)
    root.mainloop()