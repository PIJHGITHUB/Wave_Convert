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

class SyncConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("光电计算器 (自动联动版)")
        self.geometry("720x450")
        self.resizable(False, False)
        
        # 状态变量
        self.current_source = None       # 当前正在计算的触发源
        self.last_delta_source = 'dl'    # 记住最后一次操作的 Delta 栏位，默认以波长(dl)为基准
        
        self._setup_styles()
        self._build_ui()
        
        # 初始化默认值
        self.l_var.set("532")
        self.l_unit.set("nm")
        
        self.dl_var.set("1") # 默认 1nm 线宽
        self.dl_unit.set("nm")
        
        # 触发初始计算
        self._trigger_calc('l', self._calc_abs)

    def _setup_styles(self):
        style = ttk.Style(self)
        if 'vista' in style.theme_names(): style.theme_use('vista')
        
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('TEntry', font=('Consolas', 10))
        style.configure('Header.TLabelframe.Label', font=('微软雅黑', 10, 'bold'), foreground='#333')

    def _build_ui(self):
        main = ttk.Frame(self, padding="15")
        main.pack(fill='both', expand=True)

        # === 左侧面板 ===
        left_panel = ttk.Frame(main)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # 1. 绝对值 (Absolute)
        abs_frame = ttk.LabelFrame(left_panel, text="1. 中心波长/频率 (绝对值)", style='Header.TLabelframe', padding=10)
        abs_frame.pack(fill='x', pady=(0, 15))
        
        self.f_var, self.f_unit = self._create_row(abs_frame, 0, "频率 (Freq):", 'THz', 'frequency', 'f', self._calc_abs)
        self.l_var, self.l_unit = self._create_row(abs_frame, 1, "波长 (Wave):", 'nm', 'wavelength', 'l', self._calc_abs)
        self.k_var, self.k_unit = self._create_row(abs_frame, 2, "波数 (k):", '1/cm', 'wavenumber', 'k', self._calc_abs)

        # 2. 变化量 (Delta)
        delta_frame = ttk.LabelFrame(left_panel, text="2. 线宽/带宽 (Delta Δ)", style='Header.TLabelframe', padding=10)
        delta_frame.pack(fill='x')
        
        self.df_var, self.df_unit = self._create_row(delta_frame, 0, "Δ 频率:", 'GHz', 'frequency', 'df', self._calc_delta)
        self.dl_var, self.dl_unit = self._create_row(delta_frame, 1, "Δ 波长:", 'nm', 'wavelength', 'dl', self._calc_delta)
        self.dk_var, self.dk_unit = self._create_row(delta_frame, 2, "Δ 波数:", '1/cm', 'wavenumber', 'dk', self._calc_delta)

        # === 右侧面板 ===
        right_panel = ttk.Frame(main)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))

        pow_frame = ttk.LabelFrame(right_panel, text="3. 功率转换", style='Header.TLabelframe', padding=10)
        pow_frame.pack(fill='x', anchor='n')

        self.p_dbm = self._create_power_row(pow_frame, 0, "dBm:", 'dbm')
        self.p_mw  = self._create_power_row(pow_frame, 1, "mW:", 'mw')
        self.p_w   = self._create_power_row(pow_frame, 2, "W:", 'w')

        # 说明文字
        info_text = (
            "逻辑说明:\n"
            "• 修改 [中心波长] 会同步更新 [Δ Delta]。\n"
            "  (因为转换系数依赖于中心波长)\n\n"
            "• 操作方式：输入数值 -> 按 Enter。"
        )
        ttk.Label(right_panel, text=info_text, foreground="gray", justify="left").pack(side='bottom', anchor='sw', pady=10)

    def _create_row(self, parent, row, label, unit_def, unit_type, tag, callback):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=15, justify='right')
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        u_var = tk.StringVar(value=unit_def)
        cb = ttk.Combobox(parent, textvariable=u_var, values=list(UNIT_FACTORS[unit_type].keys()), 
                          width=6, state='readonly')
        cb.grid(row=row, column=2, sticky='w', padx=5, pady=5)

        # Bindings
        # FocusIn: 记住如果是 Delta 栏位被选中，它就是下一次联动的基准
        if tag in ['df', 'dl', 'dk']:
            entry.bind('<FocusIn>', lambda e: self._set_delta_source(tag))
            cb.bind('<FocusIn>', lambda e: self._set_delta_source(tag))

        entry.bind('<Return>', lambda e: self._trigger_calc(tag, callback))
        cb.bind('<<ComboboxSelected>>', lambda e: self._trigger_calc(tag, callback))
        
        return var, u_var

    def _create_power_row(self, parent, row, label, tag):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=8)
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=15, justify='right')
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=8)
        entry.bind('<Return>', lambda e: self._trigger_calc(tag, self._calc_power))
        return var

    def _set_delta_source(self, tag):
        self.last_delta_source = tag

    def _trigger_calc(self, source_tag, func):
        self.current_source = source_tag
        # 如果用户手动修改了 Delta 栏位，更新 last_delta_source
        if source_tag in ['df', 'dl', 'dk']:
            self.last_delta_source = source_tag
        func()

    # --- 核心计算逻辑 ---

    def _get_si(self, var, unit_var, unit_type):
        try:
            val = float(var.get())
            factor = UNIT_FACTORS[unit_type][unit_var.get()]
            return val * factor
        except ValueError:
            return None

    def _set_val(self, var, unit_var, unit_type, si_val):
        if si_val is None:
            var.set("")
            return
        factor = UNIT_FACTORS[unit_type][unit_var.get()]
        # 智能格式化：根据数值大小决定显示精度
        var.set(f"{si_val / factor:.10g}")

    def _calc_abs(self):
        """计算绝对值，并触发 Delta 更新"""
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

        # === 关键点：绝对值更新后，必须刷新 Delta ===
        # 我们假装用户刚刚按下了"最后操作过的那个Delta输入框"的回车
        # 这样可以保持那个数值不变，重新计算其他的 Delta
        if l_si: # 只有在波长有效时才联动
            self.current_source = self.last_delta_source 
            self._calc_delta()

    def _calc_delta(self):
        """计算 Delta，依赖当前的绝对波长"""
        # 获取当前的中心波长 (绝对值)
        base_l = self._get_si(self.l_var, self.l_unit, 'wavelength')
        
        # 如果中心波长为空，无法进行物理转换
        if not base_l: 
            return

        src = self.current_source
        
        # 读取各个 Delta 的值
        df_si = self._get_si(self.df_var, self.df_unit, 'frequency')
        dl_si = self._get_si(self.dl_var, self.dl_unit, 'wavelength')
        dk_si = self._get_si(self.dk_var, self.dk_unit, 'wavenumber')

        try:
            # 物理公式: |df| = (c / lambda^2) * |dl|
            #          |dk| = |dl| / lambda^2
            if src == 'df' and df_si is not None:
                dl_si = (base_l**2 / C) * df_si
                dk_si = df_si / C
            elif src == 'dl' and dl_si is not None:
                df_si = (C / base_l**2) * dl_si
                dk_si = dl_si / (base_l**2)
            elif src == 'dk' and dk_si is not None:
                df_si = dk_si * C
                dl_si = dk_si * (base_l**2)
        except ZeroDivisionError:
            return

        if src != 'df': self._set_val(self.df_var, self.df_unit, 'frequency', df_si)
        if src != 'dl': self._set_val(self.dl_var, self.dl_unit, 'wavelength', dl_si)
        if src != 'dk': self._set_val(self.dk_var, self.dk_unit, 'wavenumber', dk_si)

    def _calc_power(self):
        """功率计算 (独立模块)"""
        src = self.current_source
        mw = None
        try:
            if src == 'dbm':
                val = float(self.p_dbm.get())
                mw = 10 ** (val / 10.0)
            elif src == 'mw':
                mw = float(self.p_mw.get())
            elif src == 'w':
                val = float(self.p_w.get())
                mw = val * 1000.0
        except ValueError:
            return

        if mw is None: return

        if src != 'dbm':
            val_dbm = 10 * math.log10(mw) if mw > 0 else -100.0
            self.p_dbm.set(f"{val_dbm:.4f}")
        if src != 'mw':
            self.p_mw.set(f"{mw:.6g}")
        if src != 'w':
            self.p_w.set(f"{mw/1000.0:.6g}")

if __name__ == '__main__':
    app = SyncConverterApp()
    app.mainloop()