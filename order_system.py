"""
抢单配送系统
Order and Delivery System
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from game_core import DistrictType, CustomerType, WeatherType

class OrderPriority(Enum):
    S_LEVEL = "S级"  # 高收益高风险
    A_LEVEL = "A级"  # 常规
    D_LEVEL = "D级"  # 安全单

class OrderStatus(Enum):
    AVAILABLE = "可接单"
    ACCEPTED = "已接单"
    PICKED_UP = "已取餐"
    DELIVERED = "已送达"
    CANCELLED = "已取消"

@dataclass
class Order:
    """订单数据结构"""
    order_id: str
    restaurant_name: str
    customer_name: str
    pickup_district: DistrictType
    delivery_district: DistrictType
    customer_type: CustomerType
    priority: OrderPriority
    base_fee: float
    distance_km: float
    estimated_time: int  # 预计配送时间（分钟）
    special_requirements: List[str]
    weather_bonus: float = 0.0
    peak_hour_bonus: float = 0.0
    status: OrderStatus = OrderStatus.AVAILABLE
    complaint_probability: float = 0.0
    tip_probability: float = 0.0

class OrderGenerator:
    """订单生成器"""
    
    def __init__(self):
        self.restaurants = [
            "麦当劳", "肯德基", "沙县小吃", "兰州拉面", "黄焖鸡米饭",
            "海底捞", "西贝莜面村", "外婆家", "新白鹿", "绿茶餐厅"
        ]
        
        self.customer_names = [
            "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
            "郑十一", "王十二", "冯十三", "陈十四", "褚十五", "卫十六"
        ]
        
        self.special_requirements = {
            CustomerType.PROGRAMMER_SHY: ["放门口即可", "不要打电话"],
            CustomerType.RICH_IMPATIENT: ["需要视频验货", "必须带发票"],
            CustomerType.DIFFICULT_ELDERLY: ["必须当面交付", "需要找零"],
            CustomerType.NORMAL: ["正常配送"],
            CustomerType.VIP: ["需要保温袋", "轻拿轻放"]
        }
    
    def generate_order(self, weather: WeatherType, current_hour: int) -> Order:
        """生成随机订单"""
        order_id = f"ORDER_{random.randint(100000, 999999)}"
        restaurant = random.choice(self.restaurants)
        customer = random.choice(self.customer_names)
        
        pickup_district = random.choice(list(DistrictType))
        delivery_district = random.choice(list(DistrictType))
        customer_type = random.choice(list(CustomerType))
        
        # 根据客户类型确定订单优先级
        priority_weights = {
            CustomerType.PROGRAMMER_SHY: [0.1, 0.3, 0.6],  # S, A, D
            CustomerType.RICH_IMPATIENT: [0.7, 0.25, 0.05],
            CustomerType.DIFFICULT_ELDERLY: [0.4, 0.5, 0.1],
            CustomerType.NORMAL: [0.2, 0.6, 0.2],
            CustomerType.VIP: [0.5, 0.4, 0.1]
        }
        
        priority = random.choices(
            list(OrderPriority),
            weights=priority_weights[customer_type]
        )[0]
        
        # 计算基础配送费
        base_fee = self._calculate_base_fee(pickup_district, delivery_district, priority)
        
        # 计算距离
        distance = self._calculate_distance(pickup_district, delivery_district)
        
        # 计算预计时间
        estimated_time = self._calculate_estimated_time(distance, weather)
        
        # 天气奖励
        weather_bonus = self._calculate_weather_bonus(weather, base_fee)
        
        # 高峰期奖励
        peak_hour_bonus = self._calculate_peak_bonus(current_hour, base_fee)
        
        # 特殊要求
        requirements = self.special_requirements[customer_type].copy()
        if weather == WeatherType.RAINY:
            requirements.append("注意防雨")
        
        # 投诉概率
        complaint_prob = self._calculate_complaint_probability(priority, customer_type)
        
        # 小费概率
        tip_prob = self._calculate_tip_probability(delivery_district, customer_type)
        
        return Order(
            order_id=order_id,
            restaurant_name=restaurant,
            customer_name=customer,
            pickup_district=pickup_district,
            delivery_district=delivery_district,
            customer_type=customer_type,
            priority=priority,
            base_fee=base_fee,
            distance_km=distance,
            estimated_time=estimated_time,
            special_requirements=requirements,
            weather_bonus=weather_bonus,
            peak_hour_bonus=peak_hour_bonus,
            complaint_probability=complaint_prob,
            tip_probability=tip_prob
        )
    
    def _calculate_base_fee(self, pickup: DistrictType, delivery: DistrictType, priority: OrderPriority) -> float:
        """计算基础配送费"""
        base_rates = {
            OrderPriority.S_LEVEL: 15.0,
            OrderPriority.A_LEVEL: 8.0,
            OrderPriority.D_LEVEL: 5.0
        }
        
        district_multipliers = {
            DistrictType.ANT_NEST: 1.2,
            DistrictType.WUTONG_LANE: 1.0,
            DistrictType.STARTUP_PARK: 1.1,
            DistrictType.JADE_BAY: 1.5
        }
        
        base = base_rates[priority]
        multiplier = (district_multipliers[pickup] + district_multipliers[delivery]) / 2
        return round(base * multiplier, 2)
    
    def _calculate_distance(self, pickup: DistrictType, delivery: DistrictType) -> float:
        """计算配送距离"""
        if pickup == delivery:
            return round(random.uniform(0.5, 2.0), 1)
        else:
            return round(random.uniform(2.0, 8.0), 1)
    
    def _calculate_estimated_time(self, distance: float, weather: WeatherType) -> int:
        """计算预计配送时间"""
        base_time = distance * 5  # 每公里5分钟
        
        weather_multipliers = {
            WeatherType.SUNNY: 1.0,
            WeatherType.RAINY: 1.3,
            WeatherType.STORMY: 1.6,
            WeatherType.FOGGY: 1.4,
            WeatherType.TYPHOON: 2.0
        }
        
        return int(base_time * weather_multipliers[weather])
    
    def _calculate_weather_bonus(self, weather: WeatherType, base_fee: float) -> float:
        """计算天气奖励"""
        bonuses = {
            WeatherType.SUNNY: 0.0,
            WeatherType.RAINY: 0.3,
            WeatherType.STORMY: 0.8,
            WeatherType.FOGGY: 0.4,
            WeatherType.TYPHOON: 1.5
        }
        
        return round(base_fee * bonuses[weather], 2)
    
    def _calculate_peak_bonus(self, hour: int, base_fee: float) -> float:
        """计算高峰期奖励"""
        peak_hours = [11, 12, 13, 18, 19, 20]  # 午餐和晚餐高峰期
        if hour in peak_hours:
            return round(base_fee * 0.2, 2)
        return 0.0
    
    def _calculate_complaint_probability(self, priority: OrderPriority, customer_type: CustomerType) -> float:
        """计算投诉概率"""
        base_prob = {
            OrderPriority.S_LEVEL: 0.7,
            OrderPriority.A_LEVEL: 0.4,
            OrderPriority.D_LEVEL: 0.05
        }
        
        customer_multipliers = {
            CustomerType.PROGRAMMER_SHY: 0.3,
            CustomerType.RICH_IMPATIENT: 1.5,
            CustomerType.DIFFICULT_ELDERLY: 1.2,
            CustomerType.NORMAL: 1.0,
            CustomerType.VIP: 0.8
        }
        
        return min(0.9, base_prob[priority] * customer_multipliers[customer_type])
    
    def _calculate_tip_probability(self, district: DistrictType, customer_type: CustomerType) -> float:
        """计算小费概率"""
        district_prob = {
            DistrictType.ANT_NEST: 0.1,
            DistrictType.WUTONG_LANE: 0.3,
            DistrictType.STARTUP_PARK: 0.2,
            DistrictType.JADE_BAY: 0.6
        }
        
        customer_multipliers = {
            CustomerType.PROGRAMMER_SHY: 1.2,
            CustomerType.RICH_IMPATIENT: 0.8,
            CustomerType.DIFFICULT_ELDERLY: 0.5,
            CustomerType.NORMAL: 1.0,
            CustomerType.VIP: 1.5
        }
        
        return min(0.8, district_prob[district] * customer_multipliers[customer_type])

class DeliverySimulator:
    """配送模拟器"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.current_orders: List[Order] = []
        self.active_order: Optional[Order] = None
        
    def simulate_delivery(self, order: Order) -> Dict:
        """模拟配送过程"""
        result = {
            'success': True,
            'earnings': 0.0,
            'tip': 0.0,
            'complaint': False,
            'experience_gained': 0,
            'events': []
        }
        
        # 基础收入
        total_earnings = order.base_fee + order.weather_bonus + order.peak_hour_bonus
        
        # 随机事件处理
        events = self._handle_random_events(order)
        result['events'] = events
        
        for event in events:
            if event['type'] == 'accident':
                result['success'] = False
                result['earnings'] = 0
                return result
            elif event['type'] == 'equipment_damage':
                total_earnings -= event['cost']
            elif event['type'] == 'time_bonus':
                total_earnings += event['bonus']
        
        # 小费计算
        if random.random() < order.tip_probability:
            tip_amount = round(random.uniform(2.0, 20.0), 2)
            result['tip'] = tip_amount
            total_earnings += tip_amount
        
        # 投诉检查
        complaint_chance = order.complaint_probability
        
        # 根据玩家属性调整投诉概率
        if self.game_state.attributes.emotional_intelligence > 5:
            complaint_chance *= 0.8
        
        if random.random() < complaint_chance:
            result['complaint'] = True
            self.game_state.attributes.credit_score -= 5
        else:
            # 好评奖励
            self.game_state.stats.five_star_ratings += 1
            self.game_state.attributes.credit_score += 1
        
        result['earnings'] = round(total_earnings, 2)
        result['experience_gained'] = self._calculate_experience(order)
        
        return result
    
    def _handle_random_events(self, order: Order) -> List[Dict]:
        """处理随机事件"""
        events = []
        
        # 恶劣天气事件
        if self.game_state.weather in [WeatherType.RAINY, WeatherType.STORMY]:
            if random.random() < 0.3 and not self.game_state.equipment.rain_cover:
                events.append({
                    'type': 'food_damage',
                    'description': '食物被雨水损坏',
                    'cost': order.base_fee * 0.5
                })
        
        # 交通事故
        if random.random() < 0.05:
            events.append({
                'type': 'accident',
                'description': '发生交通事故',
                'cost': 500.0
            })
        
        # 电池耗尽
        if random.random() < 0.1 and self.game_state.equipment.battery_capacity < 50:
            events.append({
                'type': 'battery_dead',
                'description': '电池耗尽需要推车',
                'time_penalty': 20
            })
        
        # 提前送达奖励
        if random.random() < 0.2 and self.game_state.attributes.direction_sense > 3:
            events.append({
                'type': 'time_bonus',
                'description': '提前送达获得奖励',
                'bonus': 3.0
            })
        
        return events
    
    def _calculate_experience(self, order: Order) -> int:
        """计算经验值获得"""
        base_exp = {
            OrderPriority.S_LEVEL: 50,
            OrderPriority.A_LEVEL: 30,
            OrderPriority.D_LEVEL: 15
        }
        
        exp = base_exp[order.priority]
        
        # 恶劣天气额外经验
        if self.game_state.weather in [WeatherType.RAINY, WeatherType.STORMY]:
            exp += 10
        
        return exp