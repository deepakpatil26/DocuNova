import React, { useMemo, useState } from 'react';
import {
  MessageSquare,
  Plus,
  Trash2,
  Library,
  Users,
  Search,
  Download,
  Link as LinkIcon,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  Zap,
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listConversations,
  deleteConversation,
  exportConversation,
  createConversationShareLink,
} from '../../services/api';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import TokenUsageModal from '../TokenUsageModal';

interface SidebarProps {
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobile: boolean;
  isMobileOpen: boolean;
  onMobileClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentConversationId,
  onSelectConversation,
  onNewChat,
  isCollapsed,
  onToggleCollapse,
  isMobile,
  isMobileOpen,
  onMobileClose,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  const [search, setSearch] = useState('');
  const [isTokenModalOpen, setIsTokenModalOpen] = useState(false);

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations', search],
    queryFn: () => listConversations(search || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      if (currentConversationId) onNewChat();
    },
  });

  const navBase = useMemo(
    () =>
      `w-full flex items-center ${(isCollapsed && !isMobile) ? 'justify-center px-2' : 'gap-3 px-3'} py-2 rounded-lg text-sm font-medium transition-colors`,
    [isCollapsed, isMobile]
  );

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userInitial = user?.email?.charAt(0).toUpperCase() || 'U';

  const handleExport = async (conversationId: string) => {
    const blob = await exportConversation(conversationId, 'md');
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-${conversationId}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleShare = async (conversationId: string) => {
    const data = await createConversationShareLink(conversationId);
    const shareUrl = `${window.location.origin}/shared/${data.share_token}`;
    await navigator.clipboard.writeText(shareUrl);
    alert('Share link copied to clipboard');
  };

  return (
    <aside
      className={`fixed md:relative inset-y-0 left-0 ${(isCollapsed && !isMobile) ? 'md:w-20' : 'md:w-64'} w-72 max-w-[88vw] docu-sidebar h-full flex flex-col z-40 transition-transform md:transition-all duration-300 ${isMobile ? (isMobileOpen ? 'translate-x-0' : '-translate-x-full') : 'translate-x-0'}`}
    >
      <div className="p-4 space-y-4 flex-1 flex flex-col overflow-hidden">
        <Link
          to="/"
          className={`flex items-center ${(isCollapsed && !isMobile) ? 'justify-center' : 'gap-3 px-1'} py-1 rounded-lg hover:bg-[var(--docu-bg)] transition-colors`}
          title="Go to Home"
          onClick={() => isMobile && onMobileClose()}
        >
          <div className="w-9 h-9 rounded-lg bg-[var(--docu-bg)] border border-[var(--docu-border)] shadow-sm flex items-center justify-center overflow-hidden shrink-0">
            <img src="/docunova-logo.png" alt="DocuNova logo" className="w-7 h-7 object-contain" />
          </div>
          {!(isCollapsed && !isMobile) && (
            <div className="min-w-0">
              <div className="text-sm font-semibold text-[var(--docu-text-main)] leading-tight">DocuNova</div>
              <div className="text-[10px] uppercase tracking-widest text-[var(--docu-text-secondary)]">AI Workspace</div>
            </div>
          )}
        </Link>

        <button
          onClick={() => {
            onNewChat();
            if (isMobile) onMobileClose();
          }}
          className={`w-full flex items-center ${(isCollapsed && !isMobile) ? 'justify-center px-2' : 'gap-3 px-4'} py-2 bg-white dark:bg-[var(--docu-bg)] border border-[var(--docu-border)] rounded-xl text-sm font-medium hover:bg-[var(--docu-sidebar)] transition-all shadow-sm group`}
          title="New Chat"
        >
          <Plus className="w-4 h-4 text-[var(--docu-accent)] group-hover:scale-110 transition-transform" />
          {!(isCollapsed && !isMobile) && 'New Chat'}
        </button>

        <nav className="space-y-1">
          <Link
            to="/documents"
            className={`${navBase} ${location.pathname === '/documents'
              ? 'bg-[var(--docu-bg)] text-[var(--docu-text-main)] shadow-sm border border-[var(--docu-border)]'
              : 'text-[var(--docu-text-secondary)] hover:bg-[var(--docu-bg)]'
              }`}
            title="Library"
            onClick={() => isMobile && onMobileClose()}
          >
            <Library className="w-4 h-4 shrink-0" />
            {!(isCollapsed && !isMobile) && 'Library'}
          </Link>
          <Link
            to="/chat"
            className={`${navBase} ${location.pathname === '/chat' && !currentConversationId
              ? 'bg-[var(--docu-bg)] text-[var(--docu-text-main)] shadow-sm border border-[var(--docu-border)]'
              : 'text-[var(--docu-text-secondary)] hover:bg-[var(--docu-bg)]'
              }`}
            title="Current Chat"
            onClick={() => isMobile && onMobileClose()}
          >
            <MessageSquare className="w-4 h-4 shrink-0" />
            {!(isCollapsed && !isMobile) && 'Current Chat'}
          </Link>

          {user?.is_superuser && (
            <Link
              to="/admin/users"
              className={`${navBase} ${location.pathname === '/admin/users'
                ? 'bg-[var(--docu-bg)] text-[var(--docu-text-main)] shadow-sm border border-[var(--docu-border)]'
                : 'text-[var(--docu-text-secondary)] hover:bg-[var(--docu-bg)]'
                }`}
              title="Team"
              onClick={() => isMobile && onMobileClose()}
            >
              <Users className="w-4 h-4 shrink-0" />
              {!(isCollapsed && !isMobile) && 'Team'}
            </Link>
          )}
        </nav>

        {!(isCollapsed && !isMobile) && (
          <div className="flex-1 overflow-y-auto space-y-4 pt-4">
            <div className="text-[10px] font-bold text-[var(--docu-text-secondary)] uppercase tracking-widest px-3">
              Recents
            </div>
            <div className="px-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--docu-text-secondary)]" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search conversations"
                  className="w-full pl-8 pr-2 py-1.5 rounded-md border border-[var(--docu-border)] bg-[var(--docu-bg)] text-xs text-[var(--docu-text-main)]"
                />
              </div>
            </div>

            <div className="space-y-0.5">
              {isLoading ? (
                <div className="px-3 py-2 text-xs text-[var(--docu-text-secondary)] animate-pulse">Loading history...</div>
              ) : conversations?.map((conv: any) => (
                <div
                  key={conv.id}
                  className={`group flex items-center gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${currentConversationId === conv.id
                    ? 'bg-[var(--docu-bg)] text-[var(--docu-text-main)] border border-[var(--docu-border)] shadow-sm'
                    : 'text-[var(--docu-text-secondary)] hover:bg-[var(--docu-bg)]'
                    }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="flex-1 truncate">{conv.title || 'Untitled Chat'}</div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExport(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-[var(--docu-accent)] transition-all"
                    title="Export"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleShare(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-[var(--docu-accent)] transition-all"
                    title="Copy share link"
                  >
                    <LinkIcon className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Delete this conversation?')) deleteMutation.mutate(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all"
                    title="Delete"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-[var(--docu-border)] space-y-3">
        {/* Token Usage Button */}
        {!(isCollapsed && !isMobile) && (
          <button
            onClick={() => setIsTokenModalOpen(true)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border border-[var(--docu-border)] text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)] hover:bg-[var(--docu-bg)] hover:border-[var(--docu-accent)]/30 transition-all group"
            title="View token usage"
          >
            <Zap className="w-4 h-4 text-[var(--docu-accent)] group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium">Token Usage</span>
          </button>
        )}

        <div className={`flex items-center ${(isCollapsed && !isMobile) ? 'justify-center' : 'gap-3 px-3'} py-2 rounded-lg hover:bg-[var(--docu-bg)] transition-colors group relative`}>
          <div className="w-8 h-8 rounded-lg bg-[var(--docu-accent)]/10 border border-[var(--docu-accent)]/20 flex items-center justify-center text-[var(--docu-accent)] font-bold text-xs uppercase shrink-0">
            {userInitial}
          </div>
          {!(isCollapsed && !isMobile) && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-[var(--docu-text-main)] truncate">
                {user?.email?.split('@')[0] || 'User'}
              </div>
              <div className="text-[10px] text-[var(--docu-text-secondary)] uppercase tracking-tighter truncate">
                {user?.email || 'Anonymous'}
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="p-1 hover:bg-red-50 hover:text-red-500 rounded-md transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4 text-[var(--docu-text-secondary)] group-hover:text-red-400 transition-colors" />
          </button>
        </div>

        <button
          onClick={isMobile ? onMobileClose : onToggleCollapse}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-lg border border-[var(--docu-border)] text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)] hover:bg-[var(--docu-bg)] transition-colors"
          title={isMobile ? 'Close sidebar' : (isCollapsed ? 'Open sidebar' : 'Close sidebar')}
        >
          {isMobile ? <PanelLeftClose className="w-4 h-4" /> : (isCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />)}
          {!(isCollapsed && !isMobile) && <span className="text-xs">{isMobile ? 'Close' : 'Collapse'}</span>}
        </button>
      </div>

      {/* Token Usage Modal */}
      <TokenUsageModal isOpen={isTokenModalOpen} onClose={() => setIsTokenModalOpen(false)} />
    </aside>
  );
};

export default Sidebar;
