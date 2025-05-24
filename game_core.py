"""
送外卖模拟器 - 核心游戏系统
Game Core System for Food Delivery Simulator
"""

import random
import json
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import uuid

class WeatherType(Enum):
    SUNNY = "晴天"
    RAINY = "雨天"
    STORMY = "暴雨"
    SNOWY = "雪天"  # 添加此行
    FOGGY = "雾霾"
    TYPHOON = "台风"

class DistrictType(Enum):
    ANT_NEST = "蚂蚁窝"  # 城中村
    WUTONG_LANE = "梧桐巷"  # 老城区
    STARTUP_PARK = "创业园"  # 新兴商圈
    JADE_BAY = "翡翠湾"  # 高端社区

class CustomerType(Enum):
    PROGRAMMER_SHY = "程序员社恐型"
    RICH_IMPATIENT = "催单暴发户型"
    DIFFICULT_ELDERLY = "刁难大妈型"
    NORMAL = "普通顾客"
    VIP = "VIP客户"

@dataclass
class GameStats:
    """游戏统计数据"""
    total_orders: int = 0
    successful_deliveries: int = 0
    complaints: int = 0
    five_star_ratings: int = 0
    total_earnings: float = 0.0
    total_tips: float = 0.0

@dataclass
class PlayerAttributes:
    """玩家属性"""
    direction_sense: int = 1  # 方向感
    emotional_intelligence: int = 1  # 情商值
    education_level: int = 1  # 学历值
    stamina: int = 100  # 体力值
    credit_score: int = 100  # 信用分
    experience: int = 0  # 经验值
    level: int = 1  # 等级

@dataclass
class FinancialStatus:
    """财务状况"""
    delivery_coins: float = 100.0  # 外卖币
    credit_points: int = 100  # 信用点
    debt: float = 50000.0  # 初始负债
    monthly_rent: float = 2000.0  # 月租金
    savings: float = 0.0  # 存款
    medical_insurance: bool = False  # 医保

@dataclass
class DeliveryEquipment:
    """配送装备"""
    battery_capacity: int = 100  # 电池容量
    rain_cover: bool = False  # 防雨篷
    cargo_rack_reinforced: bool = False  # 货架加固
    uniform_quality: str = "basic"  # 制服质量 basic/formal

class GameState:
    """游戏状态管理"""
    
    def __init__(self):
        self.player_name = ""
        self.current_time = datetime.now()
        self.weather = WeatherType.SUNNY
        self.attributes = PlayerAttributes()
        self.finances = FinancialStatus()
        self.equipment = DeliveryEquipment()
        self.stats = GameStats()
        self.is_online = True
        self.fatigue_level = 0
        self.current_location = DistrictType.ANT_NEST
        
    def to_dict(self):
        """转换为字典格式用于保存"""
        return {
            'player_name': self.player_name,
            'current_time': self.current_time.isoformat(),
            'weather': self.weather.value,
            'attributes': asdict(self.attributes),
            'finances': asdict(self.finances),
            'equipment': asdict(self.equipment),
            'stats': asdict(self.stats),
            'fatigue_level': self.fatigue_level,
            'current_location': self.current_location.value
        }
    
    def save_game(self, filename: str = "savegame.json"):
        """保存游戏"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    def load_game(self, filename: str = "savegame.json"):
        """加载游戏"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.player_name = data['player_name']
                self.current_time = datetime.fromisoformat(data['current_time'])
                self.weather = WeatherType(data['weather'])
                self.attributes = PlayerAttributes(**data['attributes'])
                self.finances = FinancialStatus(**data['finances'])
                self.equipment = DeliveryEquipment(**data['equipment'])
                self.stats = GameStats(**data['stats'])
                self.fatigue_level = data['fatigue_level']
                self.current_location = DistrictType(data['current_location'])
                return True
        except FileNotFoundError:
            return False