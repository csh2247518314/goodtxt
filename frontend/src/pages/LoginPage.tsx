import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { BookOpen, Mail, Lock, User, AlertCircle, Loader2 } from 'lucide-react';

const LoginPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const { login, register, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isLogin) {
      const success = await login(formData.username, formData.password);
      if (success) {
        navigate('/');
      }
    } else {
      const success = await register(formData.username, formData.email, formData.password);
      if (success) {
        navigate('/');
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo和标题 */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">GoodTxt</h1>
              <p className="text-sm text-gray-600">多AI协同小说生成系统</p>
            </div>
          </div>
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            智能化创作，协同化生成
          </Badge>
        </div>

        {/* 登录/注册表单 */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">
              {isLogin ? '登录账户' : '创建账户'}
            </CardTitle>
            <p className="text-sm text-center text-gray-600">
              {isLogin 
                ? '欢迎回来，请输入您的登录信息' 
                : '加入GoodTxt，开始您的AI创作之旅'
              }
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 错误提示 */}
            {error && (
              <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}



            {/* 表单 */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 用户名 */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  用户名
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    type="text"
                    name="username"
                    placeholder="请输入用户名"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    className="pl-10"
                  />
                </div>
              </div>

              {/* 邮箱 (仅注册时显示) */}
              {!isLogin && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    邮箱地址
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      type="email"
                      name="email"
                      placeholder="请输入邮箱地址"
                      value={formData.email}
                      onChange={handleInputChange}
                      required={!isLogin}
                      className="pl-10"
                    />
                  </div>
                </div>
              )}

              {/* 密码 */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    type="password"
                    name="password"
                    placeholder="请输入密码"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="pl-10"
                  />
                </div>
              </div>

              {/* 提交按钮 */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {isLogin ? '登录中...' : '注册中...'}
                  </>
                ) : (
                  isLogin ? '登录' : '注册'
                )}
              </Button>
            </form>

            {/* 切换登录/注册 */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                {isLogin ? '还没有账户？' : '已有账户？'}
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="ml-1 text-blue-600 hover:text-blue-700 font-medium"
                >
                  {isLogin ? '立即注册' : '立即登录'}
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 系统信息 */}
        <div className="text-center space-y-2">
          <p className="text-xs text-gray-500">
            GoodTxt 多AI协同小说生成系统
          </p>
          <div className="flex items-center justify-center space-x-4 text-xs text-gray-400">
            <span>✨ AI智能创作</span>
            <span>🚀 多代理协同</span>
            <span>📊 质量监控</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;