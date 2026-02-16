import { useEffect, useState } from 'react';
import { getUsageStats } from '../services/api';
import { X, TrendingUp, Calendar, Zap } from 'lucide-react';

interface UsageStats {
  daily_remaining: number;
  daily_limit: number;
  daily_used: number;
  daily_percentage: number;
  monthly_remaining: number;
  monthly_limit: number;
  monthly_used: number;
  monthly_percentage: number;
  total_used: number;
  total_requests: number;
  resets_in: string;
}

interface TokenUsageModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function TokenUsageModal({ isOpen, onClose }: TokenUsageModalProps) {
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchUsage();
    }
  }, [isOpen]);

  const fetchUsage = async () => {
    try {
      const data = await getUsageStats();
      setUsage(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch usage stats:', error);
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md p-4">
        <div className="bg-[var(--docu-bg)] rounded-2xl shadow-2xl border border-[var(--docu-border)] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[var(--docu-border)]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[var(--docu-accent)]/10 border border-[var(--docu-accent)]/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-[var(--docu-accent)]" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-[var(--docu-text-main)]">Token Usage</h2>
                <p className="text-xs text-[var(--docu-text-secondary)]">Your consumption stats</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-[var(--docu-sidebar)] rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-[var(--docu-text-secondary)]" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {loading || !usage ? (
              <div className="space-y-4">
                <div className="animate-pulse">
                  <div className="h-4 bg-[var(--docu-border)] rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-[var(--docu-border)] rounded"></div>
                </div>
                <div className="animate-pulse">
                  <div className="h-4 bg-[var(--docu-border)] rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-[var(--docu-border)] rounded"></div>
                </div>
              </div>
            ) : (
              <>
                {/* Daily Usage */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-[var(--docu-accent)]" />
                      <span className="text-sm font-semibold text-[var(--docu-text-main)]">
                        Daily Usage
                      </span>
                    </div>
                    <span className="text-xs text-[var(--docu-text-secondary)]">
                      Resets in {usage.resets_in}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold text-[var(--docu-text-main)]">
                        {formatNumber(usage.daily_remaining)}
                      </span>
                      <span className="text-sm text-[var(--docu-text-secondary)]">
                        / {formatNumber(usage.daily_limit)} tokens
                      </span>
                    </div>
                    <div className="w-full bg-[var(--docu-border)] rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-500 ${usage.daily_percentage >= 90 ? 'bg-red-500' : 'bg-[var(--docu-accent)]'}`}
                        style={{ width: `${Math.min(usage.daily_percentage, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-[var(--docu-text-secondary)]">
                      {formatNumber(usage.daily_used)} tokens used ({usage.daily_percentage.toFixed(1)}%)
                    </p>
                  </div>
                </div>

                {/* Monthly Usage */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[var(--docu-accent)]Opacity-80" />
                    <span className="text-sm font-semibold text-[var(--docu-text-main)]">
                      Monthly Usage
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold text-[var(--docu-text-main)]">
                        {formatNumber(usage.monthly_remaining)}
                      </span>
                      <span className="text-sm text-[var(--docu-text-secondary)]">
                        / {formatNumber(usage.monthly_limit)} tokens
                      </span>
                    </div>
                    <div className="w-full bg-[var(--docu-border)] rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-500 ${usage.monthly_percentage >= 90 ? 'bg-red-500' : 'bg-[var(--docu-accent)]'}`}
                        style={{ width: `${Math.min(usage.monthly_percentage, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-[var(--docu-text-secondary)]">
                      {formatNumber(usage.monthly_used)} tokens used ({usage.monthly_percentage.toFixed(1)}%)
                    </p>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[var(--docu-border)]">
                  <div className="text-center p-3 bg-[var(--docu-sidebar)] rounded-lg">
                    <p className="text-xs text-[var(--docu-text-secondary)] mb-1">Total Tokens</p>
                    <p className="text-lg font-bold text-[var(--docu-text-main)]">
                      {formatNumber(usage.total_used)}
                    </p>
                  </div>
                  <div className="text-center p-3 bg-[var(--docu-sidebar)] rounded-lg">
                    <p className="text-xs text-[var(--docu-text-secondary)] mb-1">Total Requests</p>
                    <p className="text-lg font-bold text-[var(--docu-text-main)]">
                      {usage.total_requests.toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Warning */}
                {usage.daily_percentage >= 90 && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <p className="text-sm text-red-500 flex items-center gap-2">
                      <span>⚠️</span>
                      <span>You're running low on tokens. Quota resets in {usage.resets_in}.</span>
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
