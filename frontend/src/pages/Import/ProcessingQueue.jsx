// src/pages/Import/ProcessingQueue.jsx
import React from 'react';
import { CheckCircle, Clock, Loader2, XCircle, Eye } from 'lucide-react';
import Card from '@/components/common/Card';
import Badge from '@/components/common/Badge';
import ProgressBar from '@/components/common/ProgressBar';

const ProcessingQueue = ({ queue, onViewCandidate }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 text-primary animate-spin" />;
      case 'indexed':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'queued':
        return <Clock className="w-4 h-4 text-text-muted" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-error" />;
      default:
        return null;
    }
  };

  return (
    <Card className="sticky top-6 border-2 border-primary-200">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-lg font-bold text-primary mb-1">
          AI Engine Status
        </h2>
        <Badge variant="success" size="lg" className="font-bold">
          Active
        </Badge>
      </div>

      {/* Queue List */}
      <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
        {queue.map((item) => (
          <div
            key={item.id}
            className="p-3 bg-background rounded-lg border border-gray-200"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                {getStatusIcon(item.status)}
                <span className="text-sm text-text-primary font-medium truncate">
                  {item.name}
                </span>
              </div>
              {item.status === 'indexed' && item.candidateId && onViewCandidate && (
                <button
                  onClick={() => onViewCandidate(item.candidateId)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="View Candidate"
                >
                  <Eye className="w-4 h-4 text-primary" />
                </button>
              )}
            </div>

            {item.status === 'processing' && (
              <ProgressBar
                value={item.progress}
                max={100}
                size="sm"
                color="secondary"
                showLabel={true}
              />
            )}

            {item.status === 'queued' && (
              <p className="text-xs text-text-muted">
                Waiting in queue...
              </p>
            )}

            {item.status === 'indexed' && (
              <p className="text-xs text-success">
                Successfully processed{item.candidateName ? `: ${item.candidateName}` : ''}
              </p>
            )}

            {item.status === 'failed' && (
              <p className="text-xs text-error">
                {item.error || 'Processing failed'}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {queue.length === 0 && (
        <div className="text-center py-8 text-text-muted">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-sm">No files in queue</p>
          <p className="text-xs mt-1">Upload CVs to start processing</p>
        </div>
      )}
    </Card>
  );
};

export default ProcessingQueue;
