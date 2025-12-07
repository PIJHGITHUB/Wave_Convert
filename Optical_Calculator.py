import tkinter as tk
from tkinter import ttk
import math

# --- 常量定义 ---
C = 299_792_458.0  # 光速 m/s

# 单位换算因子
UNIT_FACTORS = {
    'frequency': {'Hz': 1, 'MHz': 1e6, 'GHz': 1e9, 'THz': 1e12},
    'wavelength': {'m': 1, 'mm': 1e-3, 'µm': 1e-6, 'nm': 1e-9, 'pm': 1e-12},
    'wavenumber': {'1/m': 1, '1/cm': 1e2},
}

class IntegratedOpticalCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("光电计算器")
        
        # 设置窗口大小和位置
        self.root.geometry("800x600+100+100")
        self.root.minsize(750, 550)
        
        # 配置主窗口的权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 设置样式
        self._setup_styles()
        
        # 创建主框架
        self.create_main_interface()
        
        # 初始化波长计算器的状态变量
        self.current_source = None
        self.last_delta_source = 'dl'

    def _setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('TEntry', font=('Consolas', 10))
        style.configure('Header.TLabelframe.Label', font=('微软雅黑', 11, 'bold'), foreground='#333')
        style.configure('Big.TButton', font=('微软雅黑', 10, 'bold'), padding=6)
        style.configure('Result.TLabel', font=('Arial', 12, 'bold'), foreground="blue")
        style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'), foreground='#2E86AB')

    def create_main_interface(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置主框架
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔬 光电计算器", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # === 左侧：波长转换 ===
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        
        # 波长/频率转换
        self.create_wavelength_section(left_frame)
        
        # === 右侧：计算工具 ===
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        
        # 1. 功率转换
        self.create_power_section(right_frame)
        
        # 2. 光纤耦合计算
        self.create_fiber_coupling_section(right_frame)
        
        # 底部说明
        self.create_info_section(main_frame)

    def create_wavelength_section(self, parent):
        """创建波长转换部分"""
        # 波长转换框架
        wave_frame = ttk.LabelFrame(parent, text="📡 波长/频率转换", 
                                   style='Header.TLabelframe', padding=10)
        wave_frame.pack(fill='x', pady=(0, 15))
        
        # 配置列
        wave_frame.columnconfigure(1, weight=1)
        
        # 绝对值转换
        ttk.Label(wave_frame, text="绝对值:", font=('微软雅黑', 10, 'bold')).grid(
            row=0, column=0, columnspan=3, sticky='w', pady=(0, 5))
        
        # 频率
        self.f_var, self.f_unit = self._create_conversion_row(
            wave_frame, 1, "频率:", 'THz', 'frequency', 'f', self._calc_abs)
        
        # 波长
        self.l_var, self.l_unit = self._create_conversion_row(
            wave_frame, 2, "波长:", 'nm', 'wavelength', 'l', self._calc_abs)
        
        # 波数
        self.k_var, self.k_unit = self._create_conversion_row(
            wave_frame, 3, "波数:", '1/cm', 'wavenumber', 'k', self._calc_abs)
        
        # 分隔线
        sep = ttk.Separator(wave_frame, orient='horizontal')
        sep.grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Delta转换
        ttk.Label(wave_frame, text="线宽/变化 (Δ):", font=('微软雅黑', 10, 'bold')).grid(
            row=5, column=0, columnspan=3, sticky='w', pady=(0, 5))
        
        # Delta频率
        self.df_var, self.df_unit = self._create_conversion_row(
            wave_frame, 6, "Δ频率:", 'GHz', 'frequency', 'df', self._calc_delta)
        
        # Delta波长
        self.dl_var, self.dl_unit = self._create_conversion_row(
            wave_frame, 7, "Δ波长:", 'nm', 'wavelength', 'dl', self._calc_delta)
        
        # Delta波数
        self.dk_var, self.dk_unit = self._create_conversion_row(
            wave_frame, 8, "Δ波数:", '1/cm', 'wavenumber', 'dk', self._calc_delta)

    def create_power_section(self, parent):
        """创建功率转换部分"""
        power_frame = ttk.LabelFrame(parent, text="⚡ 功率转换", 
                                    style='Header.TLabelframe', padding=10)
        power_frame.pack(fill='x', pady=(0, 15))
        
        # 配置列
        power_frame.columnconfigure(1, weight=1)
        
        # dBm
        ttk.Label(power_frame, text="dBm:").grid(row=0, column=0, sticky='e', padx=3, pady=5)
        self.p_dbm = tk.StringVar()
        dbm_entry = ttk.Entry(power_frame, textvariable=self.p_dbm, width=10, justify='right')
        dbm_entry.grid(row=0, column=1, sticky='ew', padx=3, pady=5)
        dbm_entry.bind('<Return>', lambda e: self._calc_power())
        
        # mW
        ttk.Label(power_frame, text="mW:").grid(row=1, column=0, sticky='e', padx=3, pady=5)
        self.p_mw = tk.StringVar()
        mw_entry = ttk.Entry(power_frame, textvariable=self.p_mw, width=10, justify='right')
        mw_entry.grid(row=1, column=1, sticky='ew', padx=3, pady=5)
        mw_entry.bind('<Return>', lambda e: self._calc_power())
        
        # W
        ttk.Label(power_frame, text="W:").grid(row=2, column=0, sticky='e', padx=3, pady=5)
        self.p_w = tk.StringVar()
        w_entry = ttk.Entry(power_frame, textvariable=self.p_w, width=10, justify='right')
        w_entry.grid(row=2, column=1, sticky='ew', padx=3, pady=5)
        w_entry.bind('<Return>', lambda e: self._calc_power())

    def create_fiber_coupling_section(self, parent):
        """创建光纤耦合计算部分"""
        fiber_frame = ttk.LabelFrame(parent, text="🔧 光纤耦合计算器", 
                                    style='Header.TLabelframe', padding=10)
        fiber_frame.pack(fill='x', pady=(0, 15))
        
        # 配置列
        fiber_frame.columnconfigure(1, weight=1)
        
        # 波长输入
        ttk.Label(fiber_frame, text="波长 (nm):").grid(row=0, column=0, sticky='e', padx=3, pady=5)
        self.wavelength_entry = ttk.Entry(fiber_frame, width=10, justify='right')
        self.wavelength_entry.grid(row=0, column=1, sticky='ew', padx=3, pady=5)
        ttk.Label(fiber_frame, text="nm").grid(row=0, column=2, sticky='w', padx=(0, 5))
        
        # 光斑直径输入
        ttk.Label(fiber_frame, text="光斑直径 (mm):").grid(row=1, column=0, sticky='e', padx=3, pady=5)
        self.spot_entry = ttk.Entry(fiber_frame, width=10, justify='right')
        self.spot_entry.grid(row=1, column=1, sticky='ew', padx=3, pady=5)
        ttk.Label(fiber_frame, text="mm").grid(row=1, column=2, sticky='w', padx=(0, 5))
        
        # MFD输入
        ttk.Label(fiber_frame, text="MFD (μm):").grid(row=2, column=0, sticky='e', padx=3, pady=5)
        self.mfd_entry = ttk.Entry(fiber_frame, width=10, justify='right')
        self.mfd_entry.grid(row=2, column=1, sticky='ew', padx=3, pady=5)
        ttk.Label(fiber_frame, text="μm").grid(row=2, column=2, sticky='w', padx=(0, 5))
        
        # 计算按钮
        calc_btn = ttk.Button(fiber_frame, text="计算焦距", 
                             command=self.calculate_fiber_coupling, style='Big.TButton')
        calc_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 结果显示
        result_frame = ttk.Frame(fiber_frame)
        result_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(5, 3))
        
        self.fiber_result_var = tk.StringVar()
        result_label = ttk.Label(result_frame, textvariable=self.fiber_result_var, 
                                style='Result.TLabel')
        result_label.pack(pady=5)

    def create_info_section(self, parent):
        """创建说明信息部分"""
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        info_text = (
            "💡 使用说明:\n"
            "• 波长转换：输入任意一个值，按Enter键自动转换其他单位\n"
            "• 功率转换：在任意功率单位中输入数值，按Enter键转换其他单位\n"
            "• 光纤耦合：输入三个参数，点击计算焦距获取最佳耦合焦距\n"
            "• 物理公式：f = (π × D × MFD) / (4 × λ) | Δf = (c/λ²) × Δλ"
        )
        ttk.Label(info_frame, text=info_text, font=('微软雅黑', 9), 
                 foreground="#666", justify="left").pack(pady=8)

    def _create_conversion_row(self, parent, row, label, unit_def, unit_type, tag, callback):
        """创建转换输入行"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=6)
        
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=10, justify='right')
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=6)
        
        u_var = tk.StringVar(value=unit_def)
        cb = ttk.Combobox(parent, textvariable=u_var, 
                         values=list(UNIT_FACTORS[unit_type].keys()), 
                         width=6, state='readonly')
        cb.grid(row=row, column=2, sticky='w', padx=5, pady=6)
        
        # 绑定事件
        if tag in ['df', 'dl', 'dk']:
            entry.bind('<FocusIn>', lambda e: self._set_delta_source(tag))
            cb.bind('<FocusIn>', lambda e: self._set_delta_source(tag))
        
        entry.bind('<Return>', lambda e: self._trigger_calc(tag, callback))
        cb.bind('<<ComboboxSelected>>', lambda e: self._trigger_calc(tag, callback))
        
        return var, u_var

    def _set_delta_source(self, tag):
        """设置delta源"""
        self.last_delta_source = tag

    def _trigger_calc(self, source_tag, func):
        """触发计算"""
        self.current_source = source_tag
        if source_tag in ['df', 'dl', 'dk']:
            self.last_delta_source = source_tag
        func()

    def _get_si(self, var, unit_var, unit_type):
        """获取SI单位值"""
        try:
            val = float(var.get())
            factor = UNIT_FACTORS[unit_type][unit_var.get()]
            return val * factor
        except ValueError:
            return None

    def _set_val(self, var, unit_var, unit_type, si_val):
        """设置显示值"""
        if si_val is None:
            var.set("")
            return
        factor = UNIT_FACTORS[unit_type][unit_var.get()]
        var.set(f"{si_val / factor:.10g}")

    def _calc_abs(self):
        """计算绝对值"""
        src = self.current_source
        
        f_si = self._get_si(self.f_var, self.f_unit, 'frequency')
        l_si = self._get_si(self.l_var, self.l_unit, 'wavelength')
        k_si = self._get_si(self.k_var, self.k_unit, 'wavenumber')
        
        try:
            if src == 'f' and f_si:
                l_si = C / f_si
                k_si = 1.0 / l_si
            elif src == 'l' and l_si:
                f_si = C / l_si
                k_si = 1.0 / l_si
            elif src == 'k' and k_si:
                l_si = 1.0 / k_si
                f_si = C / l_si
        except ZeroDivisionError:
            return
        
        if src != 'f': self._set_val(self.f_var, self.f_unit, 'frequency', f_si)
        if src != 'l': self._set_val(self.l_var, self.l_unit, 'wavelength', l_si)
        if src != 'k': self._set_val(self.k_var, self.k_unit, 'wavenumber', k_si)
        
        # 更新Delta值
        if l_si:
            self.current_source = self.last_delta_source
            self._calc_delta()

    def _calc_delta(self):
        """计算Delta值"""
        base_l = self._get_si(self.l_var, self.l_unit, 'wavelength')
        if not base_l:
            return
        
        src = self.current_source
        df_si = self._get_si(self.df_var, self.df_unit, 'frequency')
        dl_si = self._get_si(self.dl_var, self.dl_unit, 'wavelength')
        dk_si = self._get_si(self.dk_var, self.dk_unit, 'wavenumber')
        
        try:
            if src == 'df' and df_si:
                dl_si = (df_si * base_l**2) / C
                dk_si = dl_si / base_l**2
            elif src == 'dl' and dl_si:
                df_si = (C * dl_si) / base_l**2
                dk_si = dl_si / base_l**2
            elif src == 'dk' and dk_si:
                dl_si = dk_si * base_l**2
                df_si = (C * dl_si) / base_l**2
        except ZeroDivisionError:
            return
        
        if src != 'df': self._set_val(self.df_var, self.df_unit, 'frequency', df_si)
        if src != 'dl': self._set_val(self.dl_var, self.dl_unit, 'wavelength', dl_si)
        if src != 'dk': self._set_val(self.dk_var, self.dk_unit, 'wavenumber', dk_si)

    def calculate_fiber_coupling(self):
        """计算光纤耦合焦距"""
        try:
            # 获取输入值并转换单位到米
            λ = float(self.wavelength_entry.get()) * 1e-9   # nm → m
            D = float(self.spot_entry.get()) * 1e-3         # mm → m
            MFD = float(self.mfd_entry.get()) * 1e-6        # μm → m
            
            # 执行计算
            f = (math.pi * D * MFD) / (4 * λ)
            
            # 转换结果为毫米并显示
            self.fiber_result_var.set(f"所需焦距: {f*1e3:.3f} mm")
        except ValueError:
            self.fiber_result_var.set("错误: 请输入有效的数字")
        except ZeroDivisionError:
            self.fiber_result_var.set("错误: 波长不能为零")

    def _calc_power(self):
        """功率转换计算"""
        try:
            # 获取当前活动的输入框
            if self.p_dbm.get():
                dbm = float(self.p_dbm.get())
                mw = 10**(dbm/10)
                w = mw / 1000
                self.p_mw.set(f"{mw:.6f}")
                self.p_w.set(f"{w:.9f}")
            elif self.p_mw.get():
                mw = float(self.p_mw.get())
                dbm = 10 * math.log10(mw)
                w = mw / 1000
                self.p_dbm.set(f"{dbm:.3f}")
                self.p_w.set(f"{w:.9f}")
            elif self.p_w.get():
                w = float(self.p_w.get())
                mw = w * 1000
                dbm = 10 * math.log10(mw)
                self.p_dbm.set(f"{dbm:.3f}")
                self.p_mw.set(f"{mw:.6f}")
        except ValueError:
            pass
        except ZeroDivisionError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedOpticalCalculator(root)
    root.mainloop()