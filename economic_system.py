"""
经济管理系统
Economic Management System
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class StockType(Enum):
    TECH = "科技股"
    FINANCE = "金融股"
    CONSUMER = "消费股"
    MEDICAL = "医药股"
    ENERGY = "能源股"

class LotteryType(Enum):
    DOUBLE_COLOR_BALL = "双色球"
    SUPER_LOTTO = "大乐透"
    SCRATCH_CARD = "刮刮乐"

@dataclass
class Stock:
    """股票数据"""
    symbol: str
    name: str
    stock_type: StockType
    price: float
    change_percent: float
    volume: int
    market_cap: float

@dataclass
class StockPosition:
    """持仓数据"""
    symbol: str
    shares: int
    avg_cost: float
    current_price: float
    leverage: float = 1.0
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price * self.leverage
    
    @property
    def profit_loss(self) -> float:
        return (self.current_price - self.avg_cost) * self.shares * self.leverage
    
    @property
    def profit_loss_percent(self) -> float:
        if self.avg_cost == 0:
            return 0
        return (self.current_price - self.avg_cost) / self.avg_cost * 100

@dataclass
class MonthlyExpense:
    """月度支出"""
    rent: float
    food: float
    utilities: float
    phone: float
    transportation: float
    medical: float
    entertainment: float
    debt_payment: float
    
    @property
    def total(self) -> float:
        return sum([
            self.rent, self.food, self.utilities, self.phone,
            self.transportation, self.medical, self.entertainment, self.debt_payment
        ])

class StockMarket:
    """股票市场模拟"""
    
    def __init__(self):
        self.stocks = self._initialize_stocks()
        self.trading_hours = (9, 15)  # 9:00-15:00
        self.last_update = datetime.now()
    
    def _initialize_stocks(self) -> Dict[str, Stock]:
        """初始化股票数据"""
        stock_data = [
            ("000001", "平安银行", StockType.FINANCE, 12.50),
            ("000002", "万科A", StockType.CONSUMER, 18.20),
            ("000858", "五粮液", StockType.CONSUMER, 158.30),
            ("002415", "海康威视", StockType.TECH, 35.80),
            ("300059", "东方财富", StockType.FINANCE, 15.60),
            ("300750", "宁德时代", StockType.TECH, 420.50),
            ("600036", "招商银行", StockType.FINANCE, 35.20),
            ("600519", "贵州茅台", StockType.CONSUMER, 1680.00),
            ("600887", "伊利股份", StockType.CONSUMER, 32.40),
            ("688111", "金山办公", StockType.TECH, 280.80)
        ]
        
        stocks = {}
        for symbol, name, stock_type, price in stock_data:
            stocks[symbol] = Stock(
                symbol=symbol,
                name=name,
                stock_type=stock_type,
                price=price,
                change_percent=0.0,
                volume=random.randint(10000, 1000000),
                market_cap=price * random.randint(1000000, 10000000)
            )
        
        return stocks
    
    def update_prices(self):
        """更新股价"""
        current_time = datetime.now()
        
        # 只在交易时间更新
        if not (self.trading_hours[0] <= current_time.hour < self.trading_hours[1]):
            return
        
        # 每分钟更新一次
        if (current_time - self.last_update).seconds < 60:
            return
        
        for stock in self.stocks.values():
            # 随机波动 -5% 到 +5%
            change = random.uniform(-0.05, 0.05)
            
            # 根据股票类型调整波动性
            volatility_multipliers = {
                StockType.TECH: 1.5,
                StockType.FINANCE: 0.8,
                StockType.CONSUMER: 1.0,
                StockType.MEDICAL: 1.2,
                StockType.ENERGY: 1.3
            }
            
            change *= volatility_multipliers[stock.stock_type]
            
            new_price = stock.price * (1 + change)
            stock.change_percent = change * 100
            stock.price = round(new_price, 2)
            stock.volume = random.randint(10000, 1000000)
        
        self.last_update = current_time
    
    def get_stock_info(self, symbol: str) -> Optional[Stock]:
        """获取股票信息"""
        return self.stocks.get(symbol)
    
    def get_all_stocks(self) -> List[Stock]:
        """获取所有股票"""
        return list(self.stocks.values())
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        """搜索股票"""
        results = []
        keyword = keyword.lower()
        
        for stock in self.stocks.values():
            if (keyword in stock.name.lower() or 
                keyword in stock.symbol.lower()):
                results.append(stock)
        
        return results

class InvestmentPortfolio:
    """投资组合"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.stock_positions: Dict[str, StockPosition] = {}
        self.transaction_history: List[Dict] = []
        self.max_leverage = 5.0
        self.margin_call_threshold = 0.3  # 30% margin call
    
    def buy_stock(self, symbol: str, shares: int, price: float, leverage: float = 1.0) -> Dict:
        """买入股票"""
        if leverage > self.max_leverage:
            return {'success': False, 'message': f'杠杆倍数不能超过{self.max_leverage}倍'}
        
        cost = shares * price / leverage  # 使用杠杆时实际需要的资金
        
        if cost > self.game_state.finances.delivery_coins:
            return {'success': False, 'message': '资金不足'}
        
        # 扣除资金
        self.game_state.finances.delivery_coins -= cost
        
        # 更新持仓
        if symbol in self.stock_positions:
            position = self.stock_positions[symbol]
            total_cost = position.avg_cost * position.shares + price * shares
            total_shares = position.shares + shares
            position.avg_cost = total_cost / total_shares
            position.shares = total_shares
        else:
            self.stock_positions[symbol] = StockPosition(
                symbol=symbol,
                shares=shares,
                avg_cost=price,
                current_price=price,
                leverage=leverage
            )
        
        # 记录交易
        self.transaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'buy',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'leverage': leverage,
            'cost': cost
        })
        
        return {'success': True, 'message': f'成功买入{shares}股{symbol}'}
    
    def sell_stock(self, symbol: str, shares: int, price: float) -> Dict:
        """卖出股票"""
        if symbol not in self.stock_positions:
            return {'success': False, 'message': '没有该股票持仓'}
        
        position = self.stock_positions[symbol]
        if shares > position.shares:
            return {'success': False, 'message': '持仓不足'}
        
        # 计算收益
        revenue = shares * price * position.leverage
        
        # 更新持仓
        if shares == position.shares:
            del self.stock_positions[symbol]
        else:
            position.shares -= shares
        
        # 增加资金
        self.game_state.finances.delivery_coins += revenue
        
        # 记录交易
        profit = (price - position.avg_cost) * shares * position.leverage
        self.transaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'sell',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'leverage': position.leverage,
            'revenue': revenue,
            'profit': profit
        })
        
        return {
            'success': True, 
            'message': f'成功卖出{shares}股{symbol}',
            'profit': round(profit, 2)
        }
    
    def update_positions(self, market: StockMarket):
        """更新持仓"""
        for symbol, position in self.stock_positions.items():
            stock = market.get_stock_info(symbol)
            if stock:
                position.current_price = stock.price
        
        # 检查爆仓
        self._check_margin_call()
    
    def _check_margin_call(self):
        """检查是否爆仓"""
        for symbol, position in list(self.stock_positions.items()):
            if position.leverage > 1.0:
                loss_percent = -position.profit_loss_percent / 100
                if loss_percent >= self.margin_call_threshold:
                    # 强制平仓
                    self._force_liquidation(symbol, position)
    
    def _force_liquidation(self, symbol: str, position: StockPosition):
        """强制平仓"""
        liquidation_price = position.current_price
        self.sell_stock(symbol, position.shares, liquidation_price)
        
        # 记录爆仓事件
        self.transaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'liquidation',
            'symbol': symbol,
            'shares': position.shares,
            'price': liquidation_price,
            'message': '杠杆爆仓强制平仓'
        })
    
    def get_portfolio_value(self) -> float:
        """获取组合总价值"""
        total_value = 0
        for position in self.stock_positions.values():
            total_value += position.market_value
        return total_value
    
    def get_total_profit_loss(self) -> float:
        """获取总盈亏"""
        total_pl = 0
        for position in self.stock_positions.values():
            total_pl += position.profit_loss
        return total_pl

