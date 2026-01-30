import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  BookOpen, 
  FolderOpen, 
  Bot, 
  Settings, 
  Activity,
  PenTool,
  BarChart3
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: '仪表盘', href: '/', icon: LayoutDashboard },
  { name: '小说编辑器', href: '/editor', icon: PenTool },
  { name: '项目管理', href: '/projects', icon: FolderOpen },
  { name: 'AI代理监控', href: '/agents', icon: Bot },
  { name: '质量分析', href: '/analytics', icon: BarChart3 },
  { name: '系统监控', href: '/monitor', icon: Activity },
  { name: '设置', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <div className="w-64 border-r bg-card">
      <nav className="space-y-1 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
            >
              <Icon className="mr-3 h-4 w-4" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};