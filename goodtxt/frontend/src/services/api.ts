// API服务层
import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 令牌管理
let authToken: string | null = localStorage.getItem('auth_token');

// 设置请求拦截器
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 令牌过期，清除本地存储并重定向到登录页
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  // 登录
  async login(username: string, password: string) {
    const response = await api.post('/auth/login', { username, password });
    const { token, user } = response.data;
    authToken = token;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    return { token, user };
  },

  // 注册
  async register(username: string, email: string, password: string) {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },

  // 登出
  async logout() {
    authToken = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  // 获取当前用户信息
  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 刷新令牌
  async refreshToken() {
    const response = await api.post('/auth/refresh');
    const { token } = response.data;
    authToken = token;
    localStorage.setItem('auth_token', token);
    return token;
  }
};

// 项目相关API
export const projectAPI = {
  // 获取项目列表
  async getProjects(params?: any) {
    const response = await api.get('/projects', { params });
    return response.data;
  },

  // 创建项目
  async createProject(projectData: any) {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  // 获取项目详情
  async getProject(projectId: string) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  // 更新项目
  async updateProject(projectId: string, data: any) {
    const response = await api.put(`/projects/${projectId}`, data);
    return response.data;
  },

  // 删除项目
  async deleteProject(projectId: string) {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },

  // 开始生成
  async startGeneration(projectId: string, chapterCount?: number) {
    const response = await api.post(`/projects/${projectId}/generate`, { chapter_count: chapterCount });
    return response.data;
  },

  // 获取项目状态
  async getProjectStatus(projectId: string) {
    const response = await api.get(`/projects/${projectId}/status`);
    return response.data;
  },

  // 导出项目
  async exportProject(projectId: string, format: string = 'txt') {
    const response = await api.get(`/projects/${projectId}/export`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }
};

// 章节相关API
export const chapterAPI = {
  // 获取项目章节
  async getProjectChapters(projectId: string) {
    const response = await api.get(`/projects/${projectId}/chapters`);
    return response.data;
  },

  // 获取单个章节
  async getChapter(chapterId: string) {
    const response = await api.get(`/chapters/${chapterId}`);
    return response.data;
  },

  // 更新章节内容
  async updateChapter(chapterId: string, content: string) {
    const response = await api.put(`/chapters/${chapterId}`, { content });
    return response.data;
  },

  // 评估章节质量
  async evaluateChapterQuality(chapterId: string) {
    const response = await api.post(`/chapters/${chapterId}/quality`);
    return response.data;
  },

  // 重新生成章节
  async regenerateChapter(chapterId: string, instructions?: string) {
    const response = await api.post(`/chapters/${chapterId}/regenerate`, { instructions });
    return response.data;
  }
};

// AI代理相关API
export const agentAPI = {
  // 获取AI代理列表
  async getAgents() {
    const response = await api.get('/agents');
    return response.data;
  },

  // 获取代理状态
  async getAgentStatus(agentId?: string) {
    const url = agentId ? `/agents/${agentId}/status` : '/agents/status';
    const response = await api.get(url);
    return response.data;
  },

  // 发送代理命令
  async sendAgentCommand(agentId: string, command: string, params?: any) {
    const response = await api.post(`/agents/${agentId}/command`, {
      command,
      params
    });
    return response.data;
  },

  // 获取代理性能数据
  async getAgentPerformance(agentId?: string, timeRange?: string) {
    const params: any = timeRange ? { time_range: timeRange } : {};
    const url = agentId ? `/agents/${agentId}/performance` : '/agents/performance';
    const response = await api.get(url, { params });
    return response.data;
  },

  // 配置AI模型
  async configureModel(modelType: string, config: any) {
    const response = await api.post(`/agents/models/${modelType}/config`, config);
    return response.data;
  },

  // 测试模型连接
  async testModelConnection(modelType: string) {
    const response = await api.post(`/agents/models/${modelType}/test`);
    return response.data;
  }
};

// 系统相关API
export const systemAPI = {
  // 获取系统状态
  async getSystemStatus() {
    const response = await api.get('/system/status');
    return response.data;
  },

  // 获取系统指标
  async getSystemMetrics() {
    const response = await api.get('/system/metrics');
    return response.data;
  },

  // 获取系统日志
  async getSystemLogs(params?: any) {
    const response = await api.get('/system/logs', { params });
    return response.data;
  },

  // 健康检查
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
};

// 质量分析API
export const qualityAPI = {
  // 获取质量历史
  async getQualityHistory(limit?: number) {
    const params: any = limit ? { limit } : {};
    const response = await api.get('/quality/history', { params });
    return response.data;
  },

  // 获取项目质量报告
  async getProjectQualityReport(projectId: string) {
    const response = await api.get(`/quality/project/${projectId}/report`);
    return response.data;
  },

  // 获取全局质量统计
  async getGlobalQualityStats() {
    const response = await api.get('/quality/stats');
    return response.data;
  }
};

// 记忆管理API
export const memoryAPI = {
  // 搜索记忆
  async searchMemory(query: string, category?: string, limit?: number) {
    const params: any = { query };
    if (category) params.category = category;
    if (limit) params.limit = limit;
    
    const response = await api.get('/memory/search', { params });
    return response.data;
  },

  // 获取记忆详情
  async getMemoryDetails(memoryId: string) {
    const response = await api.get(`/memory/${memoryId}`);
    return response.data;
  },

  // 获取记忆统计
  async getMemoryStats() {
    const response = await api.get('/memory/stats');
    return response.data;
  }
};

// 配置管理API
export const configAPI = {
  // 获取系统配置
  async getSystemConfig() {
    const response = await api.get('/config');
    return response.data;
  },

  // 更新系统配置
  async updateSystemConfig(config: any) {
    const response = await api.put('/config', config);
    return response.data;
  },

  // 获取AI模型配置
  async getAIModelConfig() {
    const response = await api.get('/config/models');
    return response.data;
  },

  // 更新AI模型配置
  async updateAIModelConfig(config: any) {
    const response = await api.put('/config/models', config);
    return response.data;
  },

  // 验证配置
  async validateConfig(config: any) {
    const response = await api.post('/config/validate', config);
    return response.data;
  },

  // 重置配置
  async resetConfig() {
    const response = await api.post('/config/reset');
    return response.data;
  }
};

// 用户管理API
export const userAPI = {
  // 获取用户列表
  async getUsers(params?: any) {
    const response = await api.get('/users', { params });
    return response.data;
  },

  // 获取用户统计
  async getUserStats(userId: string) {
    const response = await api.get(`/users/${userId}/stats`);
    return response.data;
  },

  // 更新用户角色
  async updateUserRole(userId: string, role: string) {
    const response = await api.put(`/users/${userId}/role`, { role });
    return response.data;
  },

  // 删除用户
  async deleteUser(userId: string) {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },

  // 获取当前用户
  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 更新用户信息
  async updateUser(userId: string, data: any) {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  },

  // 更新用户设置
  async updateUserSettings(settings: any) {
    const response = await api.put('/users/me/settings', settings);
    return response.data;
  },

  // 更改密码
  async changePassword(currentPassword: string, newPassword: string) {
    const response = await api.put('/users/me/password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  // 生成API密钥
  async generateApiKey() {
    const response = await api.post('/users/me/api-key/generate');
    return response.data;
  },

  // 撤销API密钥
  async revokeApiKey() {
    const response = await api.post('/users/me/api-key/revoke');
    return response.data;
  }
};

// WebSocket连接管理
class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(path: string = '/ws') {
    const token = localStorage.getItem('auth_token');
    const wsUrl = API_BASE_URL.replace('http', 'ws') + path + `?token=${token}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('WebSocket消息解析失败:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket连接已关闭');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      // 限制最大重连延迟为30秒
      const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, 30000);
      setTimeout(() => {
        console.log(`尝试重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }

  private handleMessage(data: any) {
    // 处理实时消息
    switch (data.type) {
      case 'generation_progress':
        // 处理生成进度更新
        window.dispatchEvent(new CustomEvent('generation_progress', { detail: data }));
        break;
      case 'agent_status':
        // 处理代理状态更新
        window.dispatchEvent(new CustomEvent('agent_status', { detail: data }));
        break;
      case 'system_alert':
        // 处理系统警告
        window.dispatchEvent(new CustomEvent('system_alert', { detail: data }));
        break;
      default:
        console.log('未知WebSocket消息类型:', data.type);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const wsManager = new WebSocketManager();

// 工具函数
export const apiUtils = {
  // 设置认证令牌
  setAuthToken(token: string) {
    authToken = token;
    localStorage.setItem('auth_token', token);
  },

  // 清除认证令牌
  clearAuthToken() {
    authToken = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  // 获取认证令牌
  getAuthToken() {
    return localStorage.getItem('auth_token');
  },

  // 检查是否已认证
  isAuthenticated() {
    return !!authToken;
  },

  // 获取当前用户
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('解析用户数据失败:', error);
      localStorage.removeItem('user');
      return null;
    }
  }
};

// 错误处理工具
export const handleApiError = (error: any) => {
  if (error.response) {
    // 服务器响应错误
    const status = error.response.status;
    const message = error.response.data?.detail || error.response.data?.message || '请求失败';
    
    return {
      status,
      message,
      data: error.response.data
    };
  } else if (error.request) {
    // 网络错误
    return {
      status: 0,
      message: '网络连接失败，请检查网络设置',
      data: null
    };
  } else {
    // 其他错误
    return {
      status: 'unknown',
      message: error.message || '未知错误',
      data: null
    };
  }
};

export default api;