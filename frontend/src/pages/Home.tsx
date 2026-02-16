import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getStats } from '../services/api';
import type { Stats } from '../types';
import {
  FileText,
  MessagesSquare,
  MessageCircle,
  Sparkles,
  Upload,
  Bot,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Layers,
  Clock3,
  Search,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const { user } = useAuth();

  const { data: stats } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: getStats,
    refetchInterval: 10000,
  });

  const isAdmin = Boolean(user?.is_superuser || user?.email === 'admin@gmail.com');

  return (
    <div className="min-h-screen bg-[var(--docu-bg)] px-6 py-10 md:py-14">
      <div className="max-w-6xl mx-auto">
        <section className="relative overflow-hidden rounded-3xl border border-[var(--docu-border)] p-8 md:p-12 mb-8 bg-gradient-to-br from-[var(--docu-sidebar)] via-[var(--docu-bg)] to-[var(--docu-bg)]">
          <div className="absolute -top-20 -right-16 w-72 h-72 bg-[var(--docu-accent)]/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-20 -left-16 w-64 h-64 bg-[var(--docu-accent)]/5 rounded-full blur-3xl" />

          <div className="relative grid grid-cols-1 lg:grid-cols-3 gap-8 items-end">
            <div className="lg:col-span-2">
              <div className="inline-flex items-center gap-2 rounded-full border border-[var(--docu-border)] px-3 py-1 text-xs text-[var(--docu-text-secondary)] mb-4 bg-[var(--docu-bg)]/80">
                <Sparkles className="w-3.5 h-3.5 text-[var(--docu-accent)]" />
                Built for reliable document intelligence
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-[var(--docu-text-main)] leading-tight mb-4">
                Turn messy documents into
                <span className="text-[var(--docu-accent)]"> clear answers</span>
              </h1>
              <p className="text-base md:text-lg text-[var(--docu-text-secondary)] max-w-2xl mb-6">
                Upload files, ask questions, and get grounded responses with citations you can verify in seconds.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link
                  to="/documents"
                  className="inline-flex items-center gap-2 px-5 py-3 bg-[var(--btn-primary-bg)] text-[var(--btn-primary-text)] rounded-xl hover:opacity-90 transition"
                >
                  Upload your first file
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/chat"
                  className="inline-flex items-center gap-2 px-5 py-3 bg-[var(--btn-secondary-bg)] text-[var(--btn-secondary-text)] border border-[var(--docu-border)] rounded-xl hover:bg-[var(--docu-sidebar)] transition"
                >
                  Explore workspace
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="docu-card p-4">
                <div className="text-xs text-[var(--docu-text-secondary)] mb-1">Documents</div>
                <div className="text-2xl font-semibold text-[var(--docu-text-main)]">{stats?.documents ?? 0}</div>
              </div>
              <div className="docu-card p-4">
                <div className="text-xs text-[var(--docu-text-secondary)] mb-1">Conversations</div>
                <div className="text-2xl font-semibold text-[var(--docu-text-main)]">{stats?.conversations ?? 0}</div>
              </div>
              <div className="docu-card p-4 col-span-2">
                <div className="text-xs text-[var(--docu-text-secondary)] mb-1">Messages answered</div>
                <div className="text-2xl font-semibold text-[var(--docu-text-main)]">{stats?.messages ?? 0}</div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="docu-card p-5">
            <div className="flex items-center gap-2 text-[var(--docu-text-main)] font-semibold mb-2">
              <Upload className="w-4 h-4 text-[var(--docu-accent)]" /> Upload Fast
            </div>
            <p className="text-sm text-[var(--docu-text-secondary)]">Add PDFs, TXT, or Markdown and start querying within moments.</p>
          </div>
          <div className="docu-card p-5">
            <div className="flex items-center gap-2 text-[var(--docu-text-main)] font-semibold mb-2">
              <Search className="w-4 h-4 text-[var(--docu-accent)]" /> Cite Precisely
            </div>
            <p className="text-sm text-[var(--docu-text-secondary)]">Every answer is tied to source snippets for quick verification.</p>
          </div>
          <div className="docu-card p-5">
            <div className="flex items-center gap-2 text-[var(--docu-text-main)] font-semibold mb-2">
              <Layers className="w-4 h-4 text-[var(--docu-accent)]" /> Stay Organized
            </div>
            <p className="text-sm text-[var(--docu-text-secondary)]">Conversations are saved so users can continue where they left off.</p>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="rounded-2xl border border-[var(--docu-border)] p-6 bg-[var(--docu-sidebar)]/40">
            <h2 className="text-lg font-semibold text-[var(--docu-text-main)] mb-3">How it works</h2>
            <div className="space-y-3 text-sm text-[var(--docu-text-secondary)]">
              <div className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Upload one or more documents</div>
              <div className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Ask questions in natural language</div>
              <div className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Review source-backed responses</div>
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--docu-border)] p-6 bg-[var(--docu-bg)]">
            <h2 className="text-lg font-semibold text-[var(--docu-text-main)] mb-3">Designed for teams</h2>
            <div className="space-y-3 text-sm text-[var(--docu-text-secondary)]">
              <div className="flex items-start gap-2"><Clock3 className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Reduce manual reading and repeated Q&A</div>
              <div className="flex items-start gap-2"><MessagesSquare className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Keep context in saved conversations</div>
              <div className="flex items-start gap-2"><FileText className="w-4 h-4 mt-0.5 text-[var(--docu-accent)]" />Handle multiple documents in one workspace</div>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <Link
            to="/documents"
            className="group rounded-2xl border border-[var(--docu-border)] bg-[var(--docu-bg)] p-5 hover:bg-[var(--docu-sidebar)]/60 transition"
          >
            <div className="flex items-center gap-3 mb-2">
              <Upload className="w-5 h-5 text-[var(--docu-accent)]" />
              <span className="font-semibold text-[var(--docu-text-main)]">Quick Upload</span>
            </div>
            <p className="text-sm text-[var(--docu-text-secondary)]">Drop files and start your first knowledge session.</p>
          </Link>

          <Link
            to="/chat"
            className="group rounded-2xl border border-[var(--docu-border)] bg-[var(--docu-bg)] p-5 hover:bg-[var(--docu-sidebar)]/60 transition"
          >
            <div className="flex items-center gap-3 mb-2">
              <Bot className="w-5 h-5 text-[var(--docu-accent)]" />
              <span className="font-semibold text-[var(--docu-text-main)]">Open AI Workspace</span>
            </div>
            <p className="text-sm text-[var(--docu-text-secondary)]">Continue previous threads or launch a new grounded conversation.</p>
          </Link>

          {isAdmin && (
            <Link
              to="/admin/users"
              className="md:col-span-2 group rounded-2xl border border-[var(--docu-border)] bg-[var(--docu-bg)] p-5 hover:bg-[var(--docu-sidebar)]/60 transition"
            >
              <div className="flex items-center gap-3 mb-2">
                <ShieldCheck className="w-5 h-5 text-[var(--docu-accent)]" />
                <span className="font-semibold text-[var(--docu-text-main)]">Admin Control Center</span>
              </div>
              <p className="text-sm text-[var(--docu-text-secondary)]">Review user activity and monitor adoption from one dashboard.</p>
            </Link>
          )}
        </section>

        <section className="text-center py-2">
          <p className="text-xs text-[var(--docu-text-secondary)]">DocuNova gives source-grounded answers, not black-box guesses.</p>
          <div className="flex items-center justify-center gap-6 mt-3 text-[11px] text-[var(--docu-text-secondary)]">
            <span className="inline-flex items-center gap-1"><Sparkles className="w-3.5 h-3.5 text-[var(--docu-accent)]" />Citation-first</span>
            <span className="inline-flex items-center gap-1"><MessageCircle className="w-3.5 h-3.5 text-[var(--docu-accent)]" />Persistent chats</span>
            <span className="inline-flex items-center gap-1"><FileText className="w-3.5 h-3.5 text-[var(--docu-accent)]" />Document grounded</span>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Home;