class LotterySystem:
    """彩票系统"""
    
    def __init__(self):
        self.consecutive_losses = 0
        self.jackpot_probability = 1 / 17720000  # 双色球头奖概率
    
    def buy_lottery(self, lottery_type: LotteryType, numbers: List[int] = None) -> Dict:
        """购买彩票"""
        prices = {
            LotteryType.DOUBLE_COLOR_BALL: 2.0,
            LotteryType.SUPER_LOTTO: 2.0,
            LotteryType.SCRATCH_CARD: 10.0
        }
        
        price = prices[lottery_type]
        
        if lottery_type == LotteryType.DOUBLE_COLOR_BALL:
            return self._play_double_color_ball(price, numbers)
        elif lottery_type == LotteryType.SUPER_LOTTO:
            return self._play_super_lotto(price, numbers)
        else:
            return self._play_scratch_card(price)
    
    def _play_double_color_ball(self, price: float, numbers: List[int] = None) -> Dict:
        """双色球"""
        if not numbers:
            # 随机选号
            red_balls = random.sample(range(1, 34), 6)
            blue_ball = random.randint(1, 16)
            numbers = red_balls + [blue_ball]
        
        # 开奖号码
        winning_red = random.sample(range(1, 34), 6)
        winning_blue = random.randint(1, 16)
        
        # 计算中奖
        red_matches = len(set(numbers[:6]) & set(winning_red))
        blue_match = numbers[6] == winning_blue
        
        prize = self._calculate_double_color_ball_prize(red_matches, blue_match)
        
        if prize > 0:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
        
        return {
            'winning_numbers': winning_red + [winning_blue],
            'player_numbers': numbers,
            'red_matches': red_matches,
            'blue_match': blue_match,
            'prize': prize,
            'cost': price
        }
    
    def _calculate_double_color_ball_prize(self, red_matches: int, blue_match: bool) -> float:
        """计算双色球奖金"""
        # 调整小奖概率（连续未中奖时提高）
        bonus_multiplier = 1 + (self.consecutive_losses * 0.1)
        
        if red_matches == 6 and blue_match:
            return 5000000.0  # 一等奖500万
        elif red_matches == 6:
            return 1000000.0  # 二等奖
        elif red_matches == 5 and blue_match:
            return 3000.0 * bonus_multiplier
        elif red_matches == 5 or (red_matches == 4 and blue_match):
            return 200.0 * bonus_multiplier
        elif red_matches == 4 or (red_matches == 3 and blue_match):
            return 10.0 * bonus_multiplier
        elif blue_match:
            return 5.0 * bonus_multiplier
        else:
            return 0.0
    
    def _play_super_lotto(self, price: float, numbers: List[int] = None) -> Dict:
        """大乐透（简化版）"""
        if not numbers:
            front_numbers = random.sample(range(1, 36), 5)
            back_numbers = random.sample(range(1, 13), 2)
            numbers = front_numbers + back_numbers
        
        winning_front = random.sample(range(1, 36), 5)
        winning_back = random.sample(range(1, 13), 2)
        
        front_matches = len(set(numbers[:5]) & set(winning_front))
        back_matches = len(set(numbers[5:]) & set(winning_back))
        
        prize = self._calculate_super_lotto_prize(front_matches, back_matches)
        
        return {
            'winning_numbers': winning_front + winning_back,
            'player_numbers': numbers,
            'front_matches': front_matches,
            'back_matches': back_matches,
            'prize': prize,
            'cost': price
        }
    
    def _calculate_super_lotto_prize(self, front_matches: int, back_matches: int) -> float:
        """计算大乐透奖金"""
        if front_matches == 5 and back_matches == 2:
            return 10000000.0  # 一等奖1000万
        elif front_matches == 5 and back_matches == 1:
            return 500000.0
        elif front_matches == 5:
            return 10000.0
        elif front_matches == 4 and back_matches == 2:
            return 3000.0
        elif front_matches == 4 and back_matches == 1:
            return 300.0
        elif front_matches == 3 and back_matches == 2:
            return 200.0
        elif front_matches == 4 or (front_matches == 3 and back_matches == 1) or (front_matches == 2 and back_matches == 2):
            return 10.0
        elif front_matches == 3 or (front_matches == 1 and back_matches == 2) or (front_matches == 2 and back_matches == 1) or back_matches == 2:
            return 5.0
        else:
            return 0.0
    
    def _play_scratch_card(self, price: float) -> Dict:
        """刮刮乐"""
        # 简化的刮刮乐，直接随机奖金
        prizes = [0, 10, 20, 50, 100, 500, 1000, 10000]
        probabilities = [0.7, 0.15, 0.08, 0.04, 0.02, 0.008, 0.001, 0.0001]
        
        prize = random.choices(prizes, weights=probabilities)[0]
        
        return {
            'prize': prize,
            'cost': price,
            'type': 'scratch_card'
        }

class ExpenseManager:
    """支出管理"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.monthly_expenses = MonthlyExpense(
            rent=2000.0,
            food=800.0,
            utilities=200.0,
            phone=100.0,
            transportation=300.0,
            medical=0.0,
            entertainment=200.0,
            debt_payment=1000.0
        )
        self.last_payment_date = datetime.now()
    
    def calculate_daily_expenses(self) -> float:
        """计算日常支出"""
        daily_food = random.uniform(20, 50)  # 每日伙食费
        daily_transport = random.uniform(10, 30)  # 交通费
        daily_other = random.uniform(5, 20)  # 其他杂费
        
        return daily_food + daily_transport + daily_other
    
    def process_monthly_payment(self) -> Dict:
        """处理月度支出"""
        current_time = datetime.now()
        
        # 检查是否到了月度支付时间
        if (current_time - self.last_payment_date).days < 30:
            return {'processed': False, 'message': '还未到月度支付时间'}
        
        total_expense = self.monthly_expenses.total
        
        # 房租可能上涨
        if random.random() < 0.1:  # 10%概率房租上涨
            increase_rate = random.uniform(0.05, 0.15)  # 5%-15%上涨
            old_rent = self.monthly_expenses.rent
            self.monthly_expenses.rent *= (1 + increase_rate)
            total_expense = self.monthly_expenses.total
            
            return {
                'processed': True,
                'total_expense': total_expense,
                'rent_increased': True,
                'old_rent': old_rent,
                'new_rent': self.monthly_expenses.rent,
                'increase_rate': increase_rate * 100
            }
        
        # 扣除费用
        if self.game_state.finances.delivery_coins >= total_expense:
            self.game_state.finances.delivery_coins -= total_expense
            self.last_payment_date = current_time
            
            return {
                'processed': True,
                'total_expense': total_expense,
                'success': True
            }
        else:
            # 资金不足，扣信用分
            self.game_state.attributes.credit_score -= 20
            
            return {
                'processed': True,
                'total_expense': total_expense,
                'success': False,
                'credit_penalty': True
            }
    
    def get_expense_breakdown(self) -> Dict:
        """获取支出明细"""
        return {
            '房租': self.monthly_expenses.rent,
            '伙食': self.monthly_expenses.food,
            '水电': self.monthly_expenses.utilities,
            '通讯': self.monthly_expenses.phone,
            '交通': self.monthly_expenses.transportation,
            '医疗': self.monthly_expenses.medical,
            '娱乐': self.monthly_expenses.entertainment,
            '还债': self.monthly_expenses.debt_payment,
            '总计': self.monthly_expenses.total
        }