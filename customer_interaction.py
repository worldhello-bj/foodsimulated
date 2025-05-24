"""
客户互动系统
Customer Interaction System with LLM Integration
"""

import random
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
from game_core import CustomerType
from order_system import Order
from dataclasses import dataclass
class DialogueMode(Enum):
    OFFLINE = "离线模式"
    ONLINE = "在线模式"

class InteractionResult(Enum):
    SUCCESS = "成功"
    NEUTRAL = "中性"
    FAILURE = "失败"

@dataclass
class DialogueOption:
    """对话选项"""
    text: str
    impact: Dict[str, int]  # 影响：如 {"credit": -2, "tip_chance": 0.3}
    required_attributes: Dict[str, int] = None  # 需要的属性要求

@dataclass
class CustomerDialogue:
    """客户对话数据"""
    customer_type: CustomerType
    trigger_condition: str
    dialogue_options: List[DialogueOption]
    fallback_phrases: List[str]
    context: str = ""

class OfflineDialogueDatabase:
    """离线对话数据库"""
    
    def __init__(self):
        self.dialogues = self._initialize_dialogues()
    
    def _initialize_dialogues(self) -> Dict[CustomerType, List[CustomerDialogue]]:
        """初始化对话数据库"""
        return {
            CustomerType.PROGRAMMER_SHY: [
                CustomerDialogue(
                    customer_type=CustomerType.PROGRAMMER_SHY,
                    trigger_condition="正常送达",
                    dialogue_options=[
                        DialogueOption(
                            text="餐已放门口，您方便的时候取一下",
                            impact={"credit": 2, "tip_chance": 0.6}
                        ),
                        DialogueOption(
                            text="外卖到了！快来拿！",
                            impact={"credit": -1, "complaint_chance": 0.3}
                        )
                    ],
                    fallback_phrases=["谢谢", "辛苦了"],
                    context="程序员社恐型客户更喜欢不被打扰的配送方式"
                ),
                CustomerDialogue(
                    customer_type=CustomerType.PROGRAMMER_SHY,
                    trigger_condition="超时配送",
                    dialogue_options=[
                        DialogueOption(
                            text="不好意思来晚了，路上堵车",
                            impact={"credit": -1}
                        ),
                        DialogueOption(
                            text="餐放门口了，还热着呢",
                            impact={"credit": 1, "tip_chance": 0.3}
                        )
                    ],
                    fallback_phrases=["没关系", "下次注意时间"],
                    context="超时情况下程序员通常比较宽容"
                )
            ],
            
            CustomerType.RICH_IMPATIENT: [
                CustomerDialogue(
                    customer_type=CustomerType.RICH_IMPATIENT,
                    trigger_condition="催单",
                    dialogue_options=[
                        DialogueOption(
                            text="您好，我已经在路上了，马上到",
                            impact={"credit": 0}
                        ),
                        DialogueOption(
                            text="不好意思，我这边出了点状况",
                            impact={"credit": -3, "complaint_chance": 0.5}
                        ),
                        DialogueOption(
                            text="先生您好，我正在加急处理您的订单",
                            impact={"credit": 1},
                            required_attributes={"emotional_intelligence": 3}
                        )
                    ],
                    fallback_phrases=["你们效率真差", "下次还让我等这么久试试"],
                    context="催单暴发户型需要恭敬的态度"
                ),
                CustomerDialogue(
                    customer_type=CustomerType.RICH_IMPATIENT,
                    trigger_condition="准时送达",
                    dialogue_options=[
                        DialogueOption(
                            text="您的餐到了，请查收",
                            impact={"tip_chance": 0.8, "credit": 2}
                        ),
                        DialogueOption(
                            text="老板，您的外卖，还需要其他服务吗？",
                            impact={"tip_chance": 1.0, "credit": 3},
                            required_attributes={"emotional_intelligence": 4}
                        )
                    ],
                    fallback_phrases=["不错，准时到达", "这次效率可以"],
                    context="准时送达会获得丰厚小费"
                )
            ],
            
            CustomerType.DIFFICULT_ELDERLY: [
                CustomerDialogue(
                    customer_type=CustomerType.DIFFICULT_ELDERLY,
                    trigger_condition="正常配送",
                    dialogue_options=[
                        DialogueOption(
                            text="阿姨您好，您的外卖到了",
                            impact={"complaint_chance": -0.2, "credit": 2}
                        ),
                        DialogueOption(
                            text="您的餐到了",
                            impact={"complaint_chance": 0.1}
                        ),
                        DialogueOption(
                            text="奶奶，您的饭菜到了，趁热吃",
                            impact={"tip_chance": 0.4, "credit": 3},
                            required_attributes={"emotional_intelligence": 5}
                        )
                    ],
                    fallback_phrases=["你这孩子真有礼貌", "现在的年轻人还是不错的"],
                    context="称呼'阿姨'可以降低投诉率20%"
                )
            ],
            
            CustomerType.NORMAL: [
                CustomerDialogue(
                    customer_type=CustomerType.NORMAL,
                    trigger_condition="正常配送",
                    dialogue_options=[
                        DialogueOption(
                            text="您好，您的外卖到了",
                            impact={"credit": 1}
                        ),
                        DialogueOption(
                            text="外卖送到，请慢用",
                            impact={"credit": 1, "tip_chance": 0.2}
                        )
                    ],
                    fallback_phrases=["谢谢", "辛苦了"],
                    context="普通客户交互"
                )
            ],
            
            CustomerType.VIP: [
                CustomerDialogue(
                    customer_type=CustomerType.VIP,
                    trigger_condition="正常配送",
                    dialogue_options=[
                        DialogueOption(
                            text="您好，您的VIP专享外卖已送达",
                            impact={"credit": 2, "tip_chance": 0.6}
                        ),
                        DialogueOption(
                            text="尊敬的客户，您的餐食已送达，请享用",
                            impact={"credit": 3, "tip_chance": 0.8},
                            required_attributes={"emotional_intelligence": 3}
                        )
                    ],
                    fallback_phrases=["服务很好", "下次继续选择你们"],
                    context="VIP客户需要优质服务"
                )
            ]
        }
    
    def get_dialogue(self, customer_type: CustomerType, trigger: str) -> Optional[CustomerDialogue]:
        """获取对话数据"""
        if customer_type in self.dialogues:
            for dialogue in self.dialogues[customer_type]:
                if dialogue.trigger_condition == trigger:
                    return dialogue
        return None

