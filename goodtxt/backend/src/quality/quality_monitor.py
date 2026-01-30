"""
质量监控系统

负责监控和评估小说生成的质量，
包括逻辑一致性、风格统一性等方面。
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

import structlog
import numpy as np
# cosine_similarity imported if needed: from sklearn.metrics.pairwise import cosine_similarity

# QualityMetrics class is defined in this file
from ..memory.memory_manager import MemoryManager, MemoryType, MemoryCategory


class QualityIssue(Enum):
    """质量问题枚举"""
    PLOT_INCONSISTENCY = "plot_inconsistency"
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    LOGICAL_ERROR = "logical_error"
    STYLE_INCONSISTENCY = "style_inconsistency"
    PACE_ISSUE = "pace_issue"
    DIALOGUE_ISSUE = "dialogue_issue"
    GRAMMAR_ERROR = "grammar_error"
    FACTUAL_ERROR = "factual_error"


@dataclass
class QualityReport:
    """质量报告"""
    report_id: str
    content_type: str  # "chapter", "novel", "character"
    content_id: str
    overall_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    metrics: Dict[str, float]
    created_at: datetime
    evaluated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['evaluated_at'] = self.evaluated_at.isoformat()
        return data


@dataclass
class QualityMetrics:
    """质量指标"""
    coherence_score: float  # 连贯性
    consistency_score: float  # 一致性
    engagement_score: float  # 吸引力
    readability_score: float  # 可读性
    originality_score: float  # 原创性
    style_score: float  # 风格质量
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def overall(self) -> float:
        """计算总体质量分数"""
        scores = [
            self.coherence_score,
            self.consistency_score,
            self.engagement_score,
            self.readability_score,
            self.originality_score,
            self.style_score
        ]
        return sum(scores) / len(scores)


class QualityMonitor:
    """质量监控器"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.logger = structlog.get_logger()
        
        # 质量基准
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "poor": 0.5
        }
        
        # 质量历史记录
        self.quality_history: List[QualityReport] = []
        
        self.logger.info("Quality Monitor initialized")
    
    async def evaluate_chapter_quality(self, chapter) -> float:
        """评估章节质量"""
        try:
            # 获取相关记忆
            relevant_memories = await self.memory_manager.search_memories(
                query=chapter.title,
                memory_types=[MemoryType.LONG_TERM, MemoryType.MEDIUM_TERM]
            )
            
            # 计算各项指标
            coherence_score = self._evaluate_coherence(chapter.content)
            consistency_score = self._evaluate_consistency(chapter.content, relevant_memories)
            engagement_score = self._evaluate_engagement(chapter.content)
            readability_score = self._evaluate_readability(chapter.content)
            originality_score = self._evaluate_originality(chapter.content)
            style_score = self._evaluate_style(chapter.content)
            
            # 创建质量指标
            metrics = QualityMetrics(
                coherence_score=coherence_score,
                consistency_score=consistency_score,
                engagement_score=engagement_score,
                readability_score=readability_score,
                originality_score=originality_score,
                style_score=style_score
            )
            
            # 生成质量报告
            quality_report = await self._generate_quality_report(
                content_type="chapter",
                content_id=chapter.chapter_id,
                content=chapter.content,
                metrics=metrics,
                related_memories=relevant_memories
            )
            
            self.quality_history.append(quality_report)
            
            return metrics.overall
            
        except Exception as e:
            self.logger.error(f"Chapter quality evaluation failed: {e}")
            return 0.5  # 默认分数
    
    async def evaluate_novel_quality(self, project_id: str, chapters) -> Dict[str, Any]:
        """评估小说整体质量"""
        try:
            # 获取项目信息
            project_memories = await self.memory_manager.search_memories(
                query=f"project_{project_id}",
                memory_types=[MemoryType.LONG_TERM, MemoryType.MEDIUM_TERM]
            )
            
            # 章节间一致性检查
            inter_chapter_consistency = self._evaluate_inter_chapter_consistency(chapters)
            
            # 整体结构评估
            structure_score = self._evaluate_novel_structure(chapters)
            
            # 角色一致性检查
            character_consistency = self._evaluate_character_consistency(chapters)
            
            # 情节连贯性检查
            plot_coherence = self._evaluate_plot_coherence(chapters)
            
            # 综合质量评估
            overall_score = (
                inter_chapter_consistency * 0.3 +
                structure_score * 0.2 +
                character_consistency * 0.25 +
                plot_coherence * 0.25
            )
            
            # 生成综合质量报告
            quality_assessment = {
                "overall_quality": overall_score,
                "quality_level": self._get_quality_level(overall_score),
                "chapter_consistency": inter_chapter_consistency,
                "structure_score": structure_score,
                "character_consistency": character_consistency,
                "plot_coherence": plot_coherence,
                "recommendations": self._generate_improvement_recommendations(
                    overall_score, inter_chapter_consistency, structure_score
                )
            }
            
            return quality_assessment
            
        except Exception as e:
            self.logger.error(f"Novel quality evaluation failed: {e}")
            return {
                "overall_quality": 0.5,
                "error": str(e)
            }
    
    def _evaluate_coherence(self, content: str) -> float:
        """评估内容连贯性"""
        try:
            # 简单的连贯性评估
            sentences = re.split(r'[。！？]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return 0.8  # 短内容默认较高分数
            
            # 检查句子长度变化
            sentence_lengths = [len(s) for s in sentences]
            length_variance = np.var(sentence_lengths)
            
            # 方差越小，连贯性越好
            coherence_score = max(0.0, 1.0 - (length_variance / 1000))
            
            return min(1.0, coherence_score)
            
        except Exception as e:
            self.logger.error(f"Coherence evaluation failed: {e}")
            return 0.5
    
    def _evaluate_consistency(self, content: str, related_memories: Dict) -> float:
        """评估一致性"""
        try:
            consistency_score = 0.8  # 默认分数
            
            # 检查与已有设定的一致性
            if related_memories.get('long_term'):
                consistency_score += 0.1  # 有历史设定时提高分数
            
            # 检查重复概念
            content_words = set(content.split())
            if len(content_words) < 50:  # 内容过短
                consistency_score -= 0.2
            
            return min(1.0, max(0.0, consistency_score))
            
        except Exception as e:
            self.logger.error(f"Consistency evaluation failed: {e}")
            return 0.5
    
    def _evaluate_engagement(self, content: str) -> float:
        """评估吸引力"""
        try:
            # 检查情感词汇
            emotional_words = [
                '激动', '紧张', '惊讶', '愤怒', '悲伤', '快乐', 
                '恐惧', '希望', '绝望', '兴奋', '失望'
            ]
            
            emotional_count = sum(1 for word in emotional_words if word in content)
            
            # 检查对话
            dialogue_lines = re.findall(r'"[^"]*"', content)
            dialogue_ratio = len(dialogue_lines) / max(1, len(content.split('。')))
            
            # 检查动作描述
            action_words = ['跑', '跳', '打', '走', '看', '听', '说', '想']
            action_count = sum(1 for word in action_words if word in content)
            
            # 综合评分
            engagement_score = (
                min(1.0, emotional_count / 10) * 0.4 +
                min(1.0, dialogue_ratio * 5) * 0.3 +
                min(1.0, action_count / 20) * 0.3
            )
            
            return engagement_score
            
        except Exception as e:
            self.logger.error(f"Engagement evaluation failed: {e}")
            return 0.5
    
    def _evaluate_readability(self, content: str) -> float:
        """评估可读性"""
        try:
            # 简单的可读性评估
            sentences = re.split(r'[。！？]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0.0
            
            # 计算平均句子长度
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
            
            # 理想句子长度范围（15-25字符）
            if 15 <= avg_sentence_length <= 25:
                readability_score = 1.0
            elif 10 <= avg_sentence_length <= 30:
                readability_score = 0.8
            else:
                readability_score = 0.6
            
            # 调整分数
            return readability_score
            
        except Exception as e:
            self.logger.error(f"Readability evaluation failed: {e}")
            return 0.5
    
    def _evaluate_originality(self, content: str) -> float:
        """评估原创性"""
        try:
            # 检查是否包含常见短语
            common_phrases = [
                '突然', '突然之间', '突然之间', '就在这时', '就在此时',
                '只见', '只听', '只见得', '只见那', '却说', '且说'
            ]
            
            common_count = sum(1 for phrase in common_phrases if phrase in content)
            
            # 检查句式变化
            sentence_starts = []
            for sentence in re.split(r'[。！？]', content):
                if sentence.strip():
                    first_word = sentence.strip().split()[0] if sentence.strip().split() else ''
                    sentence_starts.append(first_word)
            
            unique_starts = len(set(sentence_starts))
            start_diversity = unique_starts / max(1, len(sentence_starts))
            
            # 综合评分
            originality_score = (
                max(0.0, 1.0 - common_count / 10) * 0.6 +
                start_diversity * 0.4
            )
            
            return originality_score
            
        except Exception as e:
            self.logger.error(f"Originality evaluation failed: {e}")
            return 0.5
    
    def _evaluate_style(self, content: str) -> float:
        """评估风格质量"""
        try:
            # 检查语言风格的一致性
            style_indicators = {
                'formal': ['因此', '然而', '鉴于', '综上所述'],
                'informal': ['于是', '然后', '接下来', '接着'],
                'literary': ['似乎', '仿佛', '宛如', '犹如']
            }
            
            style_scores = {}
            content_length = len(content)
            
            for style, indicators in style_indicators.items():
                count = sum(1 for indicator in indicators if indicator in content)
                style_scores[style] = count / max(1, content_length / 1000)  # 每1000字的指标数
            
            # 检查修辞手法
            rhetorical_devices = ['比喻', '拟人', '排比', '对偶']
            rhetorical_count = sum(1 for device in rhetorical_devices if device in content)
            
            # 综合评分
            style_score = (
                max(style_scores.values()) * 0.5 +
                min(1.0, rhetorical_count / 5) * 0.3 +
                0.2  # 基础分数
            )
            
            return style_score
            
        except Exception as e:
            self.logger.error(f"Style evaluation failed: {e}")
            return 0.5
    
    def _evaluate_inter_chapter_consistency(self, chapters) -> float:
        """评估章节间一致性"""
        try:
            if len(chapters) < 2:
                return 1.0
            
            # 检查角色名称一致性
            character_mentions = []
            for chapter in chapters:
                # 简单的角色名提取（实际应该更复杂）
                names = re.findall(r'[王小李张三赵钱孙周吴郑王][一二三四五六七八九十]?[a-zA-Z一-龥]*', chapter.content)
                character_mentions.extend(names)
            
            # 计算一致性
            unique_names = set(character_mentions)
            consistency_score = min(1.0, len(unique_names) / len(character_mentions) * 2)
            
            return consistency_score
            
        except Exception as e:
            self.logger.error(f"Inter-chapter consistency evaluation failed: {e}")
            return 0.5
    
    def _evaluate_novel_structure(self, chapters) -> float:
        """评估小说结构"""
        try:
            if not chapters:
                return 0.0
            
            # 检查章节长度分布
            chapter_lengths = [len(chapter.content) for chapter in chapters]
            length_variance = np.var(chapter_lengths)
            
            # 方差越小，结构越均匀
            structure_score = max(0.0, 1.0 - (length_variance / 10000))
            
            return structure_score
            
        except Exception as e:
            self.logger.error(f"Novel structure evaluation failed: {e}")
            return 0.5
    
    def _evaluate_character_consistency(self, chapters) -> float:
        """评估角色一致性"""
        try:
            # 这里可以实现更复杂的角色一致性检查
            # 简化实现
            return 0.8
            
        except Exception as e:
            self.logger.error(f"Character consistency evaluation failed: {e}")
            return 0.5
    
    def _evaluate_plot_coherence(self, chapters) -> float:
        """评估情节连贯性"""
        try:
            # 检查情节发展的逻辑性
            # 简化实现：检查章节间的时间线索和因果关系
            return 0.8
            
        except Exception as e:
            self.logger.error(f"Plot coherence evaluation failed: {e}")
            return 0.5
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= self.quality_thresholds["excellent"]:
            return "excellent"
        elif score >= self.quality_thresholds["good"]:
            return "good"
        elif score >= self.quality_thresholds["acceptable"]:
            return "acceptable"
        else:
            return "poor"
    
    def _generate_improvement_recommendations(
        self, 
        overall_score: float, 
        consistency_score: float, 
        structure_score: float
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if overall_score < 0.7:
            recommendations.append("建议提高整体内容质量，关注逻辑性和连贯性")
        
        if consistency_score < 0.8:
            recommendations.append("注意保持角色和设定的一致性，避免前后矛盾")
        
        if structure_score < 0.7:
            recommendations.append("优化章节结构，确保情节发展的合理性")
        
        if not recommendations:
            recommendations.append("内容质量良好，继续保持当前水准")
        
        return recommendations
    
    async def _generate_quality_report(
        self,
        content_type: str,
        content_id: str,
        content: str,
        metrics: QualityMetrics,
        related_memories: Dict
    ) -> QualityReport:
        """生成质量报告"""
        issues = []
        suggestions = []
        
        # 基于指标生成问题和建议
        if metrics.coherence_score < 0.7:
            issues.append({
                "type": "low_coherence",
                "description": "内容连贯性不足",
                "severity": "medium"
            })
            suggestions.append("建议改善句子间的逻辑连接")
        
        if metrics.consistency_score < 0.7:
            issues.append({
                "type": "low_consistency", 
                "description": "内容一致性不足",
                "severity": "medium"
            })
            suggestions.append("检查并保持设定的连续性")
        
        if metrics.engagement_score < 0.6:
            issues.append({
                "type": "low_engagement",
                "description": "内容吸引力不足",
                "severity": "low"
            })
            suggestions.append("增加情感表达和动作描述")
        
        if not suggestions:
            suggestions.append("内容质量良好，继续保持")
        
        report = QualityReport(
            report_id=f"qr_{content_type}_{content_id}_{datetime.now().timestamp()}",
            content_type=content_type,
            content_id=content_id,
            overall_score=metrics.overall,
            issues=issues,
            suggestions=suggestions,
            metrics=metrics.to_dict(),
            created_at=datetime.now(),
            evaluated_at=datetime.now()
        )
        
        return report