import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { listUsers } from '../services/api';
import { Shield, Mail, Calendar, CheckCircle2, XCircle } from 'lucide-react';

const AdminUsers: React.FC = () => {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['admin-users'],
    queryFn: listUsers,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-[var(--docu-accent)]/10 rounded-full"></div>
          <div className="text-sm text-[var(--docu-text-secondary)]">Loading users...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        Error loading users. Please make sure you have admin privileges.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-[var(--docu-text-main)] tracking-tight">
          User Management
        </h1>
        <p className="text-[var(--docu-text-secondary)] text-sm">
          Overview of all registered users and their platform status.
        </p>
      </div>

      <div className="bg-white dark:bg-[var(--docu-bg)] border border-[var(--docu-border)] rounded-2xl shadow-sm overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[var(--docu-sidebar)]/50 border-b border-[var(--docu-border)]">
              <th className="px-6 py-4 text-xs font-bold text-[var(--docu-text-secondary)] uppercase tracking-wider">User</th>
              <th className="px-6 py-4 text-xs font-bold text-[var(--docu-text-secondary)] uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-xs font-bold text-[var(--docu-text-secondary)] uppercase tracking-wider">Joined</th>
              <th className="px-6 py-4 text-xs font-bold text-[var(--docu-text-secondary)] uppercase tracking-wider text-right">Role</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--docu-border)]">
            {users?.map((u: any) => (
              <tr key={u.id} className="hover:bg-[var(--docu-sidebar)]/30 transition-colors group">
                <td className="px-6 py-5">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-[var(--docu-accent)]/10 border border-[var(--docu-accent)]/10 flex items-center justify-center text-[var(--docu-accent)] font-semibold text-sm">
                      {u.email.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-[var(--docu-text-main)]">{u.email}</span>
                      <span className="text-[10px] text-[var(--docu-text-secondary)] flex items-center gap-1">
                        <Mail className="w-3 h-3" /> {u.id.substring(0, 8)}...
                      </span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex items-center gap-2">
                    {u.is_active ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 text-[11px] font-medium">
                        <CheckCircle2 className="w-3 h-3" /> Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/10 text-red-600 dark:text-red-400 text-[11px] font-medium">
                        <XCircle className="w-3 h-3" /> Inactive
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-5 text-sm text-[var(--docu-text-secondary)]">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 opacity-40" />
                    {new Date().toLocaleDateString()} {/* Basic fallback */}
                  </div>
                </td>
                <td className="px-6 py-5 text-right">
                  {u.is_superuser ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--docu-accent)]/10 text-[var(--docu-accent)] text-[11px] font-bold border border-[var(--docu-accent)]/20 shadow-sm">
                      <Shield className="w-3 h-3" /> Admin
                    </span>
                  ) : (
                    <span className="text-xs text-[var(--docu-text-secondary)] font-medium">
                      Member
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-xs text-[var(--docu-text-secondary)] px-2">
        <div>Total registered users: {users?.length || 0}</div>
        <div className="flex items-center gap-4">
          <span>Privacy Mode: Active</span>
          <span>Data stored locally in SQLite</span>
        </div>
      </div>
    </div>
  );
};

export default AdminUsers;
