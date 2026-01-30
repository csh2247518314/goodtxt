"""
示例API调用

展示如何使用多AI协同小说生成系统的API接口
"""

import requests
import json
from typing import Dict, Any, Optional

# API基础URL
BASE_URL = "http://localhost:8000"


class NovelGeneratorAPI:
    """小说生成器API客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def create_project(
        self,
        title: str,
        genre: str,
        length: str,
        theme: str,
        target_audience: str,
        language: str = "中文"
    ) -> Dict[str, Any]:
        """创建小说项目"""
        data = {
            "title": title,
            "genre": genre,
            "length": length,
            "theme": theme,
            "target_audience": target_audience,
            "language": language
        }
        
        response = self.session.post(f"{self.base_url}/projects", json=data)
        response.raise_for_status()
        return response.json()
    
    def start_generation(
        self,
        project_id: str,
        chapter_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """开始小说生成"""
        params = {}
        if chapter_count:
            params["chapter_count"] = chapter_count
        
        response = self.session.post(
            f"{self.base_url}/projects/{project_id}/generate",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """获取项目状态"""
        response = self.session.get(f"{self.base_url}/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    
    def get_project_chapters(self, project_id: str) -> Dict[str, Any]:
        """获取项目章节"""
        response = self.session.get(f"{self.base_url}/projects/{project_id}/chapters")
        response.raise_for_status()
        return response.json()
    
    def get_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """获取单个章节"""
        response = self.session.get(f"{self.base_url}/chapters/{chapter_id}")
        response.raise_for_status()
        return response.json()
    
    def evaluate_chapter_quality(self, chapter_id: str) -> Dict[str, Any]:
        """评估章节质量"""
        response = self.session.post(f"{self.base_url}/chapters/{chapter_id}/quality")
        response.raise_for_status()
        return response.json()
    
    def export_novel(self, project_id: str, format: str = "txt") -> Dict[str, Any]:
        """导出小说"""
        response = self.session.get(
            f"{self.base_url}/projects/{project_id}/export",
            params={"format": format}
        )
        response.raise_for_status()
        return response.json()
    
    def search_memory(
        self,
        query: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """搜索记忆"""
        params = {"query": query}
        if category:
            params["category"] = category
        
        response = self.session.get(
            f"{self.base_url}/memory/search",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        response = self.session.get(f"{self.base_url}/system/status")
        response.raise_for_status()
        return response.json()
    
    def get_quality_history(self, limit: int = 50) -> Dict[str, Any]:
        """获取质量历史"""
        response = self.session.get(
            f"{self.base_url}/quality/history",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()


def example_basic_workflow():
    """基本工作流示例"""
    print("=== 基本工作流示例 ===")
    
    # 创建API客户端
    api = NovelGeneratorAPI()
    
    try:
        # 1. 健康检查
        print("1. 检查系统健康状态...")
        health = api.health_check()
        print(f"系统状态: {health['status']}")
        
        # 2. 创建小说项目
        print("\n2. 创建小说项目...")
        project_data = {
            "title": "魔法学院的神秘事件",
            "genre": "fantasy",
            "length": "medium",
            "theme": "友谊、成长与正义",
            "target_audience": "青少年"
        }
        
        project_result = api.create_project(**project_data)
        project_id = project_result["project_id"]
        print(f"项目创建成功，ID: {project_id}")
        
        # 3. 开始生成
        print("\n3. 开始小说生成...")
        generation_result = api.start_generation(project_id, chapter_count=5)
        print(f"生成任务启动: {generation_result['message']}")
        
        # 4. 监控进度
        print("\n4. 监控生成进度...")
        max_attempts = 20
        for i in range(max_attempts):
            status = api.get_project_status(project_id)
            print(f"尝试 {i+1}/{max_attempts}: 项目状态 = {status['project']['status']}")
            
            if status['project']['status'] == 'completed':
                print("✅ 小说生成完成！")
                break
            
            if i < max_attempts - 1:
                print("等待30秒后继续检查...")
                import time
                time.sleep(30)
        
        # 5. 查看生成结果
        print("\n5. 查看生成结果...")
        chapters = api.get_project_chapters(project_id)
        print(f"生成章节数: {chapters['total_chapters']}")
        
        # 6. 导出小说
        print("\n6. 导出小说...")
        export_result = api.export_novel(project_id)
        print(f"导出路径: {export_result['export_path']}")
        
        print("\n✅ 基本工作流完成！")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API调用错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


def example_quality_evaluation():
    """质量评估示例"""
    print("\n=== 质量评估示例 ===")
    
    api = NovelGeneratorAPI()
    
    try:
        # 获取质量历史
        print("获取质量评估历史...")
        history = api.get_quality_history(limit=10)
        print(f"历史记录数: {history['total_reports']}")
        
        if history['history']:
            latest = history['history'][0]
            print(f"最新评估:")
            print(f"  - 内容类型: {latest['content_type']}")
            print(f"  - 总体分数: {latest['overall_score']:.2f}")
            print(f"  - 问题数量: {len(latest['issues'])}")
            print(f"  - 建议数量: {len(latest['suggestions'])}")
        
        print("✅ 质量评估示例完成！")
        
    except Exception as e:
        print(f"❌ 质量评估示例错误: {e}")


def example_memory_search():
    """记忆搜索示例"""
    print("\n=== 记忆搜索示例 ===")
    
    api = NovelGeneratorAPI()
    
    try:
        # 搜索特定主题
        print("搜索世界观相关记忆...")
        worldview_memories = api.search_memory("世界观", category="worldview")
        print(f"世界观记忆结果: {len(worldview_memories.get('results', {}).get('long_term', []))}")
        
        # 搜索角色相关
        print("\n搜索角色相关记忆...")
        character_memories = api.search_memory("角色", category="character")
        print(f"角色记忆结果: {len(character_memories.get('results', {}).get('long_term', []))}")
        
        # 通用搜索
        print("\n执行通用记忆搜索...")
        general_search = api.search_memory("魔法学院")
        print(f"通用搜索结果:")
        for memory_type, memories in general_search.get('results', {}).items():
            print(f"  - {memory_type}: {len(memories)} 条记录")
        
        print("✅ 记忆搜索示例完成！")
        
    except Exception as e:
        print(f"❌ 记忆搜索示例错误: {e}")


def example_system_monitoring():
    """系统监控示例"""
    print("\n=== 系统监控示例 ===")
    
    api = NovelGeneratorAPI()
    
    try:
        # 获取系统状态
        print("获取系统状态...")
        status = api.get_system_status()
        
        print(f"系统状态: {status['system']['status']}")
        print(f"活跃项目: {status['projects']['active']}")
        print(f"已完成项目: {status['projects']['completed']}")
        
        # 框架状态
        framework = status.get('framework', {})
        print(f"\n框架状态:")
        print(f"  - 状态: {framework.get('status', 'unknown')}")
        
        # 通信状态
        comm = status.get('communication', {})
        print(f"\n通信状态:")
        print(f"  - 发送消息数: {comm.get('messages_sent', 0)}")
        print(f"  - 接收消息数: {comm.get('messages_received', 0)}")
        print(f"  - 错误数: {comm.get('errors', 0)}")
        
        # 调度器状态
        scheduler = status.get('scheduler', {})
        print(f"\n调度器状态:")
        print(f"  - 总任务数: {scheduler.get('total_tasks', 0)}")
        print(f"  - 运行任务: {scheduler.get('running_tasks', 0)}")
        print(f"  - 完成任务: {scheduler.get('completed_tasks', 0)}")
        
        print("✅ 系统监控示例完成！")
        
    except Exception as e:
        print(f"❌ 系统监控示例错误: {e}")


def main():
    """主函数"""
    print("多AI协同小说生成系统 - API示例")
    print("=" * 50)
    
    # 运行示例
    try:
        example_basic_workflow()
        example_quality_evaluation()
        example_memory_search()
        example_system_monitoring()
        
        print("\n🎉 所有示例运行完成！")
        
    except KeyboardInterrupt:
        print("\n\n用户中断了示例运行")
    except Exception as e:
        print(f"\n❌ 示例运行错误: {e}")


if __name__ == "__main__":
    main()