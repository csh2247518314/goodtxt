import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  BookOpen, 
  Users, 
  Clock,
  Award,
  AlertCircle,
  CheckCircle,
  Star,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

const Analytics: React.FC = () => {
  // 模拟分析数据
  const qualityMetrics = [
    { name: '可读性', score: 92, trend: 'up', change: '+3%' },
    { name: '连贯性', score: 88, trend: 'up', change: '+2%' },
    { name: '创意性', score: 85, trend: 'down', change: '-1%' },
    { name: '语法准确性', score: 94, trend: 'up', change: '+1%' },
    { name: '一致性', score: 90, trend: 'up', change: '+2%' },
    { name: '吸引力', score: 87, trend: 'up', change: '+4%' }
  ];

  const generationStats = {
    totalWords: 84750,
    totalChapters: 32,
    avgWordsPerChapter: 2648,
    avgGenerationTime: 4.2,
    successRate: 96.8,
    qualityScore: 89.2
  };

  const agentPerformance = [
    { name: '协调者-Alpha', efficiency: 94, quality: 96, speed: 88 },
    { name: '作者-Beta', efficiency: 91, quality: 92, speed: 89 },
    { name: '编辑-Gamma', efficiency: 97, quality: 98, speed: 95 },
    { name: '研究者-Delta', efficiency: 88, quality: 90, speed: 82 },
    { name: '质量监控-Epsilon', efficiency: 99, quality: 99, speed: 97 }
  ];

  const genreDistribution = [
    { genre: '科幻', count: 3, percentage: 37.5 },
    { genre: '言情', count: 2, percentage: 25 },
    { genre: '悬疑', count: 2, percentage: 25 },
    { genre: '武侠', count: 1, percentage: 12.5 }
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">质量分析</h1>
        <p className="text-muted-foreground">
          深度分析小说质量和AI代理表现
        </p>
      </div>

      {/* 关键指标 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总字数</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.totalWords.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +12% 比上月
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总章节</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.totalChapters}</div>
            <p className="text-xs text-muted-foreground">
              +5 新增
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均字数</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.avgWordsPerChapter}</div>
            <p className="text-xs text-muted-foreground">
              每章
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均时间</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.avgGenerationTime}min</div>
            <p className="text-xs text-muted-foreground">
              生成时间
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">成功率</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.successRate}%</div>
            <p className="text-xs text-muted-foreground">
              质量控制
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">质量评分</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{generationStats.qualityScore}%</div>
            <p className="text-xs text-muted-foreground">
              整体表现
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 质量指标分析 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>质量指标分析</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {qualityMetrics.map((metric, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{metric.name}</span>
                    {metric.trend === 'up' ? (
                      <ArrowUp className="h-3 w-3 text-green-600" />
                    ) : (
                      <ArrowDown className="h-3 w-3 text-red-600" />
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{metric.score}%</span>
                    <span className={`text-xs ${
                      metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metric.change}
                    </span>
                  </div>
                </div>
                <Progress value={metric.score} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* AI代理表现 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>AI代理表现</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {agentPerformance.map((agent, index) => (
              <div key={index} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium">{agent.name}</h4>
                  <div className="flex items-center space-x-1">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span className="text-xs text-muted-foreground">
                      {Math.round((agent.efficiency + agent.quality + agent.speed) / 3)}%
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <p className="text-muted-foreground">效率</p>
                    <Progress value={agent.efficiency} className="h-1" />
                  </div>
                  <div>
                    <p className="text-muted-foreground">质量</p>
                    <Progress value={agent.quality} className="h-1" />
                  </div>
                  <div>
                    <p className="text-muted-foreground">速度</p>
                    <Progress value={agent.speed} className="h-1" />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* 题材分布 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5" />
              <span>题材分布</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {genreDistribution.map((genre, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{genre.genre}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">{genre.count} 项目</span>
                    <span className="text-sm font-medium">{genre.percentage}%</span>
                  </div>
                </div>
                <Progress value={genre.percentage * 4} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* 改进建议 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>改进建议</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-orange-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">创意性有待提升</p>
                  <p className="text-xs text-muted-foreground">
                    建议增加更多独特的创意元素和创新的故事设定
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">连贯性表现优秀</p>
                  <p className="text-xs text-muted-foreground">
                    继续保持当前的连贯性标准，这是我们的强项
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">质量监控系统高效</p>
                  <p className="text-xs text-muted-foreground">
                    质量监控代理的表现突出，值得在所有项目中推广
                  </p>
                </div>
              </div>
            </div>
            <Button variant="outline" className="w-full mt-4">
              查看详细报告
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* 质量趋势图表 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>质量趋势</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 mx-auto mb-4" />
              <p>质量趋势图表</p>
              <p className="text-sm">基于时间线的质量变化分析</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;