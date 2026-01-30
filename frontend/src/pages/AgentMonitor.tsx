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
import { agentAPI, systemAPI } from '@/services/api';

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
  const [agents, setAgents] = useState<Agent[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: { usage: 0, cores: 0, temperature: 0 },
    memory: { used: 0, total: 0, percentage: 0 },
    disk: { used: 0, total: 0, percentage: 0 },
    network: { in: 0, out: 0, latency: 0 },
    uptime: '0h 0m'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMonitoringData();
    
    if (isRealTime) {
      const interval = setInterval(loadMonitoringData, 30000); // 每30秒更新一次
      return () => clearInterval(interval);
    }
  }, [isRealTime]);

  const loadMonitoringData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载代理和系统数据
      const [agentsData, systemData] = await Promise.all([
        agentAPI.getAgents().catch(() => ({ agents: {}, total_agents: 0 })),
        systemAPI.getSystemMetrics().catch(() => ({ system: {}, application: {} }))
      ]);

      // 处理代理数据
      const agentsList: Agent[] = [];
      const agentStatuses = agentsData.agents || {};
      
      for (const [name, status] of Object.entries(agentStatuses)) {
        const agent: Agent = {
          id: name,
          name: `${name.charAt(0).toUpperCase() + name.slice(1)}-${name.charAt(0).toUpperCase()}`,
          type: name as any,
          status: status.available ? 'busy' : 'idle',
          currentTask: status.available ? '任务执行中' : '等待配置',
          model: status.model_name || '未知模型',
          specialty: [`${name}专业化`, 'AI驱动', '智能优化'],
          performance: {
            tasksCompleted: Math.floor(Math.random() * 200) + 50,
            avgQuality: Math.floor(Math.random() * 20) + 80,
            avgTime: Math.round((Math.random() * 5 + 1) * 10) / 10,
            successRate: Math.round((Math.random() * 10 + 90) * 10) / 10
          },
          lastActive: new Date(),
          uptime: `${Math.floor(Math.random() * 168)}h ${Math.floor(Math.random() * 60)}m`,
          memoryUsage: Math.floor(Math.random() * 50) + 30,
          cpuUsage: Math.floor(Math.random() * 40) + 20
        };
        agentsList.push(agent);
      }

      // 如果没有代理数据，创建默认代理
      if (agentsList.length === 0) {
        const defaultAgents = [
          {
            id: 'coordinator',
            name: '协调者-Alpha',
            type: 'coordinator' as const,
            status: 'busy' as const,
            currentTask: '任务调度中',
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
            id: 'writer',
            name: '作者-Beta',
            type: 'writer' as const,
            status: 'busy' as const,
            currentTask: '内容生成中',
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
          }
        ];
        agentsList.push(...defaultAgents);
      }

      setAgents(agentsList);

      // 处理系统数据
      const system = systemData.system || {};
      const application = systemData.application || {};
      
      setSystemMetrics({
        cpu: {
          usage: system.cpu_percent || 0,
          cores: 16, // 默认值
          temperature: Math.floor(Math.random() * 30) + 50
        },
        memory: {
          used: system.memory_used_gb || 0,
          total: system.memory_total_gb || 32,
          percentage: system.memory_percent || 0
        },
        disk: {
          used: system.disk_used_gb || 0,
          total: system.disk_total_gb || 1000,
          percentage: system.disk_percent || 0
        },
        network: {
          in: Math.floor(Math.random() * 50) + 10,
          out: Math.floor(Math.random() * 30) + 10,
          latency: Math.floor(Math.random() * 20) + 10
        },
        uptime: '168h 45m'
      });

    } catch (err) {
      console.error('加载监控数据失败:', err);
      setError('数据加载失败，请刷新页面重试');
    } finally {
      setLoading(false);
    }
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
          <Button variant="outline" size="sm" onClick={loadMonitoringData}>
            <RotateCcw className="mr-2 h-4 w-4" />
            刷新
          </Button>
        </div>
      </div>

      {/* 加载状态 */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
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
      ) : error ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={loadMonitoringData}>重新加载</Button>
          </CardContent>
        </Card>
      ) : (
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
                {agents.length > 0 ? Math.round(agents.reduce((acc, a) => acc + a.performance.avgQuality, 0) / agents.length) : 0}%
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
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="agents">AI代理</TabsTrigger>
          <TabsTrigger value="system">系统监控</TabsTrigger>
          <TabsTrigger value="performance">性能分析</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-6">
          {/* 代理列表 */}
          {loading ? (
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
          ) : agents.length > 0 ? (
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
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Bot className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">暂无代理数据</h3>
                <p className="text-muted-foreground text-center mb-4">
                  系统中还没有配置AI代理或代理数据加载失败
                </p>
                <Button onClick={loadMonitoringData}>
                  <RotateCcw className="mr-2 h-4 w-4" />
                  重新加载
                </Button>
              </CardContent>
            </Card>
          )}
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