import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Bot, User, BookOpen } from 'lucide-react';
import { getSharedConversation } from '../services/api';
import type { Message } from '../types';

const SharedConversation: React.FC = () => {
  const { token } = useParams();

  const { data, isLoading, error } = useQuery({
    queryKey: ['shared-conversation', token],
    queryFn: () => getSharedConversation(token || ''),
    enabled: !!token,
    retry: false,
  });

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-[var(--docu-text-secondary)]">Loading shared conversation...</div>;
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 text-center px-6">
        <h1 className="text-2xl font-semibold text-[var(--docu-text-main)]">Shared conversation unavailable</h1>
        <p className="text-[var(--docu-text-secondary)]">The share link may be invalid or expired.</p>
        <Link to="/login" className="text-[var(--docu-accent)] font-semibold">Go to Login</Link>
      </div>
    );
  }

  const messages: Message[] = data.messages || [];

  return (
    <div className="min-h-screen bg-[var(--docu-bg)] px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold text-[var(--docu-text-main)] mb-1">{data.title || 'Shared Conversation'}</h1>
        <p className="text-sm text-[var(--docu-text-secondary)] mb-8">Read-only shared chat</p>

        <div className="space-y-8">
          {messages.map((msg, i) => (
            <div key={i} className="flex gap-4">
              <div className="w-8 h-8 rounded-lg border border-[var(--docu-border)] flex items-center justify-center">
                {msg.role === 'user' ? (
                  <User className="w-4 h-4 text-[var(--docu-text-secondary)]" />
                ) : (
                  <Bot className="w-4 h-4 text-[var(--docu-accent)]" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-xs uppercase tracking-wide text-[var(--docu-text-secondary)] mb-2">
                  {msg.role === 'user' ? 'User' : 'Assistant'}
                </div>
                <p className="text-[var(--docu-text-main)] whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.sources.map((source, idx) => (
                      <div key={idx} className="text-xs border border-[var(--docu-border)] rounded px-2 py-1 bg-[var(--docu-sidebar)] text-[var(--docu-text-secondary)]">
                        <BookOpen className="w-3 h-3 inline mr-1" />
                        {source.filename}
                        {source.page ? ` (p. ${source.page})` : ''}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SharedConversation;
