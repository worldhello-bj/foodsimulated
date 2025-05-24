"""
技能成长系统
Skill Development System
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CourseType(Enum):
    FIRST_AID = "急救常识"
    COMMUNICATION = "沟通心理学"
    TRAFFIC_SAFETY = "交通安全"
    CUSTOMER_SERVICE = "客户服务"
    FINANCIAL_MANAGEMENT = "理财规划"
    ENGLISH = "英语口语"

class ExamDifficulty(Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"

class EducationLevel(Enum):
    HIGH_SCHOOL = "高中"
    COLLEGE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士"

@dataclass
class Course:
    """课程数据"""
    course_type: CourseType
    name: str
    duration_hours: int
    cost: float
    difficulty: ExamDifficulty
    skill_bonuses: Dict[str, int]  # 技能加成
    unlock_requirements: Dict[str, int]  # 解锁要求
    description: str

@dataclass
class SkillProgress:
    """技能进度"""
    direction_sense: int = 1
    emotional_intelligence: int = 1
    education_level: int = 1
    first_aid: int = 0
    communication: int = 0
    traffic_safety: int = 0
    customer_service: int = 0
    financial_management: int = 0
    language_skills: int = 0

@dataclass
class StudySession:
    """学习记录"""
    course_type: CourseType
    start_time: datetime
    duration_minutes: int
    effectiveness: float  # 学习效果 0.0-1.0
    experience_gained: int
    cost: float

class NightSchool:
    """夜校系统"""
    
    def __init__(self):
        self.courses = self._initialize_courses()
        self.study_schedule = []
        self.graduation_requirements = {
            EducationLevel.HIGH_SCHOOL: {"total_hours": 200, "min_courses": 3},
            EducationLevel.COLLEGE: {"total_hours": 500, "min_courses": 6},
            EducationLevel.BACHELOR: {"total_hours": 1000, "min_courses": 10},
            EducationLevel.MASTER: {"total_hours": 1500, "min_courses": 15}
        }
    
    def _initialize_courses(self) -> Dict[CourseType, Course]:
        """初始化课程"""
        courses = {
            CourseType.FIRST_AID: Course(
                course_type=CourseType.FIRST_AID,
                name="急救常识培训",
                duration_hours=20,
                cost=200.0,
                difficulty=ExamDifficulty.EASY,
                skill_bonuses={"first_aid": 3, "customer_service": 1},
                unlock_requirements={},
                description="学习基础急救知识，降低医院单纠纷率"
            ),
            CourseType.COMMUNICATION: Course(
                course_type=CourseType.COMMUNICATION,
                name="沟通心理学",
                duration_hours=30,
                cost=400.0,
                difficulty=ExamDifficulty.MEDIUM,
                skill_bonuses={"emotional_intelligence": 2, "communication": 3},
                unlock_requirements={},
                description="提升情商和沟通技巧，减少客户投诉"
            ),
            CourseType.TRAFFIC_SAFETY: Course(
                course_type=CourseType.TRAFFIC_SAFETY,
                name="交通安全知识",
                duration_hours=15,
                cost=150.0,
                difficulty=ExamDifficulty.EASY,
                skill_bonuses={"traffic_safety": 3, "direction_sense": 1},
                unlock_requirements={},
                description="提升交通安全意识，降低事故风险"
            ),
            CourseType.CUSTOMER_SERVICE: Course(
                course_type=CourseType.CUSTOMER_SERVICE,
                name="客户服务技巧",
                duration_hours=25,
                cost=300.0,
                difficulty=ExamDifficulty.MEDIUM,
                skill_bonuses={"customer_service": 3, "emotional_intelligence": 1},
                unlock_requirements={"communication": 2},
                description="专业客服技能，提升客户满意度"
            ),
            CourseType.FINANCIAL_MANAGEMENT: Course(
                course_type=CourseType.FINANCIAL_MANAGEMENT,
                name="个人理财规划",
                duration_hours=40,
                cost=600.0,
                difficulty=ExamDifficulty.HARD,
                skill_bonuses={"financial_management": 4, "education_level": 1},
                unlock_requirements={"education_level": 3},
                description="理财投资知识，改善财务状况"
            ),
            CourseType.ENGLISH: Course(
                course_type=CourseType.ENGLISH,
                name="英语口语提升",
                duration_hours=50,
                cost=800.0,
                difficulty=ExamDifficulty.HARD,
                skill_bonuses={"language_skills": 4, "customer_service": 2},
                unlock_requirements={"education_level": 2},
                description="提升英语水平，接待外国客户"
            )
        }
        return courses
    
    def enroll_course(self, course_type: CourseType, game_state) -> Dict:
        """报名课程"""
        course = self.courses[course_type]
        
        # 检查前置要求
        if not self._check_requirements(course.unlock_requirements, game_state):
            return {
                'success': False,
                'message': '不满足课程前置要求',
                'requirements': course.unlock_requirements
            }
        
        # 检查资金
        if game_state.finances.delivery_coins < course.cost:
            return {
                'success': False,
                'message': '资金不足',
                'required': course.cost,
                'available': game_state.finances.delivery_coins
            }
        
        # 扣除费用
        game_state.finances.delivery_coins -= course.cost
        
        return {
            'success': True,
            'message': f'成功报名{course.name}',
            'course': course
        }
    
    def study_session(self, course_type: CourseType, duration_minutes: int, game_state) -> Dict:
        """学习会话"""
        if duration_minutes > 180:  # 最多3小时
            duration_minutes = 180
        
        # 计算学习效果
        effectiveness = self._calculate_study_effectiveness(duration_minutes, game_state)
        
        # 经验获得
        base_exp = duration_minutes // 10  # 每10分钟1点经验
        experience_gained = int(base_exp * effectiveness)
        
        # 消耗体力
        stamina_cost = duration_minutes // 5
        game_state.attributes.stamina = max(0, game_state.attributes.stamina - stamina_cost)
        
        # 记录学习
        session = StudySession(
            course_type=course_type,
            start_time=datetime.now(),
            duration_minutes=duration_minutes,
            effectiveness=effectiveness,
            experience_gained=experience_gained,
            cost=0  # 已经在报名时支付
        )
        
        self.study_schedule.append(session)
        
        return {
            'effectiveness': effectiveness,
            'experience_gained': experience_gained,
            'stamina_cost': stamina_cost,
            'total_study_time': sum(s.duration_minutes for s in self.study_schedule if s.course_type == course_type)
        }
    
    def take_exam(self, course_type: CourseType, game_state) -> Dict:
        """参加考试"""
        course = self.courses[course_type]
        
        # 计算学习时间
        total_study_time = sum(
            s.duration_minutes for s in self.study_schedule 
            if s.course_type == course_type
        )
        
        required_time = course.duration_hours * 60
        
        if total_study_time < required_time:
            return {
                'success': False,
                'message': '学习时间不足',
                'studied': total_study_time,
                'required': required_time
            }
        
        # 计算通过概率
        pass_probability = self._calculate_pass_probability(course_type, game_state)
        
        # 考试结果
        passed = random.random() < pass_probability
        
        if passed:
            # 应用技能加成
            self._apply_skill_bonuses(course.skill_bonuses, game_state)
            
            return {
                'success': True,
                'passed': True,
                'message': f'恭喜通过{course.name}考试！',
                'skill_bonuses': course.skill_bonuses
            }
        else:
            return {
                'success': True,
                'passed': False,
                'message': f'{course.name}考试未通过，需要继续学习',
                'pass_probability': pass_probability
            }
    
    def _check_requirements(self, requirements: Dict[str, int], game_state) -> bool:
        """检查前置要求"""
        for skill, min_level in requirements.items():
            if hasattr(game_state.attributes, skill):
                if getattr(game_state.attributes, skill) < min_level:
                    return False
        return True
    
    def _calculate_study_effectiveness(self, duration_minutes: int, game_state) -> float:
        """计算学习效果"""
        base_effectiveness = 0.7
        
        # 体力影响
        stamina_factor = game_state.attributes.stamina / 100
        
        # 时间影响（太长会疲劳）
        if duration_minutes > 120:
            time_penalty = (duration_minutes - 120) * 0.005
        else:
            time_penalty = 0
        
        # 教育等级影响
        education_bonus = game_state.attributes.education_level * 0.05
        
        effectiveness = base_effectiveness * stamina_factor + education_bonus - time_penalty
        
        return max(0.1, min(1.0, effectiveness))
    
    def _calculate_pass_probability(self, course_type: CourseType, game_state) -> float:
        """计算考试通过概率"""
        course = self.courses[course_type]
        
        # 基础通过率
        base_rates = {
            ExamDifficulty.EASY: 0.8,
            ExamDifficulty.MEDIUM: 0.6,
            ExamDifficulty.HARD: 0.4
        }
        
        base_rate = base_rates[course.difficulty]
        
        # 学习质量加成
        study_sessions = [s for s in self.study_schedule if s.course_type == course_type]
        avg_effectiveness = sum(s.effectiveness for s in study_sessions) / len(study_sessions) if study_sessions else 0.5
        
        # 相关技能加成
        skill_bonus = 0
        for skill in course.skill_bonuses.keys():
            if hasattr(game_state.attributes, skill):
                skill_bonus += getattr(game_state.attributes, skill) * 0.02
        
        probability = base_rate * avg_effectiveness + skill_bonus
        
        return max(0.1, min(0.95, probability))
    
    def _apply_skill_bonuses(self, bonuses: Dict[str, int], game_state):
        """应用技能加成"""
        for skill, bonus in bonuses.items():
            if hasattr(game_state.attributes, skill):
                current_value = getattr(game_state.attributes, skill)
                setattr(game_state.attributes, skill, current_value + bonus)

class CareerTransition:
    """职业转换系统"""
    
    def __init__(self):
        self.available_careers = {
            "公务员": {
                "requirements": {"education_level": 5, "communication": 3},
                "exam_difficulty": ExamDifficulty.HARD,
                "benefits": {"stable_income": 8000, "social_status": "high"}
            },
            "企业管理": {
                "requirements": {"education_level": 4, "financial_management": 3},
                "exam_difficulty": ExamDifficulty.MEDIUM,
                "benefits": {"variable_income": (6000, 15000), "growth_potential": "high"}
            },
            "客服主管": {
                "requirements": {"customer_service": 4, "emotional_intelligence": 3},
                "exam_difficulty": ExamDifficulty.EASY,
                "benefits": {"stable_income": 5000, "work_environment": "good"}
            },
            "培训师": {
                "requirements": {"communication": 4, "education_level": 3},
                "exam_difficulty": ExamDifficulty.MEDIUM,
                "benefits": {"hourly_rate": 200, "flexible_schedule": True}
            }
        }
    
    def check_eligibility(self, career: str, game_state) -> Dict:
        """检查职业资格"""
        if career not in self.available_careers:
            return {'eligible': False, 'message': '职业不存在'}
        
        requirements = self.available_careers[career]["requirements"]
        
        for skill, min_level in requirements.items():
            if hasattr(game_state.attributes, skill):
                if getattr(game_state.attributes, skill) < min_level:
                    return {
                        'eligible': False,
                        'message': f'{skill}等级不足，需要{min_level}级',
                        'current_level': getattr(game_state.attributes, skill)
                    }
        
        return {'eligible': True, 'message': f'符合{career}职业要求'}
    
    def attempt_transition(self, career: str, game_state) -> Dict:
        """尝试职业转换"""
        eligibility = self.check_eligibility(career, game_state)
        
        if not eligibility['eligible']:
            return eligibility
        
        career_info = self.available_careers[career]
        difficulty = career_info["exam_difficulty"]
        
        # 计算成功概率
        success_rates = {
            ExamDifficulty.EASY: 0.8,
            ExamDifficulty.MEDIUM: 0.6,
            ExamDifficulty.HARD: 0.4
        }
        
        success_rate = success_rates[difficulty]
        
        # 根据技能水平调整
        skill_bonus = sum(
            getattr(game_state.attributes, skill, 0) * 0.05 
            for skill in career_info["requirements"].keys()
        )
        
        final_success_rate = min(0.9, success_rate + skill_bonus)
        
        if random.random() < final_success_rate:
            return {
                'success': True,
                'career': career,
                'benefits': career_info["benefits"],
                'message': f'恭喜成功转职为{career}！'
            }
        else:
            return {
                'success': False,
                'message': f'{career}转职失败，继续提升技能后再试',
                'success_rate': final_success_rate
            }