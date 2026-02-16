import React, { useState } from 'react';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadDocument } from '../../services/api';

const FileUploader: React.FC<{ onUploadSuccess?: () => void }> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadDocument(file);
      setSuccess(true);
      setFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="docu-card p-6">
      <h3 className="text-lg font-semibold mb-4 text-[var(--docu-text-main)]">Upload Document</h3>

      <div className="border-2 border-dashed border-[var(--docu-border)] rounded-lg p-8 text-center hover:bg-[var(--docu-sidebar)] transition relative">
        <input
          type="file"
          onChange={handleFileChange}
          className="absolute inset-0 opacity-0 cursor-pointer"
          accept=".pdf,.txt,.md"
        />
        <Upload className="w-10 h-10 text-[var(--docu-text-secondary)] mx-auto mb-2" />
        <p className="text-[var(--docu-text-main)]">Drag & drop or click to upload</p>
        <p className="text-xs text-[var(--docu-text-secondary)] mt-1">PDF, TXT, MD (Max 10MB)</p>
      </div>

      {file && (
        <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded-md flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span className="text-sm font-medium truncate max-w-[200px]">{file.name}</span>
          </div>
          <button onClick={() => setFile(null)} className="hover:text-blue-900">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-md flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm">Upload successful! Processing started.</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className={`w-full mt-4 py-2 px-4 rounded-lg font-medium transition ${!file || uploading
            ? 'bg-[var(--docu-border)] text-[var(--docu-text-secondary)] cursor-not-allowed'
            : 'bg-[var(--btn-primary-bg)] text-[var(--btn-primary-text)] hover:opacity-90 shadow-sm'
          }`}
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
};

export default FileUploader;
