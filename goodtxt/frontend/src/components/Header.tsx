import React from 'react';
import { Bell, Settings, User } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

export const Header: React.FC = () => {
  return (
    <header className="border-b bg-card">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">GoodTxt</h1>
          <span className="text-sm text-muted-foreground">多AI协同小说生成系统</span>
        </div>
        
        <div className="ml-auto flex items-center space-x-4">
          <Button variant="ghost" size="icon">
            <Bell className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
};