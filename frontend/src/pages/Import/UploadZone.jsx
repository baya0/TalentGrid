// src/pages/Import/UploadZone.jsx
import React, { useCallback, useState, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';
import Card from '@/components/common/Card';

const UploadZone = ({ onFilesSelected }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFilesSelected(files);
    }
  }, [onFilesSelected]);

  const handleFileInput = useCallback((e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFilesSelected(files);
    }
    // Reset input so same file can be selected again
    e.target.value = '';
  }, [onFilesSelected]);

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card
      className={`
        border-2 border-dashed transition-all duration-200
        ${isDragging
          ? 'border-primary bg-primary-50 scale-102'
          : 'border-gray-300 hover:border-primary-300'
        }
      `}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="text-center py-12">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <div className={`
            w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200
            ${isDragging ? 'bg-primary scale-110' : 'bg-primary-100'}
          `}>
            <Upload className={`w-10 h-10 ${isDragging ? 'text-white' : 'text-primary'}`} />
          </div>
        </div>

        {/* Text */}
        <h3 className="text-xl font-semibold text-text-primary mb-2">
          Drag & Drop CVs here or click to browse
        </h3>
        <p className="text-text-secondary mb-6">
          Supports PDF, DOCX, and image files (JPG, PNG)
        </p>

        {/* Browse Button - using native button with onClick */}
        <button
          type="button"
          onClick={handleBrowseClick}
          className="inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200
                     bg-secondary text-white hover:bg-secondary-600 focus:ring-secondary shadow-sm hover:shadow-md
                     px-6 py-3 text-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2"
        >
          Browse Files
        </button>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
          onChange={handleFileInput}
          className="hidden"
        />

        {/* Supported Formats */}
        <div className="mt-6 flex items-center justify-center gap-4 text-sm text-text-muted">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>PDF</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>DOCX</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>Images</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default UploadZone;
