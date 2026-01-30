// 类型定义
export interface NovelProject {
  id: string;
  title: string;
  description: string;
  genre: string;
  status: 'draft' | 'generating' | 'completed' | 'archived';
  createdAt: Date;
  updatedAt: Date;
  chapterCount: number;
  wordCount: number;
  aiAgents: string[];
}

export interface Chapter {
  id: string;
  title: string;
  content: string;
  wordCount: number;
  status: 'pending' | 'generating' | 'completed' | 'reviewing';
  aiAgent: string;
  createdAt: Date;
  updatedAt: Date;
  quality: {
    coherence: number;
    grammar: number;
    creativity: number;
  };
}

export interface AIAgent {
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
  };
}

export interface SystemStatus {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  activeConnections: number;
  uptime: string;
  lastUpdate: Date;
}

export interface GenerationSettings {
  targetWordCount: number;
  style: string;
  tone: string;
  complexity: 'simple' | 'medium' | 'complex';
  includeDialogue: boolean;
  includeDescription: boolean;
  modelConfig: {
    coordinator: string;
    writer: string;
    editor: string;
  };
}

export interface QualityMetrics {
  overall: number;
  readability: number;
  coherence: number;
  creativity: number;
  grammar: number;
  consistency: number;
  engagement: number;
}