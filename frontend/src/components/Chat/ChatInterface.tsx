import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, BookOpen, Layout, CheckSquare, Square } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import { createConversation, getConversationHistory, listDocuments } from '../../services/api';
import type { Message, Document } from '../../types';
import { auth } from '../../config/firebase';
import { useNavigate } from 'react-router-dom';

interface ChatInterfaceProps {
  initialDocumentIds?: string[];
  conversationId?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ initialDocumentIds, conversationId }) => {
  const assistantName = 'DocuNova';
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversationId || null);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>(() => {
    const saved = localStorage.getItem('selectedDocumentIds');
    if (initialDocumentIds && initialDocumentIds.length > 0) return initialDocumentIds;
    return saved ? JSON.parse(saved) : [];
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const [citationStyle, setCitationStyle] = useState<'default' | 'apa' | 'mla'>('default');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync selected docs to localStorage
  useEffect(() => {
    localStorage.setItem('selectedDocumentIds', JSON.stringify(selectedDocumentIds));
  }, [selectedDocumentIds]);

  // Load conversation history if ID is selected
  const { data: historyData } = useQuery({
    queryKey: ['conversation', currentConversationId],
    queryFn: () => currentConversationId ? getConversationHistory(currentConversationId) : null,
    enabled: !!currentConversationId && isAuthenticated,
  });

  const { data: documents } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: listDocuments,
    enabled: isAuthenticated,
  });

  useEffect(() => {
    if (historyData?.messages) {
      setMessages(historyData.messages);
    } else if (!currentConversationId) {
      setMessages([]);
    }
  }, [historyData, currentConversationId]);

  const handleStreamingQuery = async (text: string) => {
    let convId = currentConversationId;
    setIsStreaming(true);

    try {
      // 1. Auto-create conversation if missing
      if (!convId) {
        const newConv = await createConversation(text.slice(0, 30) + '...');
        convId = newConv.id;
        setCurrentConversationId(convId);
        queryClient.invalidateQueries({ queryKey: ['conversations'] });
      }

      // 2. Prepare assistant message placeholder
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // 3. Start streaming fetch
      const token = (await auth.currentUser?.getIdToken()) || localStorage.getItem('token');
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiBaseUrl}/api/v1/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question: text,
          document_ids: selectedDocumentIds,
          conversation_id: convId
        })
      });

      if (!response.ok) throw new Error('Streaming failed');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          fullContent += chunk;

          // Update the last message in real-time
          setMessages(prev => {
            const next = [...prev];
            next[next.length - 1] = { ...next[next.length - 1], content: fullContent };
            return next;
          });
        }
      }

      // Finalize history on finish
      queryClient.invalidateQueries({ queryKey: ['conversation', convId] });

    } catch (err) {
      console.error('Streaming error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I encountered an error while streaming the response.'
      }]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    handleStreamingQuery(input);
    setInput('');
  };


  const toggleDocument = (docId: string) => {
    setSelectedDocumentIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const selectAllDocuments = () => {
    const completed = (documents || []).filter((d) => d.status === 'completed').map((d) => d.id);
    setSelectedDocumentIds(completed);
  };

  const clearSelectedDocuments = () => setSelectedDocumentIds([]);

  const formatCitation = (source: { filename: string; page?: number }) => {
    const pageText = source.page ? `${source.page}` : 'n.d.';
    if (citationStyle === 'apa') return `${source.filename} (p. ${pageText})`;
    if (citationStyle === 'mla') return `${source.filename}, p. ${pageText}`;
    return `${source.filename}${source.page ? ` (p. ${source.page})` : ''}`;
  };

  const viewSourceInDocument = (source: { document_id?: string; chunk_text?: string }) => {
    if (!source.document_id) return;
    navigate('/documents', {
      state: {
        focusDocumentId: source.document_id,
        focusSnippet: source.chunk_text || '',
      },
    });
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  return (
    <div className="flex h-full bg-[var(--docu-bg)] overflow-hidden">
      {/* Messages Area */}
      <div className="flex-1 flex flex-col h-full relative">

        {/* Workspace Header */}
        <header className="h-14 border-b border-[var(--docu-border)] flex items-center justify-between px-6 bg-[var(--docu-bg)]/80 backdrop-blur-sm z-10">
          <div className="flex items-center gap-3">
            <Layout className="w-5 h-5 text-[var(--docu-text-secondary)]" />
            <h1 className="text-sm font-medium text-[var(--docu-text-main)]">
              {currentConversationId ? 'Chat Interaction' : 'New Chat'}
            </h1>
          </div>
        </header>

        <div className="px-6 py-2 border-b border-[var(--docu-border)] bg-[var(--docu-bg)] flex items-center gap-2">
          <span className="text-[11px] uppercase tracking-wide text-[var(--docu-text-secondary)]">Citation style</span>
          <select
            value={citationStyle}
            onChange={(e) => setCitationStyle(e.target.value as 'default' | 'apa' | 'mla')}
            className="text-xs rounded border border-[var(--docu-border)] bg-[var(--docu-bg)] text-[var(--docu-text-main)] px-2 py-1"
          >
            <option value="default">Default</option>
            <option value="apa">APA</option>
            <option value="mla">MLA</option>
          </select>
        </div>

        {/* Selected Context Bar */}
        {selectedDocumentIds.length > 0 && (
          <div className="px-6 py-2 bg-[var(--docu-sidebar)]/50 border-b border-[var(--docu-border)] flex items-center gap-3 overflow-x-auto">
            <BookOpen className="w-4 h-4 text-[var(--docu-accent)] shrink-0" />
            <div className="flex gap-2">
              {selectedDocumentIds.map(id => (
                <span key={id} className="text-[10px] uppercase tracking-wider font-semibold text-[var(--docu-text-secondary)] bg-[var(--docu-bg)] border border-[var(--docu-border)] px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
                  {id.slice(0, 8)}...
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Document Selector */}
        <div className="px-6 py-2 border-b border-[var(--docu-border)] bg-[var(--docu-bg)]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] uppercase tracking-wide text-[var(--docu-text-secondary)] font-semibold">
              Context Documents
            </span>
            <div className="flex gap-2">
              <button
                onClick={selectAllDocuments}
                className="text-[11px] px-2 py-1 rounded border border-[var(--docu-border)] text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)]"
              >
                Chat with all
              </button>
              <button
                onClick={clearSelectedDocuments}
                className="text-[11px] px-2 py-1 rounded border border-[var(--docu-border)] text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)]"
              >
                Clear
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 max-h-20 overflow-auto">
            {(documents || [])
              .filter((d) => d.status === 'completed')
              .map((doc) => {
                const selected = selectedDocumentIds.includes(doc.id);
                return (
                  <button
                    key={doc.id}
                    onClick={() => toggleDocument(doc.id)}
                    className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs border ${selected
                      ? 'border-[var(--docu-accent)] text-[var(--docu-text-main)] bg-[var(--docu-sidebar)]'
                      : 'border-[var(--docu-border)] text-[var(--docu-text-secondary)]'
                      }`}
                    title={doc.filename}
                  >
                    {selected ? <CheckSquare className="w-3.5 h-3.5" /> : <Square className="w-3.5 h-3.5" />}
                    <span className="max-w-[200px] truncate">{doc.filename}</span>
                  </button>
                );
              })}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-8 space-y-10">
          <div className="max-w-3xl mx-auto space-y-10">
            {messages.length === 0 && !isStreaming && (
              <div className="h-[60vh] flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-[var(--docu-sidebar)] flex items-center justify-center border border-[var(--docu-border)]">
                  <Bot className="w-6 h-6 text-[var(--docu-accent)]" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-xl font-medium text-[var(--docu-text-main)]">How can I help you today?</h2>
                  <p className="text-sm text-[var(--docu-text-secondary)] max-w-sm">
                    Ask me anything about your uploaded documents. I'll provide detailed answers with citations.
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg, index) => (
              <div key={index} className="group animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex gap-4 md:gap-6">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border border-[var(--docu-border)] ${msg.role === 'user' ? 'bg-[var(--docu-sidebar)]' : 'bg-transparent'}`}>
                    {msg.role === 'user' ?
                      <User className="w-4 h-4 text-[var(--docu-text-secondary)]" /> :
                      <Bot className="w-5 h-5 text-[var(--docu-accent)]" />
                    }
                  </div>

                  <div className="flex-1 space-y-4 min-w-0">
                    <div className="text-sm font-medium text-[var(--docu-text-secondary)] uppercase tracking-tight">
                      {msg.role === 'user' ? 'You' : assistantName}
                    </div>

                    <div className="text-[var(--docu-text-main)] leading-relaxed text-[15px] prose prose-docu max-w-none">
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>

                    {msg.sources && msg.sources.length > 0 && (
                      <div className="flex flex-wrap gap-2 pt-2">
                        {msg.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="bg-[var(--docu-sidebar)] border border-[var(--docu-border)] rounded-md px-2.5 py-1.5 text-xs text-[var(--docu-text-secondary)] hover:border-[var(--docu-accent)] transition-colors"
                            title={source.chunk_text}
                          >
                            <div className="flex items-center gap-2">
                              <BookOpen className="w-3.5 h-3.5" />
                              <span className="max-w-[240px] truncate">{formatCitation(source)}</span>
                            </div>
                            {source.chunk_text && (
                              <p className="mt-1 max-w-[280px] truncate text-[10px] opacity-80">
                                {source.chunk_text}
                              </p>
                            )}
                            <div className="mt-1">
                              <button
                                onClick={() => viewSourceInDocument(source)}
                                disabled={!source.document_id}
                                className="text-[10px] underline underline-offset-2 text-[var(--docu-accent)] disabled:opacity-50"
                              >
                                View in document
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isStreaming && (!messages[messages.length - 1] || messages[messages.length - 1].role !== 'assistant' || !messages[messages.length - 1].content) && (
              <div className="flex gap-4 md:gap-6 animate-pulse">
                <div className="w-8 h-8 rounded-lg border border-[var(--docu-border)] flex items-center justify-center">
                  <Loader2 className="w-4 h-4 text-[var(--docu-accent)] animate-spin" />
                </div>
                <div className="flex-1 space-y-4">
                  <div className="text-sm font-medium text-[var(--docu-text-secondary)] uppercase tracking-tight">{assistantName}</div>
                  <div className="h-4 bg-[var(--docu-sidebar)] rounded w-3/4"></div>
                  <div className="h-4 bg-[var(--docu-sidebar)] rounded w-1/2"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="pb-8 pt-4 px-4 bg-gradient-to-t from-[var(--docu-bg)] via-[var(--docu-bg)] to-transparent">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="relative group">
              <textarea
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder={`Message ${assistantName}...`}
                className="w-full bg-white dark:bg-[var(--docu-sidebar)] border border-[var(--docu-border)] rounded-2xl pl-4 pr-12 py-4 focus:ring-1 focus:ring-[var(--docu-accent)] focus:border-[var(--docu-accent)] outline-none shadow-sm transition-all resize-none min-h-[56px] text-[15px]"
                disabled={isStreaming}
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="absolute right-3 bottom-3 p-2 bg-[var(--docu-accent)] text-white rounded-xl hover:opacity-90 disabled:opacity-30 disabled:grayscale transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <p className="mt-2 text-[10px] text-center text-[var(--docu-text-secondary)]">
              {assistantName} may provide inaccurate information. Always verify citations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
