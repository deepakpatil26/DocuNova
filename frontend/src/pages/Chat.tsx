import React from 'react';
import { useLocation } from 'react-router-dom';
import ChatInterface from '../components/Chat/ChatInterface';

const Chat: React.FC = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const conversationId = searchParams.get('id');
  const preSelectedDocumentIds = location.state?.documentIds || [];

  return (
    <div className="h-full">
      <ChatInterface
        key={conversationId || 'new'}
        initialDocumentIds={preSelectedDocumentIds}
        conversationId={conversationId || undefined}
      />
    </div>
  );
};

export default Chat;
