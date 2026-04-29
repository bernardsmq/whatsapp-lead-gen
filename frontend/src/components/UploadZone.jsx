import { useState } from 'react';
import { sheetsAPI } from '../lib/api';
import { UploadedLeadsPreview } from './UploadedLeadsPreview';

export const UploadZone = ({ onSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedLeads, setUploadedLeads] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file) => {
    if (!file.name.match(/\.(csv|xlsx|xls)$/)) {
      setError('Please upload a CSV or Excel file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setUploadedLeads(null);

    try {
      const response = await sheetsAPI.upload(file);
      setError(null);
      setUploadedLeads(response.data.leads);  // Store leads for preview
      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
          isDragging
            ? 'border-yellow-500 bg-yellow-900/10'
            : 'border-slate-600 hover:border-slate-500 bg-slate-700/50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          onChange={handleFileInput}
          accept=".csv,.xlsx,.xls"
          disabled={isLoading}
        />
        <label htmlFor="file-input" className="cursor-pointer">
          <div className="mb-4 text-5xl">📄</div>
          <p className="font-semibold text-white text-lg">Drag and drop your file here</p>
          <p className="text-sm text-slate-400 mt-1">or click to select (CSV or Excel)</p>
        </label>
        {isLoading && <p className="mt-4 text-yellow-400 font-medium">⏳ Uploading...</p>}
        {error && <p className="mt-4 text-red-400">{error}</p>}
      </div>

      {/* Show preview right here in the same window */}
      {uploadedLeads && uploadedLeads.length > 0 && (
        <UploadedLeadsPreview leads={uploadedLeads} />
      )}
    </>
  );
};
