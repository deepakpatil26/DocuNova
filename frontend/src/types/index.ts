export interface Document {
  id: string;
  filename: string;
  upload_date: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count: number;
  file_size: number;
}

export interface Source {
  document_id: string;
  filename: string;
  page?: number;
  chunk_text: string;
  relevance_score: number;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Stats {
  documents: number;
  conversations: number;
  messages: number;
}
