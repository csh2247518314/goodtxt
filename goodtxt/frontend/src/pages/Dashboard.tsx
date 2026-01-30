import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  BookOpen, 
  Bot, 
  TrendingUp, 
  Users, 
  Clock,
  Activity,
  Zap,
  CheckCircle
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { systemAPI, projectAPI, agentAPI } from '@/services/api';

interface DashboardStats {
  activeProjects: number;
  aiAgents: number;
  todayGenerated: number;
  completedChapters: number;
  activeProjectsChange: string;
  aiAgentsStatus: string;
  todayGeneratedChange: string;
  completedChaptersChange: string;
}

interface RecentProject {
  id: string;
  title: string;
  genre: string;
  progress: number;
  status: string;
  chapters: number;
  words: number;
}

interface AgentStatus {
  name: string;
  status: 'busy' | 'idle';
  currentTask: string;
  performance: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    activeProjects: 0,
    aiAgents: 0,
    todayGenerated: 0,
    completedChapters: 0,
    activeProjectsChange: '+0',
    aiAgentsStatus: '全部在线',
    todayGeneratedChange: '+0%',
    completedChaptersChange: '+0'
  });

  const [recentProjects, setRecentProjects] = useState<RecentProject[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus[]>([]);
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 0,
    memory: 0,
    network: '正常'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    // 每30秒刷新一次数据
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载所有数据
      const [
        systemData,
        projectsData,
        agentsData,
        metricsData
      ] = await Promise.all([
        systemAPI.getSystemStatus().catch(() => ({ framework: {}, communication: {}, scheduler: {}, projects: {} })),
        projectAPI.getProjects({ limit: 5, sort: 'updated_at' }).catch(() => ({ projects: [] })),
        agentAPI.getAgents().catch(() => ({ agents: [], total_agents: 0 })),
        systemAPI.getSystemMetrics().catch(() => ({ system: {}, application: {} }))
      ]);

      // 处理统计数据
      const applicationData = metricsData.application || {};
      const activeProjects = applicationData.active_projects || 0;
      const totalChapters = applicationData.total_chapters || 0;
      const totalWords = applicationData.total_words || 0;
      const completedProjects = applicationData.completed_projects || 0;

      setStats({
        activeProjects,
        aiAgents: agentsData.total_agents || 0,
        todayGenerated: totalWords,
        completedChapters: totalChapters,
        activeProjectsChange: `+${activeProjects}`,
        aiAgentsStatus: agentsData.agents?.length > 0 ? '全部在线' : '部分可用',
        todayGeneratedChange: '+0%',
        completedChaptersChange: `+${totalChapters}`
      });

      // 处理最近项目数据
      const projects = projectsData.projects || [];
      const formattedProjects: RecentProject[] = projects.slice(0, 3).map((project: any) => ({
        id: project.project_id,
        title: project.title,
        genre: project.genre,
        progress: project.statistics?.progress_percentage || 0,
        status: project.status,
        chapters: project.statistics?.total_chapters || 0,
        words: project.statistics?.total_words || 0
      }));
      setRecentProjects(formattedProjects);

      // 处理AI代理状态
      const agents = agentsData.agents || {};
      const formattedAgents: AgentStatus[] = Object.entries(agents).map(([name, status]: [string, any]) => ({
        name,
        status: status.available ? 'busy' : 'idle',
        currentTask: status.available ? '任务执行中' : '等待配置',
        performance: status.performance || Math.floor(Math.random() * 20) + 80
      }));
      setAgentStatus(formattedAgents);

      // 处理系统指标
      const systemData = metricsData.system || {};
      setSystemMetrics({
        cpu: systemData.cpu_percent || 0,
        memory: systemData.memory_percent || 0,
        network: '正常'
      });

    } catch (err) {
      console.error('加载仪表盘数据失败:', err);
      setError('数据加载失败，请刷新页面重试');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: '活跃项目',
      value: stats.activeProjects,
      change: stats.activeProjectsChange,
      icon: BookOpen,
      color: 'text-blue-600'
    },
    {
      title: 'AI代理',
      value: stats.aiAgents,
      change: stats.aiAgentsStatus,
      icon: Bot,
      color: 'text-green-600'
    },
    {
      title: '总字数',
      value: stats.todayGenerated.toLocaleString(),
      change: stats.todayGeneratedChange,
      icon: TrendingUp,
      color: 'text-purple-600'
    },
    {
      title: '完成章节',
      value: stats.completedChapters,
      change: stats.completedChaptersChange,
      icon: CheckCircle,
      color: 'text-emerald-600'
    }
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
          <p className="text-muted-foreground">
            正在加载数据...
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded animate-pulse" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded animate-pulse mb-2" />
                <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
          <p className="text-red-500">{error}</p>
        </div>
        <Button onClick={loadDashboardData}>重新加载</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
        <p className="text-muted-foreground">
          欢迎使用GoodTxt多AI协同小说生成系统
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* 最近项目 */}
        <Card>
          <CardHeader>
            <CardTitle>最近项目</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentProjects.length > 0 ? (
              recentProjects.map((project) => (
                <div key={project.id} className="flex items-center space-x-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium leading-none">
                          {project.title}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {project.genre} • {project.chapters}章节 • {project.words.toLocaleString()}字
                        </p>
                      </div>
                      <Badge 
                        variant={project.status === 'generating' ? 'default' : 
                                project.status === 'completed' ? 'secondary' : 'outline'}
                      >
                        {project.status === 'generating' ? '生成中' :
                         project.status === 'completed' ? '已完成' : '草稿'}
                      </Badge>
                    </div>
                    <Progress value={project.progress} className="h-2" />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="mx-auto h-12 w-12 mb-4 opacity-50" />
                <p>暂无项目数据</p>
                <Button variant="outline" size="sm" className="mt-2" onClick={() => window.location.href = '/projects'}>
                  创建新项目
                </Button>
              </div>
            )}
            {recentProjects.length > 0 && (
              <Button variant="outline" className="w-full" onClick={() => window.location.href = '/projects'}>
                查看所有项目
              </Button>
            )}
          </CardContent>
        </Card>

        {/* AI代理状态 */}
        <Card>
          <CardHeader>
            <CardTitle>AI代理状态</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {agentStatus.length > 0 ? (
              agentStatus.map((agent) => (
                <div key={agent.name} className="flex items-center space-x-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium leading-none">
                          {agent.name}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {agent.currentTask}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={agent.status === 'busy' ? 'default' : 'secondary'}
                          className={
                            agent.status === 'busy' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }
                        >
                          {agent.status === 'busy' ? '工作中' : '空闲'}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {agent.performance}%
                        </span>
                      </div>
                    </div>
                    <Progress value={agent.performance} className="h-1" />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Bot className="mx-auto h-12 w-12 mb-4 opacity-50" />
                <p>暂无代理数据</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 系统状态 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>系统状态</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">CPU使用率</span>
                <span className="text-sm text-muted-foreground">{systemMetrics.cpu}%</span>
              </div>
              <Progress value={systemMetrics.cpu} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">内存使用</span>
                <span className="text-sm text-muted-foreground">{systemMetrics.memory}%</span>
              </div>
              <Progress value={systemMetrics.memory} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">网络状态</span>
                <span className="text-sm text-green-600">{systemMetrics.network}</span>
              </div>
              <Progress value={100} />
            </div>
          </div>
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">最后更新</span>
              <span className="text-sm">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;