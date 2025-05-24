"""
游戏图形界面系统
Game GUI System using tkinter
"""

import tkinter as tk
import json
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import threading
import time
import tkinter.font as tkfont
import random

from game_core import GameState, WeatherType, DistrictType
from order_system import OrderGenerator, DeliverySimulator, OrderPriority
from customer_interaction import CustomerInteractionSystem, DialogueMode
from economic_system import StockMarket, InvestmentPortfolio, LotterySystem, ExpenseManager
from skill_system import NightSchool, CareerTransition

class GameGUI:
    """游戏主界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("送外卖模拟器 - Food Delivery Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        self.root.option_add("*Font", default_font)

        style = ttk.Style()
        style.configure('.', font=('Arial', 14))
        style.configure('TButton', font=('Arial', 14))
        style.configure('TLabel', font=('Arial', 14))
        style.configure('TEntry', font=('Arial', 14))
        style.configure('TNotebook.Tab', font=('Arial', 14, 'bold'))
        style.configure('Treeview.Heading', font=('Arial', 14, 'bold'))
        style.configure('Treeview', font=('Arial', 13))
        
        # 游戏系统初始化
        self.game_state = GameState()
        self.order_generator = OrderGenerator()
        self.delivery_simulator = DeliverySimulator(self.game_state)
        self.customer_system = CustomerInteractionSystem(self.game_state)
        self.stock_market = StockMarket()
        self.portfolio = InvestmentPortfolio(self.game_state)
        self.lottery_system = LotterySystem()
        self.expense_manager = ExpenseManager(self.game_state)
        self.night_school = NightSchool()
        self.career_transition = CareerTransition()
        
        # 界面组件
        self.setup_main_interface()
        self.setup_menu_bar()
        
        # 游戏循环
        self.game_running = True
        self.start_game_loop()
    
    def setup_main_interface(self):
        """设置主界面"""
        # 创建主要框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 游戏状态
        self.left_panel = ttk.Frame(self.main_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # 右侧面板 - 主要游戏区域
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置左侧状态面板
        self.setup_status_panel()
        
        # 设置右侧选项卡
        self.setup_main_tabs()
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 游戏菜单
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="游戏", menu=game_menu)
        game_menu.add_command(label="新游戏", command=self.new_game)
        game_menu.add_command(label="保存游戏", command=self.save_game)
        game_menu.add_command(label="载入游戏", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self.quit_game)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="在线模式", command=self.toggle_online_mode)
        settings_menu.add_command(label="音效设置", command=self.sound_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="游戏说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def setup_status_panel(self):
        """设置状态面板"""
        # 玩家信息框
        player_frame = ttk.LabelFrame(self.left_panel, text="玩家信息", padding=10)
        player_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.player_name_var = tk.StringVar(value="配送员小王")
        self.level_var = tk.StringVar(value="等级: 1")
        self.experience_var = tk.StringVar(value="经验: 0/100")
        self.credit_var = tk.StringVar(value="信用分: 100")
        
        tk.Label(player_frame, textvariable=self.player_name_var, font=("Arial", 12, "bold")).pack()
        tk.Label(player_frame, textvariable=self.level_var).pack()
        tk.Label(player_frame, textvariable=self.experience_var).pack()
        tk.Label(player_frame, textvariable=self.credit_var).pack()
        
        # 财务状况框
        finance_frame = ttk.LabelFrame(self.left_panel, text="财务状况", padding=10)
        finance_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.delivery_coins_var = tk.StringVar(value="外卖币: ¥100.00")
        self.savings_var = tk.StringVar(value="存款: ¥0.00")
        self.debt_var = tk.StringVar(value="负债: ¥50,000.00")
        
        tk.Label(finance_frame, textvariable=self.delivery_coins_var).pack()
        tk.Label(finance_frame, textvariable=self.savings_var).pack()
        tk.Label(finance_frame, textvariable=self.debt_var, fg="red").pack()
        
        # 当前状态框
        status_frame = ttk.LabelFrame(self.left_panel, text="当前状态", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.weather_var = tk.StringVar(value="天气: 晴天")
        self.location_var = tk.StringVar(value="位置: 蚂蚁窝")
        self.stamina_var = tk.StringVar(value="体力: 100/100")
        self.time_var = tk.StringVar(value="时间: 09:00")
        
        tk.Label(status_frame, textvariable=self.weather_var).pack()
        tk.Label(status_frame, textvariable=self.location_var).pack()
        tk.Label(status_frame, textvariable=self.stamina_var).pack()
        tk.Label(status_frame, textvariable=self.time_var).pack()
        
        # 今日统计框
        stats_frame = ttk.LabelFrame(self.left_panel, text="今日统计", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.orders_today_var = tk.StringVar(value="完成订单: 0")
        self.earnings_today_var = tk.StringVar(value="今日收入: ¥0.00")
        self.tips_today_var = tk.StringVar(value="今日小费: ¥0.00")
        
        tk.Label(stats_frame, textvariable=self.orders_today_var).pack()
        tk.Label(stats_frame, textvariable=self.earnings_today_var).pack()
        tk.Label(stats_frame, textvariable=self.tips_today_var).pack()
        
        # 快捷操作按钮
        action_frame = ttk.LabelFrame(self.left_panel, text="快捷操作", padding=10)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="休息恢复体力", command=self.rest_action).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="查看消息", command=self.view_messages).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="装备管理", command=self.equipment_management).pack(fill=tk.X, pady=2)
    
    def setup_main_tabs(self):
        """设置主要选项卡"""
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 订单配送选项卡
        self.setup_order_tab()
        
        # 客户互动选项卡
        self.setup_customer_tab()
        
        # 投资理财选项卡
        self.setup_investment_tab()
        
        # 技能学习选项卡
        self.setup_skill_tab()
        
        # 数据统计选项卡
        self.setup_stats_tab()
    
    def setup_order_tab(self):
        """设置订单配送选项卡"""
        order_frame = ttk.Frame(self.notebook)
        self.notebook.add(order_frame, text="订单配送")
        
        # 顶部按钮区域
        button_frame = ttk.Frame(order_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="刷新订单", command=self.refresh_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看路况", command=self.view_traffic).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="配送设置", command=self.delivery_settings).pack(side=tk.LEFT, padx=5)
        
        # 订单列表
        list_frame = ttk.LabelFrame(order_frame, text="可接订单")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ('ID', '餐厅', '客户', '起点', '终点', '距离', '费用', '优先级', '预计时间')
        self.order_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # 设置列宽和标题
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=100)
        
        # 滚动条
        order_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=order_scrollbar.set)
        
        self.order_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        order_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 订单详情和操作区域
        detail_frame = ttk.LabelFrame(order_frame, text="订单详情")
        detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.order_detail_text = scrolledtext.ScrolledText(detail_frame, height=6, wrap=tk.WORD)
        self.order_detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        action_frame = ttk.Frame(detail_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="接单", command=self.accept_order, style="Accept.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="拒绝", command=self.reject_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="开始配送", command=self.start_delivery).pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.order_tree.bind('<<TreeviewSelect>>', self.on_order_select)
        
        # 初始化订单列表
        self.available_orders = []
        self.selected_order = None
        self.refresh_orders()
    
    def setup_customer_tab(self):
        """设置客户互动选项卡"""
        customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(customer_frame, text="客户互动")
        
        # 模式选择
        mode_frame = ttk.LabelFrame(customer_frame, text="对话模式")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dialogue_mode_var = tk.StringVar(value="离线模式")
        ttk.Radiobutton(mode_frame, text="离线模式", variable=self.dialogue_mode_var, 
                       value="离线模式").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="在线AI模式", variable=self.dialogue_mode_var, 
                       value="在线模式").pack(side=tk.LEFT, padx=10)
        
        # 客户信息显示
        customer_info_frame = ttk.LabelFrame(customer_frame, text="当前客户")
        customer_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.customer_info_text = scrolledtext.ScrolledText(customer_info_frame, height=4, wrap=tk.WORD)
        self.customer_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 对话历史
        dialogue_frame = ttk.LabelFrame(customer_frame, text="对话记录")
        dialogue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.dialogue_text = scrolledtext.ScrolledText(dialogue_frame, wrap=tk.WORD)
        self.dialogue_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 对话选项
        options_frame = ttk.LabelFrame(customer_frame, text="回复选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dialogue_options_frame = ttk.Frame(options_frame)
        self.dialogue_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 互动历史分析
        analysis_frame = ttk.Frame(customer_frame)
        analysis_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(analysis_frame, text="查看互动历史", command=self.view_interaction_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(analysis_frame, text="客户模式分析", command=self.analyze_customer_patterns).pack(side=tk.LEFT, padx=5)
    
    def setup_investment_tab(self):
        """设置投资理财选项卡"""
        investment_frame = ttk.Frame(self.notebook)
        self.notebook.add(investment_frame, text="投资理财")
        
        # 创建子选项卡
        investment_notebook = ttk.Notebook(investment_frame)
        investment_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 股票投资
        self.setup_stock_tab(investment_notebook)
        
        # 彩票购买
        self.setup_lottery_tab(investment_notebook)
        
        # 支出管理
        self.setup_expense_tab(investment_notebook)
    
    def setup_stock_tab(self, parent_notebook):
        """设置股票投资选项卡"""
        stock_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(stock_frame, text="股票投资")
        
        # 左侧股票列表
        left_stock_frame = ttk.Frame(stock_frame)
        left_stock_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 股票市场
        market_frame = ttk.LabelFrame(left_stock_frame, text="股票市场")
        market_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 股票列表
        stock_columns = ('代码', '名称', '价格', '涨跌幅', '成交量')
        self.stock_tree = ttk.Treeview(market_frame, columns=stock_columns, show='headings', height=12)
        
        for col in stock_columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=80)
        
        stock_scrollbar = ttk.Scrollbar(market_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=stock_scrollbar.set)
        
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stock_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧交易和持仓
        right_stock_frame = ttk.Frame(stock_frame)
        right_stock_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # 交易面板
        trade_frame = ttk.LabelFrame(right_stock_frame, text="股票交易", width=300)
        trade_frame.pack(fill=tk.X, pady=5)
        trade_frame.pack_propagate(False)
        
        tk.Label(trade_frame, text="股票代码:").pack(anchor=tk.W, padx=5)
        self.stock_symbol_var = tk.StringVar()
        ttk.Entry(trade_frame, textvariable=self.stock_symbol_var).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(trade_frame, text="交易数量:").pack(anchor=tk.W, padx=5)
        self.stock_quantity_var = tk.StringVar()
        ttk.Entry(trade_frame, textvariable=self.stock_quantity_var).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(trade_frame, text="杠杆倍数:").pack(anchor=tk.W, padx=5)
        self.leverage_var = tk.StringVar(value="1.0")
        leverage_scale = ttk.Scale(trade_frame, from_=1.0, to=5.0, variable=self.leverage_var, orient=tk.HORIZONTAL)
        leverage_scale.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(trade_frame, textvariable=self.leverage_var).pack(anchor=tk.W, padx=5)
        
        trade_buttons = ttk.Frame(trade_frame)
        trade_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(trade_buttons, text="买入", command=self.buy_stock).pack(side=tk.LEFT, padx=2)
        ttk.Button(trade_buttons, text="卖出", command=self.sell_stock).pack(side=tk.LEFT, padx=2)
        
        # 持仓面板
        position_frame = ttk.LabelFrame(right_stock_frame, text="持仓信息")
        position_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.position_text = scrolledtext.ScrolledText(position_frame, height=10, wrap=tk.WORD)
        self.position_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定股票选择事件
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_stock_select)
        
        # 更新股票数据
        self.update_stock_data()
    
    def setup_lottery_tab(self, parent_notebook):
        """设置彩票购买选项卡"""
        lottery_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(lottery_frame, text="彩票购买")
        
        # 彩票类型选择
        type_frame = ttk.LabelFrame(lottery_frame, text="彩票类型")
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lottery_type_var = tk.StringVar(value="双色球")
        lottery_types = ["双色球", "大乐透", "刮刮乐"]
        
        for lottery_type in lottery_types:
            ttk.Radiobutton(type_frame, text=lottery_type, variable=self.lottery_type_var, 
                           value=lottery_type).pack(side=tk.LEFT, padx=20)
        
        # 选号区域
        number_frame = ttk.LabelFrame(lottery_frame, text="选号区域")
        number_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lottery_numbers_text = scrolledtext.ScrolledText(number_frame, height=4, wrap=tk.WORD)
        self.lottery_numbers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 购买按钮
        buy_frame = ttk.Frame(lottery_frame)
        buy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buy_frame, text="随机选号", command=self.random_lottery_numbers).pack(side=tk.LEFT, padx=5)
        ttk.Button(buy_frame, text="购买彩票", command=self.buy_lottery).pack(side=tk.LEFT, padx=5)
        ttk.Button(buy_frame, text="查看历史", command=self.view_lottery_history).pack(side=tk.LEFT, padx=5)
        
        # 开奖结果
        result_frame = ttk.LabelFrame(lottery_frame, text="开奖结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.lottery_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.lottery_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_expense_tab(self, parent_notebook):
        """设置支出管理选项卡"""
        expense_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(expense_frame, text="支出管理")
        
        # 月度支出概览
        overview_frame = ttk.LabelFrame(expense_frame, text="月度支出概览")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建支出图表
        self.expense_figure, self.expense_ax = plt.subplots(figsize=(8, 4))
        self.expense_canvas = FigureCanvasTkAgg(self.expense_figure, overview_frame)
        self.expense_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 支出详情
        detail_frame = ttk.LabelFrame(expense_frame, text="支出详情")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.expense_detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD)
        self.expense_detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        expense_buttons = ttk.Frame(expense_frame)
        expense_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(expense_buttons, text="支付月费", command=self.pay_monthly_expenses).pack(side=tk.LEFT, padx=5)
        ttk.Button(expense_buttons, text="购买医保", command=self.buy_insurance).pack(side=tk.LEFT, padx=5)
        ttk.Button(expense_buttons, text="还债", command=self.pay_debt).pack(side=tk.LEFT, padx=5)
        
        self.update_expense_chart()
    
    def setup_skill_tab(self):
        """设置技能学习选项卡"""
        skill_frame = ttk.Frame(self.notebook)
        self.notebook.add(skill_frame, text="技能学习")
        
        # 创建子选项卡
        skill_notebook = ttk.Notebook(skill_frame)
        skill_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 夜校学习
        self.setup_night_school_tab(skill_notebook)
        
        # 职业转换
        self.setup_career_tab(skill_notebook)
        
        # 技能面板
        self.setup_skill_panel_tab(skill_notebook)
    
    def setup_night_school_tab(self, parent_notebook):
        """设置夜校学习选项卡"""
        school_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(school_frame, text="夜校学习")
        
        # 课程列表
        course_frame = ttk.LabelFrame(school_frame, text="可选课程")
        course_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        course_columns = ('课程', '时长', '费用', '难度', '说明')
        self.course_tree = ttk.Treeview(course_frame, columns=course_columns, show='headings', height=8)
        
        for col in course_columns:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=120)
        
        course_scrollbar = ttk.Scrollbar(course_frame, orient=tk.VERTICAL, command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scrollbar.set)
        
        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        course_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 学习控制
        study_frame = ttk.LabelFrame(school_frame, text="学习控制")
        study_frame.pack(fill=tk.X, padx=5, pady=5)
        
        control_frame = ttk.Frame(study_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(control_frame, text="学习时长(分钟):").pack(side=tk.LEFT)
        self.study_duration_var = tk.StringVar(value="60")
        study_duration_spinbox = ttk.Spinbox(control_frame, from_=30, to=180, textvariable=self.study_duration_var, width=10)
        study_duration_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="报名课程", command=self.enroll_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="开始学习", command=self.start_study).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="参加考试", command=self.take_exam).pack(side=tk.LEFT, padx=5)
        
        # 学习进度
        progress_frame = ttk.LabelFrame(school_frame, text="学习进度")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.study_progress_text = scrolledtext.ScrolledText(progress_frame, height=6, wrap=tk.WORD)
        self.study_progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 加载课程数据
        self.update_course_list()
    
    def setup_career_tab(self, parent_notebook):
        """设置职业转换选项卡"""
        career_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(career_frame, text="职业转换")
        
        # 职业选择
        career_select_frame = ttk.LabelFrame(career_frame, text="可选职业")
        career_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.career_var = tk.StringVar()
        careers = ["公务员", "企业管理", "客服主管", "培训师"]
        
        for career in careers:
            ttk.Radiobutton(career_select_frame, text=career, variable=self.career_var, 
                           value=career).pack(side=tk.LEFT, padx=20)
        
        # 职业要求
        requirement_frame = ttk.LabelFrame(career_frame, text="职业要求")
        requirement_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.career_requirement_text = scrolledtext.ScrolledText(requirement_frame, wrap=tk.WORD)
        self.career_requirement_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        career_buttons = ttk.Frame(career_frame)
        career_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(career_buttons, text="检查资格", command=self.check_career_eligibility).pack(side=tk.LEFT, padx=5)
        ttk.Button(career_buttons, text="申请转职", command=self.attempt_career_transition).pack(side=tk.LEFT, padx=5)
        
        # 绑定职业选择事件
        self.career_var.trace('w', self.on_career_select)
    
    def setup_skill_panel_tab(self, parent_notebook):
        """设置技能面板选项卡"""
        panel_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(panel_frame, text="技能面板")
        
        # 技能雷达图
        radar_frame = ttk.LabelFrame(panel_frame, text="技能雷达图")
        radar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建技能雷达图
        self.skill_figure, self.skill_ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
        self.skill_canvas = FigureCanvasTkAgg(self.skill_figure, radar_frame)
        self.skill_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 技能详情
        skill_detail_frame = ttk.LabelFrame(panel_frame, text="技能详情")
        skill_detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.skill_detail_text = scrolledtext.ScrolledText(skill_detail_frame, height=6, wrap=tk.WORD)
        self.skill_detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_skill_radar()
    
    def setup_stats_tab(self):
        """设置数据统计选项卡"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="数据统计")
        
        # 统计图表
        chart_frame = ttk.LabelFrame(stats_frame, text="数据图表")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建统计图表
        self.stats_figure, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.stats_canvas = FigureCanvasTkAgg(self.stats_figure, chart_frame)
        self.stats_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 统计控制
        control_frame = ttk.Frame(stats_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="更新统计", command=self.update_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="导出数据", command=self.export_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="生成报告", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        self.update_statistics()
    
    # 游戏循环和更新方法
    def start_game_loop(self):
        """启动游戏循环"""
        def game_loop():
            while self.game_running:
                try:
                    self.update_game_state()
                    time.sleep(1)  # 每秒更新一次
                except Exception as e:
                    print(f"游戏循环错误: {e}")
                    break
        
        self.game_thread = threading.Thread(target=game_loop, daemon=True)
        self.game_thread.start()
        
        # 启动GUI更新
        self.update_gui()
    
    def update_game_state(self):
        """更新游戏状态"""
        # 更新股票价格
        self.stock_market.update_prices()
        
        # 更新持仓
        self.portfolio.update_positions(self.stock_market)
        
        # 处理疲劳值
        if self.game_state.fatigue_level > 80:
            self.game_state.attributes.stamina = max(0, self.game_state.attributes.stamina - 1)
        
        # 时间推进
        self.game_state.current_time = datetime.now()
    
    def update_gui(self):
        """更新GUI界面"""
        try:
            # 更新状态面板
            self.update_status_panel()
            
            # 更新股票数据
            if hasattr(self, 'stock_tree'):
                self.root.after_idle(self.update_stock_data)
            
            # 更新持仓信息
            if hasattr(self, 'position_text'):
                self.root.after_idle(self.update_position_display)
            
        except Exception as e:
            print(f"GUI更新错误: {e}")
        
        # 每3秒更新一次
        self.root.after(3000, self.update_gui)
    
    def update_status_panel(self):
        """更新状态面板"""
        # 更新玩家信息
        self.level_var.set(f"等级: {self.game_state.attributes.level}")
        self.experience_var.set(f"经验: {self.game_state.attributes.experience}/100")
        self.credit_var.set(f"信用分: {self.game_state.attributes.credit_score}")
        
        # 更新财务信息
        self.delivery_coins_var.set(f"外卖币: ¥{self.game_state.finances.delivery_coins:.2f}")
        self.savings_var.set(f"存款: ¥{self.game_state.finances.savings:.2f}")
        self.debt_var.set(f"负债: ¥{self.game_state.finances.debt:,.2f}")
        
        # 更新状态信息
        self.weather_var.set(f"天气: {self.game_state.weather.value}")
        self.location_var.set(f"位置: {self.game_state.current_location.value}")
        self.stamina_var.set(f"体力: {self.game_state.attributes.stamina}/100")
        self.time_var.set(f"时间: {self.game_state.current_time.strftime('%H:%M')}")
        
        # 更新统计信息
        self.orders_today_var.set(f"完成订单: {self.game_state.stats.successful_deliveries}")
        self.earnings_today_var.set(f"今日收入: ¥{self.game_state.stats.total_earnings:.2f}")
        self.tips_today_var.set(f"今日小费: ¥{self.game_state.stats.total_tips:.2f}")
    
    # 各种事件处理方法
    def refresh_orders(self):
        """刷新订单列表"""
        try:
            # 清空现有订单
            for item in self.order_tree.get_children():
                self.order_tree.delete(item)
            
            # 生成新订单
            self.available_orders = []
            current_hour = self.game_state.current_time.hour
            
            for _ in range(random.randint(5, 15)):
                order = self.order_generator.generate_order(self.game_state.weather, current_hour)
                self.available_orders.append(order)
                
                # 添加到树形视图
                total_fee = order.base_fee + order.weather_bonus + order.peak_hour_bonus
                
                # 根据优先级设置颜色
                tags = []
                if order.priority.value == "S级":
                    tags = ['high_risk']
                elif order.priority.value == "D级":
                    tags = ['safe']
                
                self.order_tree.insert('', 'end', values=(
                    order.order_id[-6:],  # 显示订单ID后6位
                    order.restaurant_name,
                    order.customer_name,
                    order.pickup_district.value,
                    order.delivery_district.value,
                    f"{order.distance_km}km",
                    f"¥{total_fee:.2f}",
                    order.priority.value,
                    f"{order.estimated_time}分钟"
                ), tags=tags)
            
            # 设置标签样式
            self.order_tree.tag_configure('high_risk', background='#ffcccc')
            self.order_tree.tag_configure('safe', background='#ccffcc')
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新订单失败: {e}")
    
    def on_order_select(self, event):
        """订单选择事件"""
        selection = self.order_tree.selection()
        if selection:
            item = self.order_tree.item(selection[0])
            order_id_short = str(item['values'][0])
            
            # 找到对应的完整订单
            for order in self.available_orders:
                if order.order_id.endswith(order_id_short):
                    self.selected_order = order
                    self.display_order_details(order)
                    break
    
    def display_order_details(self, order):
        """显示订单详情"""
        details = f"""
订单ID: {order.order_id}
餐厅: {order.restaurant_name}
客户: {order.customer_name} ({order.customer_type.value})
取餐地址: {order.pickup_district.value}
送餐地址: {order.delivery_district.value}
距离: {order.distance_km}km
预计时间: {order.estimated_time}分钟

费用明细:
- 基础费用: ¥{order.base_fee:.2f}
- 天气奖励: ¥{order.weather_bonus:.2f}
- 高峰奖励: ¥{order.peak_hour_bonus:.2f}
- 总计: ¥{order.base_fee + order.weather_bonus + order.peak_hour_bonus:.2f}

特殊要求:
{chr(10).join(f"- {req}" for req in order.special_requirements)}

风险评估:
- 投诉概率: {order.complaint_probability*100:.1f}%
- 小费概率: {order.tip_probability*100:.1f}%
        """.strip()
        
        self.order_detail_text.delete(1.0, tk.END)
        self.order_detail_text.insert(1.0, details)
    
    def reject_order(self):
        """拒绝订单"""
        if not self.selected_order:
            messagebox.showwarning("警告", "请先选择一个订单")
            return
        
        # 显示拒绝确认
        if messagebox.askyesno("确认拒绝", f"确定要拒绝订单 {self.selected_order.order_id[-6:]} 吗？"):
            # 从可用订单列表中移除
            self.available_orders.remove(self.selected_order)
            
            # 清除选中的订单
            self.selected_order = None
            self.order_detail_text.delete(1.0, tk.END)
            
            # 刷新订单列表
            self.refresh_orders()
            
            messagebox.showinfo("已拒绝", "订单已拒绝")
    def accept_order(self):
        """接受订单"""
        if not self.selected_order:
            messagebox.showwarning("警告", "请先选择一个订单")
            return
        
        if self.game_state.attributes.stamina < 20:
            messagebox.showwarning("警告", "体力不足，请先休息")
            return
        
        # 接受订单
        self.selected_order.status = "已接单"
        messagebox.showinfo("成功", f"已接受订单 {self.selected_order.order_id[-6:]}")
        
        # 从可用订单列表中移除
        self.available_orders.remove(self.selected_order)
        self.refresh_orders()
    
    def start_delivery(self):
        """开始配送"""
        if not self.selected_order or self.selected_order.status != "已接单":
            messagebox.showwarning("警告", "没有可配送的订单")
            return
        
        # 模拟配送过程
        result = self.delivery_simulator.simulate_delivery(self.selected_order)
        
        # 更新游戏状态
        if result['success']:
            self.game_state.finances.delivery_coins += result['earnings']
            self.game_state.stats.successful_deliveries += 1
            self.game_state.stats.total_earnings += result['earnings']
            self.game_state.stats.total_tips += result['tip']
            self.game_state.attributes.experience += result['experience_gained']
            
            # 检查升级
            if self.game_state.attributes.experience >= 100:
                self.game_state.attributes.level += 1
                self.game_state.attributes.experience = 0
                messagebox.showinfo("升级", f"恭喜升级到 {self.game_state.attributes.level} 级！")
            
            message = f"配送成功！\n收入: ¥{result['earnings']:.2f}"
            if result['tip'] > 0:
                message += f"\n小费: ¥{result['tip']:.2f}"
            if result['complaint']:
                message += "\n收到客户投诉，信用分-5"
            
            # 处理随机事件
            if result['events']:
                event_msg = "\n\n配送过程中发生的事件:"
                for event in result['events']:
                    event_msg += f"\n- {event['description']}"
                message += event_msg
            
            messagebox.showinfo("配送完成", message)
            
            # 触发客户互动
            self.trigger_customer_interaction(self.selected_order, "正常送达")
        else:
            messagebox.showerror("配送失败", "配送过程中发生意外")
        
        # 清除选中的订单
        self.selected_order = None
        self.order_detail_text.delete(1.0, tk.END)
    
    def trigger_customer_interaction(self, order, trigger):
        """触发客户互动"""
        # 切换到客户互动选项卡
        self.notebook.select(1)  # 客户互动是第二个选项卡
        
        # 显示客户信息
        customer_info = f"""
当前客户: {order.customer_name}
客户类型: {order.customer_type.value}
订单地址: {order.delivery_district.value}
配送情况: {trigger}
        """.strip()
        
        self.customer_info_text.delete(1.0, tk.END)
        self.customer_info_text.insert(1.0, customer_info)
        
        # 获取互动结果
        if self.dialogue_mode_var.get() == "离线模式":
            self.customer_system.mode = DialogueMode.OFFLINE
        else:
            self.customer_system.mode = DialogueMode.ONLINE
        
        interaction_result = self.customer_system.interact_with_customer(order, trigger)
        
        # 显示对话
        self.display_customer_dialogue(order, interaction_result)
    
    def display_customer_dialogue(self, order, interaction_result):
        """显示客户对话"""
        # 添加对话记录
        dialogue_entry = f"""
[{datetime.now().strftime('%H:%M')}] 配送员: {interaction_result.get('options_used', '正常配送完成')}
[{datetime.now().strftime('%H:%M')}] {order.customer_name}: {interaction_result.get('customer_response', '谢谢')}

"""
        
        self.dialogue_text.insert(tk.END, dialogue_entry)
        self.dialogue_text.see(tk.END)
        
        # 显示可用选项（如果有）
        self.clear_dialogue_options()
        if 'available_options' in interaction_result:
            for i, option in enumerate(interaction_result['available_options']):
                btn = ttk.Button(self.dialogue_options_frame, text=option, 
                               command=lambda opt=option: self.select_dialogue_option(opt))
                btn.pack(side=tk.LEFT, padx=5)
    
    def clear_dialogue_options(self):
        """清除对话选项"""
        for widget in self.dialogue_options_frame.winfo_children():
            widget.destroy()
    
    def select_dialogue_option(self, option):
        """选择对话选项"""
        self.dialogue_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M')}] 您选择了: {option}\n\n")
        self.dialogue_text.see(tk.END)
        self.clear_dialogue_options()
    
    # 股票交易相关方法
    def update_stock_data(self):
        """更新股票数据"""
        try:
            # 清空现有数据
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            
            # 添加股票数据
            for stock in self.stock_market.get_all_stocks():
                # 根据涨跌设置颜色
                tags = []
                if stock.change_percent > 0:
                    tags = ['positive']
                elif stock.change_percent < 0:
                    tags = ['negative']
                
                self.stock_tree.insert('', 'end', values=(
                    stock.symbol,
                    stock.name,
                    f"¥{stock.price:.2f}",
                    f"{stock.change_percent:+.2f}%",
                    f"{stock.volume:,}"
                ), tags=tags)
            
            # 设置标签样式
            self.stock_tree.tag_configure('positive', foreground='red')
            self.stock_tree.tag_configure('negative', foreground='green')
            
        except Exception as e:
            print(f"更新股票数据错误: {e}")
    
    def on_stock_select(self, event):
        """股票选择事件"""
        selection = self.stock_tree.selection()
        if selection:
            item = self.stock_tree.item(selection[0])
            symbol = item['values'][0]
            self.stock_symbol_var.set(symbol)
    
    def buy_stock(self):
        """买入股票"""
        try:
            symbol = self.stock_symbol_var.get()
            quantity = int(self.stock_quantity_var.get())
            leverage = float(self.leverage_var.get())
            
            stock = self.stock_market.get_stock_info(symbol)
            if not stock:
                messagebox.showerror("错误", "股票代码不存在")
                return
            
            result = self.portfolio.buy_stock(symbol, quantity, stock.price, leverage)
            
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self.update_position_display()
            else:
                messagebox.showerror("失败", result['message'])
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"买入失败: {e}")
    
    def sell_stock(self):
        """卖出股票"""
        try:
            symbol = self.stock_symbol_var.get()
            quantity = int(self.stock_quantity_var.get())
            
            stock = self.stock_market.get_stock_info(symbol)
            if not stock:
                messagebox.showerror("错误", "股票代码不存在")
                return
            
            result = self.portfolio.sell_stock(symbol, quantity, stock.price)
            
            if result['success']:
                profit_msg = f"盈亏: ¥{result.get('profit', 0):.2f}"
                messagebox.showinfo("成功", f"{result['message']}\n{profit_msg}")
                self.update_position_display()
            else:
                messagebox.showerror("失败", result['message'])
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"卖出失败: {e}")
    
    def update_position_display(self):
        """更新持仓显示"""
        try:
            self.position_text.delete(1.0, tk.END)
            
            if not self.portfolio.stock_positions:
                self.position_text.insert(1.0, "暂无持仓")
                return
            
            content = "当前持仓:\n\n"
            total_value = 0
            total_profit = 0
            
            for symbol, position in self.portfolio.stock_positions.items():
                stock = self.stock_market.get_stock_info(symbol)
                if stock:
                    position.current_price = stock.price
                    total_value += position.market_value
                    total_profit += position.profit_loss
                    
                    content += f"股票: {symbol} ({stock.name})\n"
                    content += f"持仓: {position.shares}股\n"
                    content += f"成本: ¥{position.avg_cost:.2f}\n"
                    content += f"现价: ¥{position.current_price:.2f}\n"
                    content += f"杠杆: {position.leverage:.1f}倍\n"
                    content += f"市值: ¥{position.market_value:.2f}\n"
                    content += f"盈亏: ¥{position.profit_loss:.2f} ({position.profit_loss_percent:.2f}%)\n"
                    content += "-" * 30 + "\n"
            
            content += f"\n总市值: ¥{total_value:.2f}\n"
            content += f"总盈亏: ¥{total_profit:.2f}\n"
            
            self.position_text.insert(1.0, content)
            
        except Exception as e:
            print(f"更新持仓显示错误: {e}")
    
    # 彩票相关方法
    def random_lottery_numbers(self):
        """随机选号"""
        lottery_type = self.lottery_type_var.get()
        
        if lottery_type == "双色球":
            red_balls = random.sample(range(1, 34), 6)
            blue_ball = random.randint(1, 16)
            numbers = f"红球: {' '.join(f'{n:02d}' for n in sorted(red_balls))}\n蓝球: {blue_ball:02d}"
        elif lottery_type == "大乐透":
            front_balls = random.sample(range(1, 36), 5)
            back_balls = random.sample(range(1, 13), 2)
            numbers = f"前区: {' '.join(f'{n:02d}' for n in sorted(front_balls))}\n后区: {' '.join(f'{n:02d}' for n in sorted(back_balls))}"
        else:
            numbers = "刮刮乐无需选号，直接购买即可"
        
        self.lottery_numbers_text.delete(1.0, tk.END)
        self.lottery_numbers_text.insert(1.0, numbers)
    
    def buy_lottery(self):
        """购买彩票"""
        try:
            from economic_system import LotteryType
            
            lottery_type_map = {
                "双色球": LotteryType.DOUBLE_COLOR_BALL,
                "大乐透": LotteryType.SUPER_LOTTO,
                "刮刮乐": LotteryType.SCRATCH_CARD
            }
            
            lottery_type = lottery_type_map[self.lottery_type_var.get()]
            
            # 获取选号（如果有）
            numbers = None
            if lottery_type != LotteryType.SCRATCH_CARD:
                number_text = self.lottery_numbers_text.get(1.0, tk.END).strip()
                if number_text and ":" in number_text:
                    # 解析选号
                    try:
                        lines = number_text.split('\n')
                        if lottery_type == LotteryType.DOUBLE_COLOR_BALL:
                            red_line = lines[0].split(':')[1].strip()
                            blue_line = lines[1].split(':')[1].strip()
                            red_numbers = [int(n) for n in red_line.split()]
                            blue_number = int(blue_line)
                            numbers = red_numbers + [blue_number]
                        elif lottery_type == LotteryType.SUPER_LOTTO:
                            front_line = lines[0].split(':')[1].strip()
                            back_line = lines[1].split(':')[1].strip()
                            front_numbers = [int(n) for n in front_line.split()]
                            back_numbers = [int(n) for n in back_line.split()]
                            numbers = front_numbers + back_numbers
                    except:
                        numbers = None
            
            # 检查资金
            prices = {"双色球": 2.0, "大乐透": 2.0, "刮刮乐": 10.0}
            price = prices[self.lottery_type_var.get()]
            
            if self.game_state.finances.delivery_coins < price:
                messagebox.showerror("错误", "资金不足")
                return
            
            # 扣除费用
            self.game_state.finances.delivery_coins -= price
            
            # 购买彩票
            result = self.lottery_system.buy_lottery(lottery_type, numbers)
            
            # 显示结果
            self.display_lottery_result(result)
            
            # 如果中奖，增加资金
            if result['prize'] > 0:
                self.game_state.finances.delivery_coins += result['prize']
                messagebox.showinfo("中奖", f"恭喜中奖 ¥{result['prize']:.2f}！")
            
        except Exception as e:
            messagebox.showerror("错误", f"购买彩票失败: {e}")
    
    def display_lottery_result(self, result):
        """显示彩票结果"""
        content = f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if 'winning_numbers' in result:
            content += f"开奖号码: {result['winning_numbers']}\n"
            content += f"您的号码: {result['player_numbers']}\n"
            if 'red_matches' in result:
                content += f"红球匹配: {result['red_matches']}个\n"
                content += f"蓝球匹配: {'是' if result['blue_match'] else '否'}\n"
        
        content += f"奖金: ¥{result['prize']:.2f}\n"
        content += f"成本: ¥{result['cost']:.2f}\n"
        content += f"净收益: ¥{result['prize'] - result['cost']:.2f}\n"
        content += "-" * 40 + "\n\n"
        
        self.lottery_result_text.insert(1.0, content)
    
    # 支出管理相关方法
    def update_expense_chart(self):
        """更新支出图表"""
        try:
            self.expense_ax.clear()
            
            # 获取支出数据
            expenses = self.expense_manager.get_expense_breakdown()
            
            # 创建饼图
            labels = list(expenses.keys())[:-1]  # 排除总计
            values = list(expenses.values())[:-1]
            
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', 
                     '#c2c2f0', '#ffb3e6', '#c4e17f']
            
            self.expense_ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            self.expense_ax.set_title('月度支出分布')
            
            self.expense_canvas.draw()
            
            # 更新支出详情
            detail_text = "月度支出详情:\n\n"
            for category, amount in expenses.items():
                detail_text += f"{category}: ¥{amount:.2f}\n"
            
            self.expense_detail_text.delete(1.0, tk.END)
            self.expense_detail_text.insert(1.0, detail_text)
            
        except Exception as e:
            print(f"更新支出图表错误: {e}")
    
    def pay_monthly_expenses(self):
        """支付月费"""
        result = self.expense_manager.process_monthly_payment()
        
        if result['processed']:
            if result.get('success', True):
                message = f"成功支付月费 ¥{result['total_expense']:.2f}"
                if result.get('rent_increased'):
                    message += f"\n房租上涨: ¥{result['old_rent']:.2f} → ¥{result['new_rent']:.2f}"
                messagebox.showinfo("支付成功", message)
            else:
                messagebox.showerror("支付失败", "资金不足，信用分-20")
        else:
            messagebox.showinfo("提示", result['message'])
        
        self.update_expense_chart()
    
    def buy_insurance(self):
        """购买医保"""
        cost = 500.0
        if self.game_state.finances.delivery_coins >= cost:
            self.game_state.finances.delivery_coins -= cost
            self.game_state.finances.medical_insurance = True
            messagebox.showinfo("成功", "医保购买成功！可享受医疗保障")
        else:
            messagebox.showerror("失败", "资金不足")
    
    def pay_debt(self):
        """还债"""
        # 创建还债对话框
        debt_window = tk.Toplevel(self.root)
        debt_window.title("还债")
        debt_window.geometry("300x150")
        debt_window.grab_set()
        
        tk.Label(debt_window, text=f"当前负债: ¥{self.game_state.finances.debt:.2f}").pack(pady=10)
        tk.Label(debt_window, text="还款金额:").pack()
        
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(debt_window, textvariable=amount_var)
        amount_entry.pack(pady=5)
        
        def confirm_payment():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("错误", "请输入有效金额")
                    return
                
                if amount > self.game_state.finances.delivery_coins:
                    messagebox.showerror("错误", "资金不足")
                    return
                
                if amount > self.game_state.finances.debt:
                    amount = self.game_state.finances.debt
                
                self.game_state.finances.delivery_coins -= amount
                self.game_state.finances.debt -= amount
                
                messagebox.showinfo("成功", f"成功还债 ¥{amount:.2f}")
                debt_window.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效数字")
        
        ttk.Button(debt_window, text="确认还款", command=confirm_payment).pack(pady=10)
        ttk.Button(debt_window, text="取消", command=debt_window.destroy).pack()
    
    # 技能学习相关方法
    def update_course_list(self):
        """更新课程列表"""
        try:
            # 清空现有数据
            for item in self.course_tree.get_children():
                self.course_tree.delete(item)
            
            # 添加课程数据
            for course_type, course in self.night_school.courses.items():
                self.course_tree.insert('', 'end', values=(
                    course.name,
                    f"{course.duration_hours}小时",
                    f"¥{course.cost:.2f}",
                    course.difficulty.value,
                    course.description
                ))
            
        except Exception as e:
            print(f"更新课程列表错误: {e}")
    
    def enroll_course(self):
        """报名课程"""
        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择课程")
            return
        
        try:
            item = self.course_tree.item(selection[0])
            course_name = item['values'][0]
            
            # 找到对应的课程类型
            course_type = None
            for ct, course in self.night_school.courses.items():
                if course.name == course_name:
                    course_type = ct
                    break
            
            if course_type:
                result = self.night_school.enroll_course(course_type, self.game_state)
                
                if result['success']:
                    messagebox.showinfo("成功", result['message'])
                else:
                    messagebox.showerror("失败", result['message'])
            
        except Exception as e:
            messagebox.showerror("错误", f"报名失败: {e}")
    
    def start_study(self):
        """开始学习"""
        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择课程")
            return
        
        try:
            item = self.course_tree.item(selection[0])
            course_name = item['values'][0]
            duration = int(self.study_duration_var.get())
            
            # 找到对应的课程类型
            course_type = None
            for ct, course in self.night_school.courses.items():
                if course.name == course_name:
                    course_type = ct
                    break
            
            if course_type:
                result = self.night_school.study_session(course_type, duration, self.game_state)
                
                # 显示学习结果
                progress_text = f"""
学习课程: {course_name}
学习时长: {duration}分钟
学习效果: {result['effectiveness']*100:.1f}%
获得经验: {result['experience_gained']}点
消耗体力: {result['stamina_cost']}点
累计学习: {result['total_study_time']}分钟

"""
                
                self.study_progress_text.insert(tk.END, progress_text)
                self.study_progress_text.see(tk.END)
                
                messagebox.showinfo("学习完成", f"获得经验 {result['experience_gained']} 点")
            
        except Exception as e:
            messagebox.showerror("错误", f"学习失败: {e}")
    
    def take_exam(self):
        """参加考试"""
        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择课程")
            return
        
        try:
            item = self.course_tree.item(selection[0])
            course_name = item['values'][0]
            
            # 找到对应的课程类型
            course_type = None
            for ct, course in self.night_school.courses.items():
                if course.name == course_name:
                    course_type = ct
                    break
            
            if course_type:
                result = self.night_school.take_exam(course_type, self.game_state)
                
                if result['success']:
                    if result['passed']:
                        messagebox.showinfo("考试通过", result['message'])
                        self.update_skill_radar()
                    else:
                        messagebox.showwarning("考试失败", result['message'])
                else:
                    messagebox.showerror("无法参加考试", result['message'])
            
        except Exception as e:
            messagebox.showerror("错误", f"考试失败: {e}")
    
    def update_skill_radar(self):
        """更新技能雷达图"""
        try:
            self.skill_ax.clear()
            
            # 技能数据
            skills = ['方向感', '情商', '学历', '急救', '沟通', '交通安全']
            values = [
                self.game_state.attributes.direction_sense,
                self.game_state.attributes.emotional_intelligence,
                self.game_state.attributes.education_level,
                getattr(self.game_state.attributes, 'first_aid', 0),
                getattr(self.game_state.attributes, 'communication', 0),
                getattr(self.game_state.attributes, 'traffic_safety', 0)
            ]
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(skills), endpoint=False).tolist()
            values += values[:1]  # 闭合图形
            angles += angles[:1]
            
            # 绘制雷达图
            self.skill_ax.plot(angles, values, 'o-', linewidth=2, label='当前技能')
            self.skill_ax.fill(angles, values, alpha=0.25)
            self.skill_ax.set_xticks(angles[:-1])
            self.skill_ax.set_xticklabels(skills)
            self.skill_ax.set_ylim(0, 10)
            self.skill_ax.set_title('技能雷达图')
            self.skill_ax.grid(True)
            
            self.skill_canvas.draw()
            
            # 更新技能详情
            detail_text = "技能详情:\n\n"
            for skill, value in zip(skills, values[:-1]):
                detail_text += f"{skill}: {value}级\n"
            
            self.skill_detail_text.delete(1.0, tk.END)
            self.skill_detail_text.insert(1.0, detail_text)
            
        except Exception as e:
            print(f"更新技能雷达图错误: {e}")
    
    # 职业转换相关方法
    def on_career_select(self, *args):
        """职业选择事件"""
        career = self.career_var.get()
        if career and career in self.career_transition.available_careers:
            career_info = self.career_transition.available_careers[career]
            
            requirement_text = f"职业: {career}\n\n"
            requirement_text += "技能要求:\n"
            for skill, level in career_info['requirements'].items():
                current_level = getattr(self.game_state.attributes, skill, 0)
                status = "✓" if current_level >= level else "✗"
                requirement_text += f"{status} {skill}: {level}级 (当前: {current_level}级)\n"
            
            requirement_text += f"\n考试难度: {career_info['exam_difficulty'].value}\n"
            requirement_text += "\n职业福利:\n"
            for benefit, value in career_info['benefits'].items():
                requirement_text += f"- {benefit}: {value}\n"
            
            self.career_requirement_text.delete(1.0, tk.END)
            self.career_requirement_text.insert(1.0, requirement_text)
    
    def check_career_eligibility(self):
        """检查职业资格"""
        career = self.career_var.get()
        if not career:
            messagebox.showwarning("警告", "请先选择职业")
            return
        
        result = self.career_transition.check_eligibility(career, self.game_state)
        
        if result['eligible']:
            messagebox.showinfo("资格检查", result['message'])
        else:
            messagebox.showwarning("资格不足", result['message'])
    
    def attempt_career_transition(self):
        """尝试职业转换"""
        career = self.career_var.get()
        if not career:
            messagebox.showwarning("警告", "请先选择职业")
            return
        
        result = self.career_transition.attempt_transition(career, self.game_state)
        
        if result['success']:
            messagebox.showinfo("转职成功", result['message'])
            # 这里可以添加结局触发逻辑
        else:
            messagebox.showwarning("转职失败", result['message'])
    
    # 统计相关方法
    def update_statistics(self):
        """更新统计数据"""
        try:
            # 清除所有子图
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
            
            # 图1: 收入趋势
            days = list(range(1, 31))
            earnings = [random.uniform(100, 500) for _ in days]  # 模拟数据
            self.ax1.plot(days, earnings, marker='o')
            self.ax1.set_title('月度收入趋势')
            self.ax1.set_xlabel('日期')
            self.ax1.set_ylabel('收入(元)')
            
            # 图2: 订单类型分布
            order_types = ['S级', 'A级', 'D级']
            order_counts = [self.game_state.stats.total_orders * 0.2, 
                           self.game_state.stats.total_orders * 0.5, 
                           self.game_state.stats.total_orders * 0.3]
            self.ax2.pie(order_counts, labels=order_types, autopct='%1.1f%%')
            self.ax2.set_title('订单类型分布')
            
            # 图3: 客户满意度
            satisfaction_data = ['五星', '四星', '三星', '二星', '一星']
            satisfaction_counts = [self.game_state.stats.five_star_ratings, 20, 5, 2, self.game_state.stats.complaints]
            self.ax3.bar(satisfaction_data, satisfaction_counts, color=['gold', 'silver', 'orange', 'red', 'darkred'])
            self.ax3.set_title('客户评价分布')
            self.ax3.set_ylabel('数量')
            
            # 图4: 技能成长
            skill_names = ['方向感', '情商', '学历']
            skill_values = [self.game_state.attributes.direction_sense, 
                           self.game_state.attributes.emotional_intelligence, 
                           self.game_state.attributes.education_level]
            self.ax4.bar(skill_names, skill_values, color=['blue', 'green', 'purple'])
            self.ax4.set_title('核心技能等级')
            self.ax4.set_ylabel('等级')
            
            plt.tight_layout()
            self.stats_canvas.draw()
            
        except Exception as e:
            print(f"更新统计图表错误: {e}")
    
    def export_statistics(self):
        """导出统计数据"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                stats_data = {
                    'game_state': self.game_state.to_dict(),
                    'export_time': datetime.now().isoformat(),
                    'statistics': {
                        'total_orders': self.game_state.stats.total_orders,
                        'successful_deliveries': self.game_state.stats.successful_deliveries,
                        'total_earnings': self.game_state.stats.total_earnings,
                        'total_tips': self.game_state.stats.total_tips,
                        'complaints': self.game_state.stats.complaints,
                        'five_star_ratings': self.game_state.stats.five_star_ratings
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"统计数据已导出到 {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def generate_report(self):
        """生成游戏报告"""
        try:
            report_window = tk.Toplevel(self.root)
            report_window.title("游戏报告")
            report_window.geometry("600x700")
            
            report_text = scrolledtext.ScrolledText(report_window, wrap=tk.WORD)
            report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 生成报告内容
            report_content = f"""
            送外卖模拟器 - 游戏报告
            ========================
            
            玩家信息:
            - 姓名: {self.game_state.player_name or '配送员小王'}
            - 等级: {self.game_state.attributes.level}
            - 经验: {self.game_state.attributes.experience}
            - 信用分: {self.game_state.attributes.credit_score}
            
            财务状况:
            - 外卖币: ¥{self.game_state.finances.delivery_coins:.2f}
            - 存款: ¥{self.game_state.finances.savings:.2f}
            - 负债: ¥{self.game_state.finances.debt:.2f}
            
            配送统计:
            - 总订单数: {self.game_state.stats.total_orders}
            - 成功配送: {self.game_state.stats.successful_deliveries}
            - 成功率: {(self.game_state.stats.successful_deliveries/max(1, self.game_state.stats.total_orders)*100):.1f}%
            - 总收入: ¥{self.game_state.stats.total_earnings:.2f}
            - 总小费: ¥{self.game_state.stats.total_tips:.2f}
            
            客户反馈:
            - 五星好评: {self.game_state.stats.five_star_ratings}
            - 客户投诉: {self.game_state.stats.complaints}
            - 投诉率: {(self.game_state.stats.complaints/max(1, self.game_state.stats.total_orders)*100):.1f}%
            
            技能发展:
            - 方向感: {self.game_state.attributes.direction_sense}级
            - 情商值: {self.game_state.attributes.emotional_intelligence}级
            - 学历值: {self.game_state.attributes.education_level}级
            
            当前状态:
            - 体力值: {self.game_state.attributes.stamina}/100
            - 疲劳度: {self.game_state.fatigue_level}%
            - 位置: {self.game_state.current_location.value}
            - 天气: {self.game_state.weather.value}
            
            投资情况:
            - 持仓数量: {len(self.portfolio.stock_positions)}
            - 持仓市值: ¥{self.portfolio.get_portfolio_value():.2f}
            - 总盈亏: ¥{self.portfolio.get_total_profit_loss():.2f}
            
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            report_text.insert(1.0, report_content)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报告失败: {e}")
    
    # 其他功能方法
    def rest_action(self):
        """休息恢复体力"""
        if self.game_state.attributes.stamina >= 100:
            messagebox.showinfo("提示", "体力已满，无需休息")
            return
        
        # 消耗时间和金钱
        rest_cost = 10.0
        if self.game_state.finances.delivery_coins >= rest_cost:
            self.game_state.finances.delivery_coins -= rest_cost
            self.game_state.attributes.stamina = min(100, self.game_state.attributes.stamina + 30)
            self.game_state.fatigue_level = max(0, self.game_state.fatigue_level - 20)
            messagebox.showinfo("休息完成", "体力恢复30点，疲劳度降低20点")
        else:
            messagebox.showerror("资金不足", "休息需要¥10.00")
    
    def view_messages(self):
        """查看消息"""
        # 创建消息窗口
        msg_window = tk.Toplevel(self.root)
        msg_window.title("系统消息")
        msg_window.geometry("500x400")
        
        msg_text = scrolledtext.ScrolledText(msg_window, wrap=tk.WORD)
        msg_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 模拟系统消息
        messages = [
            f"[{datetime.now().strftime('%H:%M')}] 系统: 欢迎来到送外卖模拟器！",
            f"[{datetime.now().strftime('%H:%M')}] 平台: 今日有{random.randint(5, 15)}个新订单等待配送",
            f"[{datetime.now().strftime('%H:%M')}] 天气: 当前{self.game_state.weather.value}，注意安全",
        ]
        
        if self.game_state.attributes.credit_score < 80:
            messages.append(f"[{datetime.now().strftime('%H:%M')}] 警告: 信用分过低，请注意服务质量")
        
        if self.game_state.finances.debt > 40000:
            messages.append(f"[{datetime.now().strftime('%H:%M')}] 提醒: 负债较高，建议努力还债")
        
        msg_text.insert(1.0, '\n'.join(messages))
    
    def equipment_management(self):
        """装备管理"""
        # 创建装备管理窗口
        equip_window = tk.Toplevel(self.root)
        equip_window.title("装备管理")
        equip_window.geometry("400x500")
        
        # 当前装备
        current_frame = ttk.LabelFrame(equip_window, text="当前装备")
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        equipment_info = f"""
电池容量: {self.game_state.equipment.battery_capacity}%
防雨篷: {'已安装' if self.game_state.equipment.rain_cover else '未安装'}
货架加固: {'已加固' if self.game_state.equipment.cargo_rack_reinforced else '未加固'}
制服质量: {self.game_state.equipment.uniform_quality}
        """.strip()
        
        tk.Label(current_frame, text=equipment_info, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # 装备升级
        upgrade_frame = ttk.LabelFrame(equip_window, text="装备升级")
        upgrade_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        upgrades = [
            ("电池扩容", "续航+20分钟", 300, "battery_capacity"),
            ("防雨篷", "雨天效率+30%", 200, "rain_cover"),
            ("货架加固", "减少餐损概率", 150, "cargo_rack_reinforced"),
            ("正装制服", "进入高端社区", 500, "uniform_quality")
        ]
        
        for name, desc, price, attr in upgrades:
            frame = ttk.Frame(upgrade_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(frame, text=f"{name} - {desc}").pack(side=tk.LEFT)
            tk.Label(frame, text=f"¥{price}").pack(side=tk.RIGHT, padx=5)
            
            def buy_upgrade(attribute=attr, cost=price):
                if self.game_state.finances.delivery_coins >= cost:
                    self.game_state.finances.delivery_coins -= cost
                    if attribute == "uniform_quality":
                        self.game_state.equipment.uniform_quality = "formal"
                    else:
                        setattr(self.game_state.equipment, attribute, True)
                    messagebox.showinfo("成功", f"{name}升级完成！")
                    equip_window.destroy()
                else:
                    messagebox.showerror("失败", "资金不足")
            
            ttk.Button(frame, text="购买", command=buy_upgrade).pack(side=tk.RIGHT)
    
    # 菜单方法
    def new_game(self):
        """新游戏"""
        if messagebox.askyesno("新游戏", "确定要开始新游戏吗？当前进度将丢失。"):
            self.game_state = GameState()
            self.portfolio = InvestmentPortfolio(self.game_state)
            self.expense_manager = ExpenseManager(self.game_state)
            messagebox.showinfo("新游戏", "新游戏已开始！")
    
    def save_game(self):
        """保存游戏"""
        try:
            self.game_state.save_game()
            messagebox.showinfo("保存成功", "游戏已保存")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存游戏时出错: {e}")
    
    def load_game(self):
        """载入游戏"""
        try:
            if self.game_state.load_game():
                messagebox.showinfo("载入成功", "游戏已载入")
            else:
                messagebox.showerror("载入失败", "找不到保存文件")
        except Exception as e:
            messagebox.showerror("载入失败", f"载入游戏时出错: {e}")
    
    def toggle_online_mode(self):
        """切换在线模式"""
        current_mode = self.customer_system.mode
        if current_mode == DialogueMode.OFFLINE:
            self.customer_system.mode = DialogueMode.ONLINE
            messagebox.showinfo("模式切换", "已切换到在线AI模式")
        else:
            self.customer_system.mode = DialogueMode.OFFLINE
            messagebox.showinfo("模式切换", "已切换到离线模式")
    
    def sound_settings(self):
        """音效设置"""
        messagebox.showinfo("音效设置", "音效设置功能待开发")
    
    def show_help(self):
        """显示帮助"""
        help_window = tk.Toplevel(self.root)
        help_window.title("游戏说明")
        help_window.geometry("600x500")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
        送外卖模拟器 - 游戏说明
        
        游戏目标:
        通过配送外卖赚取收入，提升技能，最终实现人生逆袭。
        
        基本玩法:
        1. 抢单配送 - 在订单配送界面选择合适的订单进行配送
        2. 客户互动 - 与不同类型的客户进行沟通，影响服务质量
        3. 投资理财 - 通过股票投资和彩票增加收入来源
        4. 技能学习 - 在夜校学习提升各项技能
        5. 职业转换 - 达到条件后可以转换到其他职业
        
        系统说明:
        - 体力系统: 配送消耗体力，体力不足需要休息
        - 信用系统: 服务质量影响信用分，信用分影响接单机会
        - 经济系统: 管理收入支出，投资理财增加财富
        - 成长系统: 通过学习和实践提升各项技能
        
        结局条件:
        - 财务自由: 存款达到50万且月收入超过8000
        - 教育逆袭: 完成本科学历并成功转职
        - 社畜轮回: 连续工作365天
        - 更多隐藏结局等你发现...
        
        操作提示:
        - 左侧面板显示实时状态信息
        - 右侧选项卡包含各个功能模块
        - 鼠标悬停可查看详细信息
        - 定期保存游戏进度
        """
        
        help_text.insert(1.0, help_content)
    
    def show_about(self):
        """显示关于"""
        messagebox.showinfo("关于", 
                           "送外卖模拟器 v1.0\n\n"
                           "一款现实主义生存模拟游戏\n"
                           "体验外卖配送员的真实生活\n\n"
                           "开发者: 游戏策划团队\n"
                           "技术栈: Python + tkinter + matplotlib")
    
    def view_traffic(self):
        """查看路况"""
        traffic_window = tk.Toplevel(self.root)
        traffic_window.title("实时路况")
        traffic_window.geometry("500x400")
        
        # 模拟路况数据
        traffic_data = {
            "蚂蚁窝": random.choice(["畅通", "缓慢", "拥堵"]),
            "梧桐巷": random.choice(["畅通", "缓慢", "拥堵"]),
            "创业园": random.choice(["畅通", "缓慢", "拥堵"]),
            "翡翠湾": random.choice(["畅通", "缓慢", "拥堵"])
        }
        
        tk.Label(traffic_window, text="实时路况信息", font=("Arial", 14, "bold")).pack(pady=10)
        
        for district, status in traffic_data.items():
            color = {"畅通": "green", "缓慢": "orange", "拥堵": "red"}[status]
            frame = tk.Frame(traffic_window)
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=district, width=10).pack(side=tk.LEFT)
            tk.Label(frame, text=status, fg=color, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
    
    def delivery_settings(self):
        """配送设置"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("配送设置")
        settings_window.geometry("400x300")
        
        # 自动接单设置
        auto_frame = ttk.LabelFrame(settings_window, text="自动接单设置")
        auto_frame.pack(fill=tk.X, padx=10, pady=5)
        
        auto_accept_var = tk.BooleanVar()
        ttk.Checkbutton(auto_frame, text="启用自动接单", variable=auto_accept_var).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Label(auto_frame, text="最低收入要求:").pack(anchor=tk.W, padx=10)
        min_income_var = tk.StringVar(value="8.00")
        ttk.Entry(auto_frame, textvariable=min_income_var, width=10).pack(anchor=tk.W, padx=10, pady=2)
        
        # 风险偏好设置
        risk_frame = ttk.LabelFrame(settings_window, text="风险偏好")
        risk_frame.pack(fill=tk.X, padx=10, pady=5)
        
        risk_var = tk.StringVar(value="平衡")
        for risk_type in ["保守", "平衡", "激进"]:
            ttk.Radiobutton(risk_frame, text=risk_type, variable=risk_var, value=risk_type).pack(anchor=tk.W, padx=10)
        
        # 保存设置
        def save_settings():
            messagebox.showinfo("设置保存", "设置已保存")
            settings_window.destroy()
        
        ttk.Button(settings_window, text="保存设置", command=save_settings).pack(pady=20)
    
    def view_interaction_history(self):
        """查看互动历史"""
        history_window = tk.Toplevel(self.root)
        history_window.title("互动历史")
        history_window.geometry("700x500")
        
        history_text = scrolledtext.ScrolledText(history_window, wrap=tk.WORD)
        history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        history = self.customer_system.get_interaction_history(20)
        
        if history:
            content = "最近20次客户互动记录:\n\n"
            for record in history:
                content += f"时间: {record['timestamp']}\n"
                content += f"客户类型: {record['customer_type']}\n"
                content += f"触发情况: {record['trigger']}\n"
                content += f"玩家回复: {record['player_choice']}\n"
                content += f"客户反应: {record['customer_response']}\n"
                content += f"影响: {record['impact']}\n"
                content += "-" * 50 + "\n\n"
        else:
            content = "暂无互动历史记录"
        
        history_text.insert(1.0, content)
    
    def analyze_customer_patterns(self):
        """分析客户模式"""
        analysis = self.customer_system.analyze_customer_patterns()
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("客户模式分析")
        analysis_window.geometry("500x400")
        
        analysis_text = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD)
        analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if isinstance(analysis, dict) and 'message' not in analysis:
            content = "客户互动成功率分析:\n\n"
            for customer_type, stats in analysis.items():
                content += f"{customer_type}:\n"
                content += f"  总互动次数: {stats['total']}\n"
                content += f"  正面互动: {stats['positive_impact']}\n"
                content += f"  成功率: {stats['success_rate']*100:.1f}%\n\n"
        else:
            content = analysis.get('message', '暂无数据')
        
        analysis_text.insert(1.0, content)
    
    def view_lottery_history(self):
        """查看彩票历史"""
        messagebox.showinfo("彩票历史", "彩票历史功能待开发")
    
    def quit_game(self):
        """退出游戏"""
        if messagebox.askyesno("退出游戏", "确定要退出游戏吗？"):
            self.game_running = False
            self.root.quit()
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()

# 主启动函数
def main():
    """主函数"""
    try:
        app = GameGUI()
        app.run()
    except Exception as e:
        print(f"游戏启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()