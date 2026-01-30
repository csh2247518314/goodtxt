import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Bot, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Wifi, 
  Activity,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Play,
  Pause,
  RotateCcw,
  Settings,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Agent {
  id: string;
  name: string;
  type: 'coordinator' | 'writer' | 'editor' | 'researcher' | 'monitor';
  status: 'idle' | 'busy' | 'offline' | 'error';
  currentTask?: string;
  model: string;
  specialty: string[];
  performance: {
    tasksCompleted: number;
    avgQuality: number;
    avgTime: number;
    successRate: number;
  };
  lastActive: Date;
  uptime: string;
  memoryUsage: number;
  cpuUsage: number;
}

interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    in: number;
    out: number;
    latency: number;
  };
  uptime: string;
}

const AgentMonitor: React.FC = () => {
  const [activeTab, setActiveTab] = useState('agents');
  const [isRealTime, setIsRealTime] = useState(true);

  // 模拟数据
  const agents: Agent[] = [
    {
      id: '1',
      name: '协调者-Alpha',
      type: 'coordinator',
      status: 'busy',
      currentTask: '项目星际征途章节3生成调度',
      model: 'DeepSeek-V3',
      specialty: ['任务调度', '流程管理', '质量控制'],
      performance: {
        tasksCompleted: 156,
        avgQuality: 94,
        avgTime: 3.2,
        successRate: 98.5
      },
      lastActive: new Date(),
      uptime: '72h 15m',
      memoryUsage: 67,
      cpuUsage: 45
    },
    {
      id: '2',
      name: '作者-Beta',
      type: 'writer',
      status: 'busy',
      currentTask: '生成章节3内容：角色对话优化',
      model: 'Qwen-72B',
      specialty: ['剧情创作', '角色塑造', '对话生成'],
      performance: {
        tasksCompleted: 89,
        avgQuality: 91,
        avgTime: 5.8,
        successRate: 96.2
      },
      lastActive: new Date(),
      uptime: '48h 23m',
      memoryUsage: 78,
      cpuUsage: 62
    },
    {
      id: '3',
      name: '编辑-Gamma',
      type: 'editor',
      status: 'idle',
      currentTask: '等待新任务',
      model: 'Qwen-32B',
      specialty: ['语法检查', '文本润色', '风格统一'],
      performance: {
        tasksCompleted: 234,
        avgQuality: 96,
        avgTime: 2.1,
        successRate: 99.1
      },
      lastActive: new Date(Date.now() - 300000),
      uptime: '120h 45m',
      memoryUsage: 34,
      cpuUsage: 12
    },
    {
      id: '4',
      name: '研究者-Delta',
      type: 'researcher',
      status: 'busy',
      currentTask: '构建世界观：星际文明体系',
      model: 'Qwen-72B',
      specialty: ['资料收集', '世界观构建', '背景设定'],
      performance: {
        tasksCompleted: 67,
        avgQuality: 88,
        avgTime: 4.3,
        successRate: 94.8
      },
      lastActive: new Date(),
      uptime: '36h 12m',
      memoryUsage: 82,
      cpuUsage: 71
    },
    {
      id: '5',
      name: '质量监控-Epsilon',
      type: 'monitor',
      status: 'busy',
      currentTask: '全文一致性检查：角色设定验证',
      model: 'DeepSeek-Coder',
      specialty: ['质量检测', '一致性检查', '错误纠正'],
      performance: {
        tasksCompleted: 312,
        avgQuality: 97,
        avgTime: 1.8,
        successRate: 99.6
      },
      lastActive: new Date(),
      uptime: '96h 33m',
      memoryUsage: 56,
      cpuUsage: 38
    }
  ];

  const systemMetrics: SystemMetrics = {
    cpu: {
      usage: 58,
      cores: 16,
      temperature: 68
    },
    memory: {
      used: 16.4,
      total: 32,
      percentage: 51.3
    },
    disk: {
      used: 234.7,
      total: 1000,
      percentage: 23.5
    },
    network: {
      in: 15.6,
      out: 23.4,
      latency: 12
    },
    uptime: '168h 45m'
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'busy': return <Activity className="h-4 w-4 text-green-600" />;
      case 'idle': return <Minus className="h-4 w-4 text-blue-600" />;
      case 'offline': return <XCircle className="h-4 w-4 text-gray-400" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-600" />;
      default: return <XCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'busy': return 'bg-green-100 text-green-800';
      case 'idle': return 'bg-blue-100 text-blue-800';
      case 'offline': return 'bg-gray-100 text-gray-600';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'busy': return '工作中';
      case 'idle': return '空闲';
      case 'offline': return '离线';
      case 'error': return '错误';
      default: return '未知';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'coordinator': return '协调者';
      case 'writer': return '作者';
      case 'editor': return '编辑';
      case 'researcher': return '研究者';
      case 'monitor': return '监控';
      default: return '未知';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题和控制 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI代理监控</h1>
          <p className="text-muted-foreground">
            实时监控AI代理状态和系统性能
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={isRealTime ? "default" : "outline"}
            size="sm"
            onClick={() => setIsRealTime(!isRealTime)}
          >
            {isRealTime ? <Pause className="mr-2 h-4 w-4" /> : <Play className="mr-2 h-4 w-4" />}
            {isRealTime ? '暂停监控' : '开始监控'}
          </Button>
          <Button variant="outline" size="sm">
            <RotateCcw className="mr-2 h-4 w-4" />
            刷新
          </Button>
        </div>
      </div>

      {/* 总体状态概览 */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">在线代理</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.filter(a => a.status !== 'offline').length}
            </div>
            <p className="text-xs text-muted-foreground">
              / {agents.length} 总数
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">活跃任务</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agents.filter(a => a.status === 'busy').length}
            </div>
            <p className="text-xs text-muted-foreground">
              正在执行
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均质量</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(agents.reduce((acc, a) => acc + a.performance.avgQuality, 0) / agents.length)}%
            </div>
            <p className="text-xs text-muted-foreground">
              整体表现
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">系统负载</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemMetrics.cpu.usage}%</div>
            <p className="text-xs text-muted-foreground">
              CPU使用率
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="agents">AI代理</TabsTrigger>
          <TabsTrigger value="system">系统监控</TabsTrigger>
          <TabsTrigger value="performance">性能分析</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-6">
          {/* 代理列表 */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {agents.map((agent) => (
              <Card key={agent.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-5 w-5" />
                      <div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {getTypeLabel(agent.type)}
                        </p>
                      </div>
                    </div>
                    {getStatusIcon(agent.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* 状态和任务 */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge className={getStatusColor(agent.status)}>
                        {getStatusLabel(agent.status)}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        运行 {agent.uptime}
                      </span>
                    </div>
                    {agent.currentTask && (
                      <p className="text-sm text-muted-foreground">
                        {agent.currentTask}
                      </p>
                    )}
                  </div>

                  {/* 性能指标 */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">完成任务</p>
                      <p className="font-medium">{agent.performance.tasksCompleted}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">平均质量</p>
                      <p className="font-medium">{agent.performance.avgQuality}%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">平均时间</p>
                      <p className="font-medium">{agent.performance.avgTime}min</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">成功率</p>
                      <p className="font-medium">{agent.performance.successRate}%</p>
                    </div>
                  </div>

                  {/* 资源使用 */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>CPU使用率</span>
                      <span>{agent.cpuUsage}%</span>
                    </div>
                    <Progress value={agent.cpuUsage} className="h-2" />
                    <div className="flex justify-between text-sm">
                      <span>内存使用</span>
                      <span>{agent.memoryUsage}%</span>
                    </div>
                    <Progress value={agent.memoryUsage} className="h-2" />
                  </div>

                  {/* 专业领域 */}
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">专业领域</p>
                    <div className="flex flex-wrap gap-1">
                      {agent.specialty.map((skill, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* 模型信息 */}
                  <div className="text-sm">
                    <p className="text-muted-foreground">模型</p>
                    <p className="font-medium">{agent.model}</p>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Settings className="mr-2 h-3 w-3" />
                      配置
                    </Button>
                    <Button variant="outline" size="sm">
                      <RotateCcw className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          {/* 系统监控 */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5" />
                  <span>CPU状态</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>使用率</span>
                    <span>{systemMetrics.cpu.usage}%</span>
                  </div>
                  <Progress value={systemMetrics.cpu.usage} />
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">核心数</p>
                    <p className="font-medium">{systemMetrics.cpu.cores}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">温度</p>
                    <p className="font-medium">{systemMetrics.cpu.temperature}°C</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MemoryStick className="h-5 w-5" />
                  <span>内存状态</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>使用率</span>
                    <span>{systemMetrics.memory.percentage}%</span>
                  </div>
                  <Progress value={systemMetrics.memory.percentage} />
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">已使用</p>
                    <p className="font-medium">{systemMetrics.memory.used}GB</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">总计</p>
                    <p className="font-medium">{systemMetrics.memory.total}GB</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <HardDrive className="h-5 w-5" />
                  <span>存储状态</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>使用率</span>
                    <span>{systemMetrics.disk.percentage}%</span>
                  </div>
                  <Progress value={systemMetrics.disk.percentage} />
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">已使用</p>
                    <p className="font-medium">{systemMetrics.disk.used}GB</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">总计</p>
                    <p className="font-medium">{systemMetrics.disk.total}GB</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Wifi className="h-5 w-5" />
                  <span>网络状态</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>延迟</span>
                    <span>{systemMetrics.network.latency}ms</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">下行</p>
                    <p className="font-medium">{systemMetrics.network.in}MB/s</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">上行</p>
                    <p className="font-medium">{systemMetrics.network.out}MB/s</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>代理性能排名</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agents
                    .sort((a, b) => b.performance.avgQuality - a.performance.avgQuality)
                    .map((agent, index) => (
                      <div key={agent.id} className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{agent.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {getTypeLabel(agent.type)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{agent.performance.avgQuality}%</p>
                          <p className="text-sm text-muted-foreground">
                            {agent.performance.tasksCompleted} 任务
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>系统运行时间</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-4">
                  <div className="text-4xl font-bold text-primary">
                    {systemMetrics.uptime}
                  </div>
                  <p className="text-muted-foreground">
                    系统持续稳定运行
                  </p>
                  <div className="flex items-center justify-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="text-sm text-green-600">正常运行</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AgentMonitor;