import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Wifi, 
  Clock,
  Server,
  AlertTriangle,
  CheckCircle,
  Info,
  Zap
} from 'lucide-react';

const SystemMonitor: React.FC = () => {
  // 模拟系统监控数据
  const systemStats = {
    cpu: { usage: 58, cores: 16, temperature: 68, loadAvg: [1.2, 1.5, 1.8] },
    memory: { used: 16.4, total: 32, percentage: 51.3, swap: 2.1 },
    disk: { used: 234.7, total: 1000, percentage: 23.5, io: { read: 45, write: 23 } },
    network: { in: 15.6, out: 23.4, latency: 12, packets: 1234 },
    uptime: '168h 45m',
    processes: 145,
    connections: 23
  };

  const systemLogs = [
    { time: '14:32:15', level: 'info', message: 'AI代理协调者开始新任务' },
    { time: '14:31:45', level: 'debug', message: '章节2内容生成完成，质量评分92%' },
    { time: '14:31:20', level: 'warning', message: '内存使用率超过50%，建议清理缓存' },
    { time: '14:30:55', level: 'info', message: '系统自动备份开始' },
    { time: '14:30:30', level: 'success', message: '质量监控代理完成一致性检查' },
    { time: '14:30:05', level: 'info', message: '新项目"武侠传说"创建成功' }
  ];

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'success':
      case 'info':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'debug':
        return <Info className="h-4 w-4 text-blue-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-green-600';
      case 'info':
        return 'text-blue-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      case 'debug':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">系统监控</h1>
        <p className="text-muted-foreground">
          实时监控系统性能和运行状态
        </p>
      </div>

      {/* 系统概览 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">运行时间</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.uptime}</div>
            <p className="text-xs text-muted-foreground">
              持续稳定运行
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">活跃进程</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.processes}</div>
            <p className="text-xs text-muted-foreground">
              运行中
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">网络连接</CardTitle>
            <Wifi className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.connections}</div>
            <p className="text-xs text-muted-foreground">
              活跃连接
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">系统状态</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-green-600 font-medium">正常运行</span>
            </div>
            <p className="text-xs text-muted-foreground">
              所有服务正常
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* CPU监控 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Cpu className="h-5 w-5" />
              <span>CPU监控</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>使用率</span>
                <span>{systemStats.cpu.usage}%</span>
              </div>
              <Progress value={systemStats.cpu.usage} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">核心数</p>
                <p className="font-medium">{systemStats.cpu.cores}</p>
              </div>
              <div>
                <p className="text-muted-foreground">温度</p>
                <p className="font-medium">{systemStats.cpu.temperature}°C</p>
              </div>
              <div>
                <p className="text-muted-foreground">负载1</p>
                <p className="font-medium">{systemStats.cpu.loadAvg[0]}</p>
              </div>
              <div>
                <p className="text-muted-foreground">负载5</p>
                <p className="font-medium">{systemStats.cpu.loadAvg[1]}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 内存监控 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MemoryStick className="h-5 w-5" />
              <span>内存监控</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>使用率</span>
                <span>{systemStats.memory.percentage}%</span>
              </div>
              <Progress value={systemStats.memory.percentage} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">已使用</p>
                <p className="font-medium">{systemStats.memory.used}GB</p>
              </div>
              <div>
                <p className="text-muted-foreground">总计</p>
                <p className="font-medium">{systemStats.memory.total}GB</p>
              </div>
              <div>
                <p className="text-muted-foreground">Swap使用</p>
                <p className="font-medium">{systemStats.memory.swap}GB</p>
              </div>
              <div>
                <p className="text-muted-foreground">可用</p>
                <p className="font-medium">{(systemStats.memory.total - systemStats.memory.used).toFixed(1)}GB</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 磁盘监控 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <HardDrive className="h-5 w-5" />
              <span>磁盘监控</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>使用率</span>
                <span>{systemStats.disk.percentage}%</span>
              </div>
              <Progress value={systemStats.disk.percentage} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">已使用</p>
                <p className="font-medium">{systemStats.disk.used}GB</p>
              </div>
              <div>
                <p className="text-muted-foreground">总计</p>
                <p className="font-medium">{systemStats.disk.total}GB</p>
              </div>
              <div>
                <p className="text-muted-foreground">读取速度</p>
                <p className="font-medium">{systemStats.disk.io.read}MB/s</p>
              </div>
              <div>
                <p className="text-muted-foreground">写入速度</p>
                <p className="font-medium">{systemStats.disk.io.write}MB/s</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 网络监控 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Wifi className="h-5 w-5" />
              <span>网络监控</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>延迟</span>
                <span>{systemStats.network.latency}ms</span>
              </div>
              <Progress value={Math.min(100, (200 - systemStats.network.latency) / 2)} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">下行速度</p>
                <p className="font-medium">{systemStats.network.in}MB/s</p>
              </div>
              <div>
                <p className="text-muted-foreground">上行速度</p>
                <p className="font-medium">{systemStats.network.out}MB/s</p>
              </div>
              <div>
                <p className="text-muted-foreground">数据包</p>
                <p className="font-medium">{systemStats.network.packets}</p>
              </div>
              <div>
                <p className="text-muted-foreground">连接状态</p>
                <p className="font-medium text-green-600">正常</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 系统日志 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>系统日志</span>
            </div>
            <Button variant="outline" size="sm">
              清空日志
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {systemLogs.map((log, index) => (
              <div key={index} className="flex items-start space-x-3 py-2 border-b border-border last:border-b-0">
                <span className="text-xs text-muted-foreground font-mono mt-0.5">
                  {log.time}
                </span>
                <div className="flex items-center space-x-2">
                  {getLogIcon(log.level)}
                  <span className={`text-xs ${getLogColor(log.level)} font-medium`}>
                    [{log.level.toUpperCase()}]
                  </span>
                </div>
                <span className="text-sm text-foreground flex-1">
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SystemMonitor;