import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  BookOpen, 
  Clock, 
  Users,
  BarChart3,
  Edit,
  Trash2,
  Archive,
  Download,
  Share
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { projectAPI } from '@/services/api';

interface Project {
  id: string;
  title: string;
  description?: string;
  genre: string;
  status: 'draft' | 'generating' | 'completed' | 'archived';
  progress: number;
  wordCount: number;
  targetWords: number;
  createdAt: Date;
  updatedAt: Date;
  aiAgents: string[];
  chapters: number;
  quality: number;
}

const ProjectManager: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterGenre, setFilterGenre] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('updatedAt');
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const genres = ['科幻', '言情', '悬疑', '武侠', '历史', '现代'];
  const statuses = [
    { value: 'all', label: '全部' },
    { value: 'draft', label: '草稿' },
    { value: 'generating', label: '生成中' },
    { value: 'completed', label: '已完成' },
    { value: 'archived', label: '已归档' }
  ];

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projectAPI.getProjects();
      
      // 转换API数据为前端格式
      const formattedProjects: Project[] = (response.projects || []).map((project: any) => ({
        id: project.project_id,
        title: project.title,
        description: project.description || '',
        genre: project.genre,
        status: project.status,
        progress: project.statistics?.progress_percentage || 0,
        wordCount: project.statistics?.total_words || 0,
        targetWords: 50000, // 默认目标字数
        createdAt: new Date(project.created_at),
        updatedAt: new Date(project.updated_at || project.created_at),
        aiAgents: ['协调者', '作者', '编辑'], // 默认代理
        chapters: project.statistics?.total_chapters || 0,
        quality: project.statistics?.average_quality || 0
      }));
      
      setProjects(formattedProjects);
    } catch (err) {
      console.error('加载项目失败:', err);
      setError('加载项目失败，请刷新页面重试');
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (project.description && project.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesGenre = filterGenre === 'all' || project.genre === filterGenre;
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus;
    
    return matchesSearch && matchesGenre && matchesStatus;
  });

  // 计算统计数据
  const stats = {
    total: projects.length,
    generating: projects.filter(p => p.status === 'generating').length,
    completed: projects.filter(p => p.status === 'completed').length,
    averageQuality: projects.length > 0 ? Math.round(projects.reduce((acc, p) => acc + p.quality, 0) / projects.length) : 0
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'generating': return 'bg-blue-100 text-blue-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'archived': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'generating': return '生成中';
      case 'draft': return '草稿';
      case 'archived': return '已归档';
      default: return '未知';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">项目管理</h1>
          <p className="text-muted-foreground">
            管理您的小说项目，跟踪进度和质量
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          新建项目
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总项目</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">
              全部项目数量
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">生成中</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.generating}</div>
            <p className="text-xs text-muted-foreground">
              正在积极生成
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已完成</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completed}</div>
            <p className="text-xs text-muted-foreground">
              可发布版本
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均质量</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageQuality}%</div>
            <p className="text-xs text-muted-foreground">
              整体表现
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索项目..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={filterGenre}
              onChange={(e) => setFilterGenre(e.target.value)}
              className="px-3 py-2 border rounded-md bg-background"
            >
              <option value="all">全部类型</option>
              {genres.map(genre => (
                <option key={genre} value={genre}>{genre}</option>
              ))}
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border rounded-md bg-background"
            >
              {statuses.map(status => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              更多筛选
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 加载状态 */}
      {loading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded" />
                <div className="h-3 bg-gray-200 rounded w-2/3" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                  <div className="h-3 bg-gray-200 rounded w-1/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={loadProjects}>重新加载</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 项目列表 */}
      {!loading && !error && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{project.title}</CardTitle>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {project.description || '暂无描述'}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* 项目元信息 */}
                <div className="flex items-center justify-between">
                  <Badge variant="outline">{project.genre}</Badge>
                  <Badge className={getStatusColor(project.status)}>
                    {getStatusLabel(project.status)}
                  </Badge>
                </div>

                {/* 进度条 */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>进度</span>
                    <span>{project.progress}%</span>
                  </div>
                  <Progress value={project.progress} />
                </div>

                {/* 统计信息 */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">字数</p>
                    <p className="font-medium">
                      {project.wordCount.toLocaleString()} / {project.targetWords.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">章节</p>
                    <p className="font-medium">{project.chapters}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">质量</p>
                    <p className="font-medium">{project.quality}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">AI代理</p>
                    <p className="font-medium">{project.aiAgents.length}</p>
                  </div>
                </div>

                {/* 更新时间 */}
                <div className="text-xs text-muted-foreground">
                  最后更新: {project.updatedAt.toLocaleDateString()}
                </div>

                {/* 操作按钮 */}
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => window.location.href = `/editor?id=${project.id}`}
                  >
                    <Edit className="mr-2 h-3 w-3" />
                    编辑
                  </Button>
                  {project.status === 'completed' && (
                    <Button variant="outline" size="sm">
                      <Download className="h-3 w-3" />
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    <Share className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Archive className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && !error && filteredProjects.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">
              {projects.length === 0 ? '暂无项目' : '未找到项目'}
            </h3>
            <p className="text-muted-foreground text-center mb-4">
              {projects.length === 0 
                ? '您还没有创建任何项目，立即开始创作吧！'
                : (searchTerm || filterGenre !== 'all' || filterStatus !== 'all'
                  ? '尝试调整搜索条件或筛选器'
                  : '没有符合条件的项目')}
            </p>
            <Button onClick={() => window.location.href = '/editor'}>
              <Plus className="mr-2 h-4 w-4" />
              创建新项目
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProjectManager;