import React from 'react';
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

const Dashboard: React.FC = () => {
  // 模拟数据
  const stats = [
    {
      title: '活跃项目',
      value: '3',
      change: '+2',
      icon: BookOpen,
      color: 'text-blue-600'
    },
    {
      title: 'AI代理',
      value: '5',
      change: '全部在线',
      icon: Bot,
      color: 'text-green-600'
    },
    {
      title: '今日生成',
      value: '2,847',
      change: '+12%',
      icon: TrendingUp,
      color: 'text-purple-600'
    },
    {
      title: '完成章节',
      value: '24',
      change: '+5',
      icon: CheckCircle,
      color: 'text-emerald-600'
    }
  ];

  const recentProjects = [
    {
      id: '1',
      title: '星际征途',
      genre: '科幻',
      progress: 65,
      status: 'generating',
      chapters: 12,
      words: 15420
    },
    {
      id: '2',
      title: '古风情缘',
      genre: '言情',
      progress: 90,
      status: 'reviewing',
      chapters: 8,
      words: 23150
    },
    {
      id: '3',
      title: '悬疑小镇',
      genre: '悬疑',
      progress: 30,
      status: 'draft',
      chapters: 5,
      words: 8930
    }
  ];

  const agentStatus = [
    { name: '协调者', status: 'busy', currentTask: '章节3生成中', performance: 95 },
    { name: '作者', status: 'busy', currentTask: '角色对话优化', performance: 88 },
    { name: '编辑', status: 'idle', currentTask: '等待任务', performance: 92 },
    { name: '研究者', status: 'busy', currentTask: '世界观构建', performance: 85 },
    { name: '质量监控', status: 'busy', currentTask: '全文一致性检查', performance: 90 }
  ];

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
        {stats.map((stat) => {
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
            {recentProjects.map((project) => (
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
                              project.status === 'reviewing' ? 'secondary' : 'outline'}
                    >
                      {project.status === 'generating' ? '生成中' :
                       project.status === 'reviewing' ? '审核中' : '草稿'}
                    </Badge>
                  </div>
                  <Progress value={project.progress} className="h-2" />
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              查看所有项目
            </Button>
          </CardContent>
        </Card>

        {/* AI代理状态 */}
        <Card>
          <CardHeader>
            <CardTitle>AI代理状态</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {agentStatus.map((agent) => (
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
            ))}
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
                <span className="text-sm text-muted-foreground">45%</span>
              </div>
              <Progress value={45} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">内存使用</span>
                <span className="text-sm text-muted-foreground">67%</span>
              </div>
              <Progress value={67} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">网络状态</span>
                <span className="text-sm text-green-600">正常</span>
              </div>
              <Progress value={100} />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;