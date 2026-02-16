import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle';
import { PanelLeftOpen } from 'lucide-react';

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobile, setIsMobile] = useState<boolean>(() =>
    typeof window !== 'undefined' ? window.innerWidth < 768 : false
  );
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved === '1';
  });
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', isSidebarCollapsed ? '1' : '0');
  }, [isSidebarCollapsed]);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    if (!isMobile) setIsMobileSidebarOpen(false);
  }, [isMobile]);

  const searchParams = new URLSearchParams(location.search);
  const currentConversationId = searchParams.get('id');

  const handleSelectConversation = (id: string) => {
    navigate(`/chat?id=${id}`);
    if (isMobile) setIsMobileSidebarOpen(false);
  };

  const handleNewChat = () => {
    navigate('/chat');
    if (isMobile) setIsMobileSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-[var(--docu-bg)] text-[var(--docu-text-main)] overflow-hidden">
      <Sidebar
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
        isMobile={isMobile}
        isMobileOpen={isMobileSidebarOpen}
        onMobileClose={() => setIsMobileSidebarOpen(false)}
      />

      {isMobile && isMobileSidebarOpen && (
        <button
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setIsMobileSidebarOpen(false)}
          aria-label="Close sidebar overlay"
        />
      )}

      <main className="flex-1 overflow-auto relative">
        {/* Top Control Layer (Floating) */}
        <div className="fixed top-4 left-4 right-4 z-30 pointer-events-none flex items-start justify-between">
          <button
            onClick={() => setIsMobileSidebarOpen(true)}
            className="md:hidden pointer-events-auto inline-flex items-center justify-center w-10 h-10 rounded-full border border-[var(--docu-border)] bg-[var(--docu-bg)]/80 backdrop-blur-md text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)] shadow-lg transition-all active:scale-95"
            aria-label="Open sidebar"
          >
            <PanelLeftOpen className="w-5 h-5" />
          </button>

          <div className="flex-1" /> {/* Spacer */}

          <div className="pointer-events-auto">
            <ThemeToggle />
          </div>
        </div>

        <div className="h-full w-full pt-4 md:pt-0">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
