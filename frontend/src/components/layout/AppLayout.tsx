import React from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';

interface AppLayoutProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  systemStatus: string;
  version: string;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentTab,
  onSelectTab,
  systemStatus,
  version,
  children,
}) => {
  return (
    <div className="app-container">
      <Sidebar currentTab={currentTab} onSelectTab={onSelectTab} />
      <div className="main-content">
        <Header systemStatus={systemStatus} version={version} />
        <main className="page-body">{children}</main>
        <Footer />
      </div>
    </div>
  );
};
