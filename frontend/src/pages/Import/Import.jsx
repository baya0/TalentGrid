// src/pages/Import/Import.jsx
import React, { useState, useEffect } from 'react';
import { Upload, Database, HardDrive, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import ProgressBar from '@/components/common/ProgressBar';
import UploadZone from './UploadZone';
import ProcessingQueue from './ProcessingQueue';
import GmailImport from './GmailImport';
import { uploadCV } from '@/services/api';

const STORAGE_KEY = 'talentgrid_import_state';

const Import = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [processingQueue, setProcessingQueue] = useState([]);
  const [successCount, setSuccessCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [isRestored, setIsRestored] = useState(false);

  const totalSteps = 3;
  const progress = (currentStep / totalSteps) * 100;

  // Load saved state from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const state = JSON.parse(saved);
        // Only restore completed items (not in-progress ones)
        const completedQueue = (state.processingQueue || []).filter(
          item => item.status === 'indexed' || item.status === 'failed'
        );
        if (completedQueue.length > 0) {
          setProcessingQueue(completedQueue);
          setSuccessCount(state.successCount || 0);
          setErrorCount(state.errorCount || 0);
          setCurrentStep(state.currentStep || 3);
          setIsRestored(true);
        }
      } catch (e) {
        console.error('Failed to load import state:', e);
      }
    }
  }, []);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    // Only save if we have completed items
    const completedQueue = processingQueue.filter(
      item => item.status === 'indexed' || item.status === 'failed'
    );
    if (completedQueue.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        processingQueue: completedQueue,
        successCount,
        errorCount,
        currentStep,
        savedAt: new Date().toISOString(),
      }));
    }
  }, [processingQueue, successCount, errorCount, currentStep]);

  const handleClearHistory = () => {
    setProcessingQueue([]);
    setSuccessCount(0);
    setErrorCount(0);
    setCurrentStep(1);
    setIsRestored(false);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleFilesSelected = async (files) => {
    const fileArray = Array.from(files);

    // Add files to queue as pending
    const newQueueItems = fileArray.map((file, index) => ({
      id: Date.now() + index,
      name: file.name,
      progress: 0,
      status: 'queued',
      file: file,
    }));

    setProcessingQueue(prev => [...prev, ...newQueueItems]);
    setCurrentStep(2);

    // Process files one by one
    for (const queueItem of newQueueItems) {
      await processFile(queueItem);
    }

    setCurrentStep(3);
  };

  const processFile = async (queueItem) => {
    // Update status to processing
    setProcessingQueue(prev =>
      prev.map(item =>
        item.id === queueItem.id
          ? { ...item, status: 'processing', progress: 10 }
          : item
      )
    );

    try {
      // Upload and parse the CV
      const result = await uploadCV(queueItem.file, (percent) => {
        // Update progress during upload
        setProcessingQueue(prev =>
          prev.map(item =>
            item.id === queueItem.id
              ? { ...item, progress: Math.min(percent, 50) }
              : item
          )
        );
      });

      // Simulate processing progress after upload
      setProcessingQueue(prev =>
        prev.map(item =>
          item.id === queueItem.id
            ? { ...item, progress: 75 }
            : item
        )
      );

      // Small delay to show progress
      await new Promise(resolve => setTimeout(resolve, 500));

      // Mark as complete
      setProcessingQueue(prev =>
        prev.map(item =>
          item.id === queueItem.id
            ? {
                ...item,
                progress: 100,
                status: 'indexed',
                candidateId: result.id,
                candidateName: result.name,
                file: undefined, // Remove file object before saving to localStorage
              }
            : item
        )
      );

      setSuccessCount(prev => prev + 1);

    } catch (error) {
      console.error('Upload failed:', error);

      // Mark as failed
      setProcessingQueue(prev =>
        prev.map(item =>
          item.id === queueItem.id
            ? {
                ...item,
                status: 'failed',
                error: error.response?.data?.detail || error.message,
                file: undefined, // Remove file object
              }
            : item
        )
      );

      setErrorCount(prev => prev + 1);
    }
  };

  const handleViewCandidate = (candidateId) => {
    navigate(`/candidates/${candidateId}`);
  };

  const handleViewAll = () => {
    navigate('/sourcing');
  };

  const handleGmailCVImported = (result) => {
    // Add imported CV to queue as already processed
    const queueItem = {
      id: Date.now(),
      name: result.name || 'Gmail CV',
      progress: 100,
      status: 'indexed',
      candidateId: result.candidate_id,
      candidateName: result.name,
      source: 'gmail',
    };
    setProcessingQueue(prev => [...prev, queueItem]);
    setSuccessCount(prev => prev + 1);
    if (currentStep === 1) {
      setCurrentStep(3);
    }
  };

  const integrations = [
    {
      name: 'Google Drive',
      icon: <HardDrive className="w-8 h-8" />,
      color: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
      available: false,
    },
    {
      name: 'Dropbox',
      icon: <Database className="w-8 h-8" />,
      color: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
      available: false,
    },
    {
      name: 'SQL Import',
      icon: <Database className="w-8 h-8" />,
      color: 'bg-orange-50 text-orange-600 hover:bg-orange-100',
      available: false,
    },
  ];

  const getStepLabel = () => {
    switch (currentStep) {
      case 1:
        return 'Upload CVs';
      case 2:
        return 'Processing with AI';
      case 3:
        return 'Complete';
      default:
        return 'Upload';
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-text-primary mb-2">
              CV Import
            </h1>
            <p className="text-text-secondary">
              Upload CVs to automatically extract and index candidate information using AI
            </p>
          </div>
          {(successCount > 0 || errorCount > 0) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearHistory}
              className="text-text-secondary hover:text-text-primary"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Clear History
            </Button>
          )}
        </div>

        {/* Restored Session Notice */}
        {isRestored && (
          <div className="mb-6 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>Your previous import session has been restored.</span>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-8">
          <ProgressBar
            value={progress}
            max={100}
            size="md"
            color="secondary"
            label={`Step ${currentStep} of ${totalSteps}: ${getStepLabel()}`}
            showLabel={true}
          />
        </div>

        {/* Success/Error Summary */}
        {(successCount > 0 || errorCount > 0) && (
          <div className="mb-6 flex gap-4">
            {successCount > 0 && (
              <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-lg">
                <CheckCircle className="w-5 h-5" />
                <span>{successCount} CV(s) processed successfully</span>
              </div>
            )}
            {errorCount > 0 && (
              <div className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-lg">
                <AlertCircle className="w-5 h-5" />
                <span>{errorCount} CV(s) failed</span>
              </div>
            )}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Side - Upload Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Zone */}
            <UploadZone onFilesSelected={handleFilesSelected} />

            {/* Gmail Import */}
            <GmailImport onCVImported={handleGmailCVImported} />

            {/* Integration Options */}
            <Card>
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Or connect to external sources (Coming Soon)
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {integrations.map((integration, index) => (
                  <button
                    key={index}
                    disabled={!integration.available}
                    className={`
                      flex flex-col items-center justify-center p-6 rounded-xl
                      transition-all duration-200 border-2 border-transparent
                      ${integration.available
                        ? `${integration.color} cursor-pointer hover:border-current`
                        : 'bg-gray-50 text-gray-400 cursor-not-allowed opacity-60'
                      }
                    `}
                  >
                    {integration.icon}
                    <span className="mt-3 font-medium">{integration.name}</span>
                  </button>
                ))}
              </div>
            </Card>

            {/* View All Button */}
            {successCount > 0 && (
              <div className="flex justify-center">
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={handleViewAll}
                >
                  View All Candidates
                </Button>
              </div>
            )}
          </div>

          {/* Right Side - AI Engine Status */}
          <div className="lg:col-span-1">
            <ProcessingQueue
              queue={processingQueue}
              onViewCandidate={handleViewCandidate}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Import;