class CustomerInteractionSystem:
    """客户互动系统"""
    
    def __init__(self, game_state, mode: DialogueMode = DialogueMode.OFFLINE):
        self.game_state = game_state
        self.mode = mode
        self.offline_db = OfflineDialogueDatabase()
        self.interaction_history = []
    
    def interact_with_customer(self, order: Order, trigger: str) -> Dict:
        """与客户互动"""
        if self.mode == DialogueMode.OFFLINE:
            return self._offline_interaction(order, trigger)
        else:
            return self._online_interaction(order, trigger)
    
    def _offline_interaction(self, order: Order, trigger: str) -> Dict:
        """离线模式互动"""
        dialogue = self.offline_db.get_dialogue(order.customer_type, trigger)
        
        if not dialogue:
            # 回退到默认对话
            return {
                'success': True,
                'customer_response': "好的，谢谢",
                'impact': {"credit": 0},
                'options_used': "默认回复"
            }
        
        # 过滤可用选项（检查属性要求）
        available_options = []
        for option in dialogue.dialogue_options:
            if self._check_attribute_requirements(option.required_attributes):
                available_options.append(option)
        
        if not available_options:
            available_options = dialogue.dialogue_options  # 如果没有可用选项，使用全部
        
        # 模拟选择（实际游戏中应该让玩家选择）
        chosen_option = random.choice(available_options)
        
        # 应用影响
        self._apply_interaction_impact(chosen_option.impact)
        
        # 生成客户回复
        customer_response = random.choice(dialogue.fallback_phrases)
        
        # 记录互动历史
        interaction_record = {
            'timestamp': self.game_state.current_time.isoformat(),
            'customer_type': order.customer_type.value,
            'trigger': trigger,
            'player_choice': chosen_option.text,
            'customer_response': customer_response,
            'impact': chosen_option.impact
        }
        self.interaction_history.append(interaction_record)
        
        return {
            'success': True,
            'customer_response': customer_response,
            'impact': chosen_option.impact,
            'options_used': chosen_option.text,
            'available_options': [opt.text for opt in available_options]
        }
    
    def _online_interaction(self, order: Order, trigger: str) -> Dict:
        """在线模式互动（模拟LLM调用）"""
        # 这里应该调用实际的LLM API
        # 为了演示，我们模拟一个智能回复
        
        prompt = self._generate_llm_prompt(order, trigger)
        
        # 模拟LLM响应（实际实现时应该调用真实的LLM API）
        simulated_response = self._simulate_llm_response(order, trigger)
        
        return simulated_response
    
    def _generate_llm_prompt(self, order: Order, trigger: str) -> str:
        """生成LLM提示词"""
        context = f"""
        你是一个外卖配送员，正在与客户互动。
        
        客户信息：
        - 类型：{order.customer_type.value}
        - 订单优先级：{order.priority.value}
        - 配送区域：{order.delivery_district.value}
        
        当前情况：{trigger}
        
        玩家属性：
        - 情商：{self.game_state.attributes.emotional_intelligence}
        - 经验等级：{self.game_state.attributes.level}
        
        请生成3个不同的回复选项，并预测客户可能的反应。
        每个选项应该包含不同的风险和收益。
        """
        
        return context
    
    def _simulate_llm_response(self, order: Order, trigger: str) -> Dict:
        """模拟LLM响应"""
        # 这是一个简化的模拟，实际实现时应该调用真实的LLM API
        
        responses = {
            CustomerType.PROGRAMMER_SHY: {
                "正常送达": [
                    {"text": "已放门口，请取餐", "impact": {"credit": 2, "tip_chance": 0.5}},
                    {"text": "外卖到了，请享用", "impact": {"credit": 1}},
                    {"text": "餐食送达，无需回复", "impact": {"credit": 3, "tip_chance": 0.7}}
                ]
            },
            CustomerType.RICH_IMPATIENT: {
                "催单": [
                    {"text": "抱歉延误，正在加急处理", "impact": {"credit": 0}},
                    {"text": "马上到达，请稍候", "impact": {"credit": -1}},
                    {"text": "尊敬的客户，我会尽快送达", "impact": {"credit": 2}}
                ]
            }
        }
        
        # 获取预定义回复或生成默认回复
        if order.customer_type in responses and trigger in responses[order.customer_type]:
            options = responses[order.customer_type][trigger]
            chosen = random.choice(options)
        else:
            chosen = {"text": "好的，了解", "impact": {"credit": 0}}
        
        self._apply_interaction_impact(chosen["impact"])
        
        return {
            'success': True,
            'customer_response': "智能回复生成成功",
            'impact': chosen["impact"],
            'options_used': chosen["text"],
            'llm_generated': True
        }
    
    def _check_attribute_requirements(self, requirements: Optional[Dict[str, int]]) -> bool:
        """检查属性要求"""
        if not requirements:
            return True
        
        for attr, min_value in requirements.items():
            if hasattr(self.game_state.attributes, attr):
                if getattr(self.game_state.attributes, attr) < min_value:
                    return False
            else:
                return False
        
        return True
    
    def _apply_interaction_impact(self, impact: Dict[str, int]):
        """应用互动影响"""
        for effect, value in impact.items():
            if effect == "credit":
                self.game_state.attributes.credit_score += value
            elif effect == "tip_chance":
                # 这个会在订单结算时使用
                pass
            elif effect == "complaint_chance":
                # 这个会在订单结算时使用
                pass
    
    def get_interaction_history(self, limit: int = 10) -> List[Dict]:
        """获取互动历史"""
        return self.interaction_history[-limit:]
    
    def analyze_customer_patterns(self) -> Dict:
        """分析客户互动模式"""
        if not self.interaction_history:
            return {"message": "暂无互动历史"}
        
        # 统计各类客户的互动成功率
        customer_stats = {}
        for record in self.interaction_history:
            customer_type = record['customer_type']
            if customer_type not in customer_stats:
                customer_stats[customer_type] = {'total': 0, 'positive_impact': 0}
            
            customer_stats[customer_type]['total'] += 1
            if record['impact'].get('credit', 0) > 0:
                customer_stats[customer_type]['positive_impact'] += 1
        
        # 计算成功率
        for customer_type in customer_stats:
            stats = customer_stats[customer_type]
            stats['success_rate'] = stats['positive_impact'] / stats['total'] if stats['total'] > 0 else 0
        
        return customer_stats