import React from 'react';
import { useQueryClient } from '@tanstack/react-query';
import FileUploader from '../components/Upload/FileUploader';
import DocumentList from '../components/Documents/DocumentList';

const Documents: React.FC = () => {
  const queryClient = useQueryClient();

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['documents'] });
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex flex-col md:flex-row gap-8">
        <div className="md:w-1/3">
          <FileUploader onUploadSuccess={handleUploadSuccess} />
        </div>
        <div className="md:w-2/3">
          <DocumentList />
        </div>
      </div>
    </div>
  );
};

export default Documents;
