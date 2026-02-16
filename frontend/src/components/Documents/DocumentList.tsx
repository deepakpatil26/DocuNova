import React, { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { listDocuments, deleteDocument } from '../../services/api';
import type { Document } from '../../types';

const DocumentList: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();

  const focusState = useMemo(() => {
    const state = location.state as { focusDocumentId?: string; focusSnippet?: string } | null;
    return {
      focusDocumentId: state?.focusDocumentId || null,
      focusSnippet: state?.focusSnippet || '',
    };
  }, [location.state]);

  const { data: documents, isLoading, error } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: listDocuments,
    refetchInterval: 5000,
    enabled: isAuthenticated,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing': return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-[var(--docu-text-secondary)]" />;
    }
  };

  if (isLoading) return <div className="text-center p-8 text-[var(--docu-text-secondary)] animate-pulse">Loading documents...</div>;
  if (error) return <div className="text-center p-8 text-red-500">Failed to load documents</div>;

  return (
    <div className="docu-card overflow-hidden">
      <div className="p-4 border-b border-[var(--docu-border)] bg-[var(--docu-sidebar)]/50">
        <h3 className="text-sm font-semibold text-[var(--docu-text-main)] uppercase tracking-tight">Documents Library</h3>
      </div>

      {documents?.length === 0 ? (
        <div className="p-12 text-center text-[var(--docu-text-secondary)] italic text-sm">
          No documents uploaded yet.
        </div>
      ) : (
        <ul className="divide-y divide-[var(--docu-border)]">
          {documents?.map((doc) => (
            <li
              key={doc.id}
              className={`p-4 transition-colors flex items-center justify-between group ${
                focusState.focusDocumentId === doc.id
                  ? 'bg-[var(--docu-sidebar)] border-l-4 border-[var(--docu-accent)]'
                  : 'hover:bg-[var(--docu-sidebar)]/30'
              }`}
            >
              <div className="flex items-center gap-4">
                <div className="p-2.5 bg-white dark:bg-[var(--docu-sidebar)] border border-[var(--docu-border)] text-[var(--docu-accent)] rounded-xl shadow-sm">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-medium text-[var(--docu-text-main)] text-[15px]">{doc.filename}</p>
                  <div className="flex items-center gap-2 text-[11px] text-[var(--docu-text-secondary)] mt-1 font-medium">
                    <span className="uppercase tracking-wide">{(doc.file_size / 1024).toFixed(1)} KB</span>
                    <span className="opacity-30">•</span>
                    <span className="flex items-center gap-1.5">
                      {getStatusIcon(doc.status)}
                      <span className="capitalize">{doc.status}</span>
                    </span>
                    {doc.chunk_count > 0 && (
                      <>
                        <span className="opacity-30">•</span>
                        <span>{doc.chunk_count} chunks</span>
                      </>
                    )}
                  </div>
                  {focusState.focusDocumentId === doc.id && focusState.focusSnippet && (
                    <p className="mt-2 text-[11px] text-[var(--docu-text-secondary)] max-w-xl truncate">
                      Matched snippet: {focusState.focusSnippet}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                {doc.status === 'completed' && (
                  <button
                    onClick={() => navigate('/chat', { state: { documentIds: [doc.id] } })}
                    className="flex items-center gap-2 px-4 py-2 bg-[var(--btn-secondary-bg)] border border-[var(--docu-border)] text-[var(--btn-secondary-text)] text-xs font-semibold rounded-xl hover:bg-[var(--docu-sidebar)] transition-all shadow-sm active:scale-95"
                  >
                    Chat
                  </button>
                )}

                <button
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this document?')) {
                      deleteMutation.mutate(doc.id);
                    }
                  }}
                  className="p-2 text-[var(--docu-text-secondary)] hover:text-red-500 transition-colors rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
                  title="Delete document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentList;
