import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AdminUsers from '../pages/AdminUsers';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the API call
vi.mock('../services/api', () => ({
  listUsers: vi.fn(() => Promise.resolve([])),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithClient = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('AdminUsers Component', () => {
  it('renders loading state initially', () => {
    // Mock return value is handled by React Query's isLoading first
    renderWithClient(<AdminUsers />);
    expect(screen.getByText(/Loading users/i)).toBeInTheDocument();
  });
});
