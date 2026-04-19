import { useState } from 'react';
import { sheetsAPI } from '../lib/api';

export const UploadZone = ({ onSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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

    try {
      const response = await sheetsAPI.upload(file);
      setError(null);
      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
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
        <div className="mb-2">
          📄
        </div>
        <p className="font-semibold text-gray-700">Drag and drop your file here</p>
        <p className="text-sm text-gray-500">or click to select (CSV or Excel)</p>
      </label>
      {isLoading && <p className="mt-2 text-blue-600">Uploading...</p>}
      {error && <p className="mt-2 text-red-600">{error}</p>}
    </div>
  );
};
