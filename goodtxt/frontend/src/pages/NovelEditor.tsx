import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Save, 
  Download,
  Settings,
  Eye,
  Edit,
  BookOpen,
  Users,
  Clock,
  TrendingUp,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Chapter {
  id: string;
  title: string;
  content: string;
  status: 'generating' | 'completed' | 'editing' | 'reviewing';
  wordCount: number;
  quality: number;
  aiAgent: string;
  progress: number;
}

const NovelEditor: React.FC = () => {
  const [activeTab, setActiveTab] = useState('editor');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedChapter, setSelectedChapter] = useState<string>('1');
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 项目配置状态
  const [novelConfig, setNovelConfig] = useState({
    title: '',
    genre: 'romance',
    length: 'medium',
    theme: '',
    target_audience: 'adult',
    description: ''
  });

  // 获取URL参数中的项目ID
  const projectId = new URLSearchParams(window.location.search).get('id');

  useEffect(() => {
    if (projectId) {
      loadProject();
    } else {
      // 没有项目ID时，显示创建新项目的界面
      setLoading(false);
    }
  }, [projectId]);

  const loadProject = async () => {
    if (!projectId) return;
    
    try {
      setLoading(true);
      // 这里会调用实际的API加载项目
      // const projectData = await projectAPI.getProject(projectId);
      // setProject(projectData);
      
      // 临时使用模拟数据
      setProject({
        id: projectId,
        title: '星际征途',
        genre: '科幻',
        status: 'draft',
        progress: 0,
        totalWords: 0,
        targetWords: 50000,
        aiAgents: ['协调者', '作者', '编辑', '研究者'],
        chapters: []
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载项目失败');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    try {
      setLoading(true);
      // 调用创建项目API
      // const response = await projectAPI.createProject(novelConfig);
      // setProject(response.project);
      
      // 临时使用模拟响应
      const newProject = {
        id: projectId,
        title: novelConfig.title || '新小说项目',
        genre: novelConfig.genre,
        status: 'created',
        progress: 0,
        totalWords: 0,
        targetWords: 50000,
        aiAgents: ['协调者', '作者', '编辑', '研究者'],
        chapters: []
      };
      setProject(newProject);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建项目失败');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!project) {
      setError('请先创建项目');
      return;
    }

    if (!novelConfig.title || !novelConfig.theme) {
      setError('请填写项目标题和主题');
      return;
    }

    try {
      setIsGenerating(true);
      setError(null);

      // 开始生成小说
      // const response = await projectAPI.startGeneration(project.id, 3);
      
      // 模拟生成过程
      console.log('开始生成小说...', {
        projectId: project.id,
        config: novelConfig
      });
      
      // 这里会启动真实的AI生成流程
      // 生成完成后会通过WebSocket推送更新
      alert('小说生成已开始！请在项目列表中查看进度。');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = () => {
    // 保存逻辑
    console.log('保存章节');
  };

  const handleExport = () => {
    // 导出逻辑
    console.log('导出项目');
  };

  const activeChapter = project.chapters.find(ch => ch.id === selectedChapter);

  return (
    <div className="space-y-6">
      {/* 项目头部信息 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{project.title}</h1>
          <div className="flex items-center space-x-4 mt-2">
            <Badge variant="secondary">{project.genre}</Badge>
            <span className="text-sm text-muted-foreground">
              {project.totalWords.toLocaleString()} / {project.targetWords.toLocaleString()} 字
            </span>
            <span className="text-sm text-muted-foreground">
              进度: {project.progress}%
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="mr-2 h-4 w-4" />
            设置
          </Button>
          <Button variant="outline" size="sm" onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" />
            保存
          </Button>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            导出
          </Button>
        </div>
      </div>

      {/* 进度条 */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>项目进度</span>
              <span>{project.progress}%</span>
            </div>
            <Progress value={project.progress} className="h-3" />
          </div>
        </CardContent>
      </Card>

      {/* 主要编辑区域 */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* 章节列表 */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5" />
              <span>章节列表</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {project.chapters.map((chapter) => (
              <div
                key={chapter.id}
                className={cn(
                  "p-3 rounded-lg border cursor-pointer transition-colors",
                  selectedChapter === chapter.id 
                    ? "border-primary bg-primary/5" 
                    : "hover:bg-accent"
                )}
                onClick={() => setSelectedChapter(chapter.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">{chapter.title}</h4>
                  <Badge 
                    variant={chapter.status === 'completed' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {chapter.status === 'completed' ? '已完成' :
                     chapter.status === 'generating' ? '生成中' : '草稿'}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{chapter.wordCount} 字</span>
                    <span>{chapter.quality}% 质量</span>
                  </div>
                  <Progress value={chapter.progress} className="h-1" />
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-muted-foreground">{chapter.aiAgent}</span>
                  <Button variant="ghost" size="sm" className="h-6 px-2">
                    <Edit className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full mt-4">
              + 添加新章节
            </Button>
          </CardContent>
        </Card>

        {/* 编辑器区域 */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{activeChapter?.title}</CardTitle>
              <div className="flex items-center space-x-2">
                <Button 
                  variant={isGenerating ? "destructive" : "default"}
                  onClick={handleGenerate}
                  disabled={activeChapter?.status === 'generating'}
                >
                  {isGenerating ? (
                    <>
                      <Pause className="mr-2 h-4 w-4" />
                      暂停
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      生成
                    </>
                  )}
                </Button>
                <Button variant="outline">
                  <RotateCcw className="mr-2 h-4 w-4" />
                  重生
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList>
                <TabsTrigger value="editor">
                  <Edit className="mr-2 h-4 w-4" />
                  编辑
                </TabsTrigger>
                <TabsTrigger value="preview">
                  <Eye className="mr-2 h-4 w-4" />
                  预览
                </TabsTrigger>
                <TabsTrigger value="analysis">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  分析
                </TabsTrigger>
              </TabsList>

              <TabsContent value="editor" className="mt-6">
                {activeChapter?.status === 'generating' ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="h-5 w-5 animate-spin" />
                      <span>AI正在生成内容...</span>
                    </div>
                    <Progress value={activeChapter.progress} className="h-2" />
                    <p className="text-sm text-muted-foreground">
                      当前章节进度: {activeChapter.progress}%
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="border rounded-lg p-4 min-h-96">
                      <div className="prose max-w-none">
                        <div dangerouslySetInnerHTML={{ 
                          __html: activeChapter?.content?.replace(/\n/g, '<br>') || '' 
                        }} />
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>共 {activeChapter?.wordCount} 字</span>
                      <span>质量评分: {activeChapter?.quality}%</span>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="preview" className="mt-6">
                <div className="border rounded-lg p-6">
                  <h2 className="text-xl font-bold mb-4">{activeChapter?.title}</h2>
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap">
                      {activeChapter?.content}
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="analysis" className="mt-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>内容分析</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>可读性</span>
                          <span>92%</span>
                        </div>
                        <Progress value={92} />
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>连贯性</span>
                          <span>88%</span>
                        </div>
                        <Progress value={88} />
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>创意性</span>
                          <span>85%</span>
                        </div>
                        <Progress value={85} />
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle>AI代理表现</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {project.aiAgents.map((agent, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Users className="h-4 w-4" />
                            <span className="text-sm">{agent}</span>
                          </div>
                          <Badge variant="outline">活跃</Badge>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NovelEditor;