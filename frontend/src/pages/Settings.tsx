import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Settings, 
  Save, 
  RotateCcw, 
  Download, 
  Upload,
  Bot,
  Brain,
  Key,
  Database,
  Bell,
  Shield,
  Palette,
  Globe,
  Cpu,
  HardDrive,
  Wifi,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Plus
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AIModel {
  id: string;
  name: string;
  provider: string;
  type: 'coordinator' | 'writer' | 'editor' | 'researcher' | 'monitor';
  status: 'active' | 'inactive' | 'error';
  version: string;
  performance: number;
  cost: number;
  latency: number;
}

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ai-models');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // 模拟AI模型数据
  const aiModels: AIModel[] = [
    {
      id: '1',
      name: 'DeepSeek-V3',
      provider: 'DeepSeek',
      type: 'coordinator',
      status: 'active',
      version: 'v3.0',
      performance: 95,
      cost: 0.002,
      latency: 150
    },
    {
      id: '2',
      name: 'Qwen-72B',
      provider: '阿里云',
      type: 'writer',
      status: 'active',
      version: '72B-Chat',
      performance: 92,
      cost: 0.0015,
      latency: 200
    },
    {
      id: '3',
      name: 'Qwen-32B',
      provider: '阿里云',
      type: 'editor',
      status: 'active',
      version: '32B-Instruct',
      performance: 94,
      cost: 0.001,
      latency: 120
    },
    {
      id: '4',
      name: 'DeepSeek-Coder',
      provider: 'DeepSeek',
      type: 'monitor',
      status: 'active',
      version: 'v2.0',
      performance: 88,
      cost: 0.0025,
      latency: 180
    }
  ];

  const [settings, setSettings] = useState({
    // AI模型设置
    defaultCoordinator: '1',
    defaultWriter: '2',
    defaultEditor: '3',
    defaultMonitor: '4',
    
    // 生成设置
    maxWordsPerChapter: 3000,
    targetQuality: 85,
    maxGenerationTime: 600,
    autoSave: true,
    autoBackup: true,
    
    // 系统设置
    maxConcurrentTasks: 5,
    memoryLimit: 16,
    diskSpaceLimit: 100,
    networkTimeout: 30,
    
    // 通知设置
    enableNotifications: true,
    emailNotifications: true,
    progressNotifications: true,
    errorNotifications: true,
    
    // 界面设置
    theme: 'system',
    language: 'zh-CN',
    autoRefresh: true,
    refreshInterval: 30
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    // 保存设置逻辑
    console.log('保存设置:', settings);
    setHasUnsavedChanges(false);
  };

  const handleReset = () => {
    // 重置设置逻辑
    console.log('重置设置');
    setHasUnsavedChanges(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'inactive': return <XCircle className="h-4 w-4 text-gray-400" />;
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default: return <XCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-600';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">系统设置</h1>
          <p className="text-muted-foreground">
            配置AI模型、生成参数和系统偏好
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {hasUnsavedChanges && (
            <Badge variant="outline" className="text-orange-600">
              有未保存的更改
            </Badge>
          )}
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="mr-2 h-4 w-4" />
            重置
          </Button>
          <Button onClick={handleSave} disabled={!hasUnsavedChanges}>
            <Save className="mr-2 h-4 w-4" />
            保存
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="ai-models">AI模型</TabsTrigger>
          <TabsTrigger value="generation">生成设置</TabsTrigger>
          <TabsTrigger value="system">系统配置</TabsTrigger>
          <TabsTrigger value="notifications">通知设置</TabsTrigger>
          <TabsTrigger value="interface">界面设置</TabsTrigger>
        </TabsList>

        <TabsContent value="ai-models" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <span>AI模型配置</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {aiModels.map((model) => (
                <div key={model.id} className="border rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Brain className="h-6 w-6" />
                      <div>
                        <h3 className="font-medium">{model.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {model.provider} • {model.version}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(model.status)}
                      <Badge className={getStatusColor(model.status)}>
                        {model.status === 'active' ? '活跃' : 
                         model.status === 'inactive' ? '非活跃' : '错误'}
                      </Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">性能</p>
                      <div className="flex items-center space-x-2">
                        <Progress value={model.performance} className="h-2 flex-1" />
                        <span className="font-medium">{model.performance}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-muted-foreground">成本</p>
                      <p className="font-medium">¥{model.cost}/1K tokens</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">延迟</p>
                      <p className="font-medium">{model.latency}ms</p>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      测试连接
                    </Button>
                    <Button variant="outline" size="sm">
                      配置
                    </Button>
                    {model.status === 'active' ? (
                      <Button variant="outline" size="sm">
                        停用
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm">
                        启用
                      </Button>
                    )}
                  </div>
                </div>
              ))}

              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                <h3 className="font-medium mb-2">添加新模型</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  支持添加自定义AI模型配置
                </p>
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" />
                  添加模型
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generation" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>生成参数</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">每章最大字数</label>
                  <Input
                    type="number"
                    value={settings.maxWordsPerChapter}
                    onChange={(e) => handleSettingChange('maxWordsPerChapter', parseInt(e.target.value))}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">目标质量分数</label>
                  <Input
                    type="number"
                    value={settings.targetQuality}
                    onChange={(e) => handleSettingChange('targetQuality', parseInt(e.target.value))}
                    className="mt-1"
                    max="100"
                    min="0"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">最大生成时间(秒)</label>
                  <Input
                    type="number"
                    value={settings.maxGenerationTime}
                    onChange={(e) => handleSettingChange('maxGenerationTime', parseInt(e.target.value))}
                    className="mt-1"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>自动化设置</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">自动保存</p>
                    <p className="text-sm text-muted-foreground">定期保存生成内容</p>
                  </div>
                  <Button
                    variant={settings.autoSave ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('autoSave', !settings.autoSave)}
                  >
                    {settings.autoSave ? '开启' : '关闭'}
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">自动备份</p>
                    <p className="text-sm text-muted-foreground">自动备份项目数据</p>
                  </div>
                  <Button
                    variant={settings.autoBackup ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('autoBackup', !settings.autoBackup)}
                  >
                    {settings.autoBackup ? '开启' : '关闭'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5" />
                  <span>性能设置</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">最大并发任务数</label>
                  <Input
                    type="number"
                    value={settings.maxConcurrentTasks}
                    onChange={(e) => handleSettingChange('maxConcurrentTasks', parseInt(e.target.value))}
                    className="mt-1"
                    min="1"
                    max="10"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">内存限制(GB)</label>
                  <Input
                    type="number"
                    value={settings.memoryLimit}
                    onChange={(e) => handleSettingChange('memoryLimit', parseInt(e.target.value))}
                    className="mt-1"
                    min="4"
                    max="64"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">磁盘空间限制(GB)</label>
                  <Input
                    type="number"
                    value={settings.diskSpaceLimit}
                    onChange={(e) => handleSettingChange('diskSpaceLimit', parseInt(e.target.value))}
                    className="mt-1"
                    min="10"
                    max="1000"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Globe className="h-5 w-5" />
                  <span>网络设置</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">网络超时(秒)</label>
                  <Input
                    type="number"
                    value={settings.networkTimeout}
                    onChange={(e) => handleSettingChange('networkTimeout', parseInt(e.target.value))}
                    className="mt-1"
                    min="10"
                    max="300"
                  />
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">连接状态</p>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">连接正常</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">API响应时间</p>
                  <p className="text-sm text-muted-foreground">平均 156ms</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>通知设置</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">启用通知</p>
                    <p className="text-sm text-muted-foreground">接收系统通知</p>
                  </div>
                  <Button
                    variant={settings.enableNotifications ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('enableNotifications', !settings.enableNotifications)}
                  >
                    {settings.enableNotifications ? '开启' : '关闭'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">邮件通知</p>
                    <p className="text-sm text-muted-foreground">通过邮件接收重要通知</p>
                  </div>
                  <Button
                    variant={settings.emailNotifications ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('emailNotifications', !settings.emailNotifications)}
                    disabled={!settings.enableNotifications}
                  >
                    {settings.emailNotifications ? '开启' : '关闭'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">进度通知</p>
                    <p className="text-sm text-muted-foreground">生成进度更新</p>
                  </div>
                  <Button
                    variant={settings.progressNotifications ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('progressNotifications', !settings.progressNotifications)}
                    disabled={!settings.enableNotifications}
                  >
                    {settings.progressNotifications ? '开启' : '关闭'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">错误通知</p>
                    <p className="text-sm text-muted-foreground">系统错误和警告</p>
                  </div>
                  <Button
                    variant={settings.errorNotifications ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('errorNotifications', !settings.errorNotifications)}
                    disabled={!settings.enableNotifications}
                  >
                    {settings.errorNotifications ? '开启' : '关闭'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interface" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Palette className="h-5 w-5" />
                  <span>外观设置</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">主题</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => handleSettingChange('theme', e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
                  >
                    <option value="light">浅色</option>
                    <option value="dark">深色</option>
                    <option value="system">跟随系统</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium">语言</label>
                  <select
                    value={settings.language}
                    onChange={(e) => handleSettingChange('language', e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
                  >
                    <option value="zh-CN">简体中文</option>
                    <option value="en-US">English</option>
                  </select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <RefreshCw className="h-5 w-5" />
                  <span>自动刷新</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">自动刷新</p>
                    <p className="text-sm text-muted-foreground">自动更新页面数据</p>
                  </div>
                  <Button
                    variant={settings.autoRefresh ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('autoRefresh', !settings.autoRefresh)}
                  >
                    {settings.autoRefresh ? '开启' : '关闭'}
                  </Button>
                </div>
                {settings.autoRefresh && (
                  <div>
                    <label className="text-sm font-medium">刷新间隔(秒)</label>
                    <Input
                      type="number"
                      value={settings.refreshInterval}
                      onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                      className="mt-1"
                      min="10"
                      max="300"
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>数据管理</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-2">
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  导出配置
                </Button>
                <Button variant="outline">
                  <Upload className="mr-2 h-4 w-4" />
                  导入配置
                </Button>
                <Button variant="destructive">
                  <Database className="mr-2 h-4 w-4" />
                  重置数据库
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;