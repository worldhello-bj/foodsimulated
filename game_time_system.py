"""
游戏时间系统
Game Time System - 管理游戏内的时间流逝
"""

from datetime import datetime, timedelta
from enum import Enum
import random

class TimeOfDay(Enum):
    """一天中的时间段"""
    DAWN = "黎明"       # 05:00-07:00
    MORNING = "上午"    # 07:00-11:00
    NOON = "中午"       # 11:00-13:00
    AFTERNOON = "下午"  # 13:00-17:00
    EVENING = "傍晚"    # 17:00-19:00
    NIGHT = "夜晚"      # 19:00-23:00
    MIDNIGHT = "深夜"   # 23:00-05:00

class GameTimeManager:
    """游戏时间管理器"""
    
    def __init__(self, start_hour=9, start_minute=0):
        # 游戏开始时间（默认上午9点）
        self.game_start_time = datetime(2024, 1, 1, start_hour, start_minute, 0)
        self.current_game_time = self.game_start_time
        
        # 时间流逝速度（游戏中1秒 = 现实中多少秒）
        self.time_speed_multiplier = 60  # 游戏时间比现实时间快60倍
        
        # 上次更新的真实时间
        self.last_real_time = datetime.now()
        
        # 游戏日计数
        self.game_day = 1
        
        # 时间事件回调
        self.time_callbacks = []
    
    def update_time(self):
        """更新游戏时间"""
        current_real_time = datetime.now()
        real_time_passed = (current_real_time - self.last_real_time).total_seconds()
        
        # 计算游戏时间应该前进多少
        game_time_advance = real_time_passed * self.time_speed_multiplier
        
        # 更新游戏时间
        old_game_time = self.current_game_time
        self.current_game_time += timedelta(seconds=game_time_advance)
        
        # 检查是否跨天
        if old_game_time.day != self.current_game_time.day:
            self.game_day += 1
            self.trigger_new_day_events()
        
        # 更新记录的真实时间
        self.last_real_time = current_real_time
        
        # 触发时间事件
        self.trigger_time_events(old_game_time, self.current_game_time)
    
    def get_time_of_day(self):
        """获取当前时间段"""
        hour = self.current_game_time.hour
        
        if 5 <= hour < 7:
            return TimeOfDay.DAWN
        elif 7 <= hour < 11:
            return TimeOfDay.MORNING
        elif 11 <= hour < 13:
            return TimeOfDay.NOON
        elif 13 <= hour < 17:
            return TimeOfDay.AFTERNOON
        elif 17 <= hour < 19:
            return TimeOfDay.EVENING
        elif 19 <= hour < 23:
            return TimeOfDay.NIGHT
        else:
            return TimeOfDay.MIDNIGHT
    
    def get_formatted_time(self):
        """获取格式化的时间字符串"""
        return self.current_game_time.strftime("%H:%M")
    
    def get_formatted_date(self):
        """获取格式化的日期字符串"""
        return f"第{self.game_day}天"
    
    def get_full_datetime_string(self):
        """获取完整的日期时间字符串"""
        time_of_day = self.get_time_of_day().value
        return f"{self.get_formatted_date()} {self.get_formatted_time()} ({time_of_day})"
    
    def is_peak_hour(self):
        """判断是否为高峰期"""
        hour = self.current_game_time.hour
        # 早高峰：7-9点，午高峰：11-13点，晚高峰：17-19点
        return (7 <= hour <= 9) or (11 <= hour <= 13) or (17 <= hour <= 19)
    
    def is_late_night(self):
        """判断是否为深夜"""
        hour = self.current_game_time.hour
        return hour >= 22 or hour <= 5
    
    def advance_time(self, minutes):
        """手动推进时间（用于配送等活动）"""
        self.current_game_time += timedelta(minutes=minutes)
    
    def set_time_speed(self, multiplier):
        """设置时间流逝速度"""
        self.time_speed_multiplier = multiplier
    
    def add_time_callback(self, callback):
        """添加时间事件回调"""
        self.time_callbacks.append(callback)
    
    def trigger_time_events(self, old_time, new_time):
        """触发时间相关事件"""
        # 检查小时变化
        if old_time.hour != new_time.hour:
            for callback in self.time_callbacks:
                if hasattr(callback, 'on_hour_change'):
                    callback.on_hour_change(new_time.hour)
    
    def trigger_new_day_events(self):
        """触发新一天的事件"""
        for callback in self.time_callbacks:
            if hasattr(callback, 'on_new_day'):
                callback.on_new_day(self.game_day)
    
    def get_delivery_time_modifier(self):
        """根据时间段获取配送时间修正系数"""
        time_of_day = self.get_time_of_day()
        hour = self.current_game_time.hour
        
        # 不同时间段的配送时间修正
        modifiers = {
            TimeOfDay.DAWN: 0.8,      # 黎明时段路况好，送得快
            TimeOfDay.MORNING: 1.2,   # 上午高峰期，稍慢
            TimeOfDay.NOON: 1.5,      # 午餐高峰期，很慢
            TimeOfDay.AFTERNOON: 1.0, # 下午正常
            TimeOfDay.EVENING: 1.3,   # 晚餐高峰期，较慢
            TimeOfDay.NIGHT: 0.9,     # 夜晚路况好
            TimeOfDay.MIDNIGHT: 0.7   # 深夜路况最好
        }
        
        return modifiers.get(time_of_day, 1.0)