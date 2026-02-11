// src/pages/Import/GmailImport.jsx
import React, { useState, useEffect } from 'react';
import { Mail, RefreshCw, Check, AlertCircle, FileText, Download, Unplug } from 'lucide-react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import {
  getGmailAuthUrl,
  exchangeGmailToken,
  getGmailStatus,
  scanGmailForCVs,
  importCVFromGmail,
  disconnectGmail
} from '@/services/api';

const GmailImport = ({ onCVImported }) => {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanned, setScanned] = useState(false);
  const [error, setError] = useState(null);
  const [emails, setEmails] = useState([]);
  const [selectedCVs, setSelectedCVs] = useState(new Set());
  const [importing, setImporting] = useState(new Set());
  const [imported, setImported] = useState(new Set());
  const [daysBack, setDaysBack] = useState(30);

  // Check connection status on mount
  useEffect(() => {
    checkConnectionStatus();
  }, []);

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');

    if (code && state) {
      // Clean up URL first to prevent re-processing
      window.history.replaceState({}, document.title, window.location.pathname);
      handleOAuthCallback(code, state);
    }
  }, []);

  const checkConnectionStatus = async () => {
    setLoading(true);
    try {
      const status = await getGmailStatus();
      setConnected(status.connected);
    } catch (err) {
      // Not connected
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      const { auth_url, state } = await getGmailAuthUrl();
      // Store state for verification
      localStorage.setItem('gmail_oauth_state', state);
      // Redirect to Google OAuth
      window.location.href = auth_url;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate Gmail connection');
      setLoading(false);
    }
  };

  const handleOAuthCallback = async (code, state) => {
    setLoading(true);
    setError(null);

    try {
      const storedState = localStorage.getItem('gmail_oauth_state');

      // Skip state check if no stored state (page was refreshed)
      if (storedState && state !== storedState) {
        console.warn('OAuth state mismatch, but proceeding anyway');
      }

      await exchangeGmailToken(code, state);
      localStorage.removeItem('gmail_oauth_state');

      // Mark as connected - backend stores the tokens
      setConnected(true);

      // Auto-scan after connecting
      setTimeout(() => handleScan(), 500);
    } catch (err) {
      console.error('OAuth callback error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to connect Gmail');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectGmail();
      setConnected(false);
      setEmails([]);
      setTokens(null);
      setSelectedCVs(new Set());
      setImported(new Set());
    } catch (err) {
      setError('Failed to disconnect Gmail');
    }
  };

  const handleScan = async () => {
    setScanning(true);
    setError(null);

    try {
      // Tokens are stored on backend, pass empty object
      const result = await scanGmailForCVs({}, { daysBack });
      setEmails(result.emails || []);
      setScanned(true);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to scan emails';
      // If unauthorized, mark as disconnected
      if (err.response?.status === 401) {
        setConnected(false);
        setError('Gmail session expired. Please reconnect.');
      } else {
        setError(errorMsg);
      }
    } finally {
      setScanning(false);
    }
  };

  const toggleCVSelection = (messageId, attachmentId) => {
    const key = `${messageId}:${attachmentId}`;
    const newSelected = new Set(selectedCVs);
    if (newSelected.has(key)) {
      newSelected.delete(key);
    } else {
      newSelected.add(key);
    }
    setSelectedCVs(newSelected);
  };

  const handleImportSelected = async () => {
    setError(null);

    for (const key of selectedCVs) {
      if (imported.has(key)) continue;

      const [messageId, attachmentId] = key.split(':');
      // Find the email and attachment
      let filename = 'cv.pdf';
      for (const email of emails) {
        if (email.message_id === messageId) {
          const att = email.attachments.find(a => a.attachment_id === attachmentId);
          if (att) filename = att.filename;
          break;
        }
      }

      setImporting(prev => new Set([...prev, key]));

      try {
        // Tokens are stored on backend, pass empty object
        const result = await importCVFromGmail({}, messageId, attachmentId, filename);

        setImported(prev => new Set([...prev, key]));
        setSelectedCVs(prev => {
          const next = new Set(prev);
          next.delete(key);
          return next;
        });

        if (onCVImported) {
          onCVImported(result);
        }
      } catch (err) {
        setError(`Failed to import ${filename}: ${err.response?.data?.detail || err.message}`);
      } finally {
        setImporting(prev => {
          const next = new Set(prev);
          next.delete(key);
          return next;
        });
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const totalCVs = emails.reduce((sum, email) => sum + email.attachments.length, 0);

  return (
    <Card className="border-2 border-red-200 bg-red-50/30">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
          <Mail className="w-5 h-5 text-red-600" />
        </div>
        <div>
          <h3 className="font-semibold text-text-primary">Gmail Import</h3>
          <p className="text-sm text-text-secondary">
            Scan your inbox for CV attachments
          </p>
        </div>
        {connected && (
          <button
            onClick={handleDisconnect}
            className="ml-auto text-sm text-gray-500 hover:text-red-600 flex items-center gap-1"
          >
            <Unplug className="w-4 h-4" />
            Disconnect
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!connected ? (
        <div className="text-center py-6">
          <p className="text-text-secondary mb-4">
            Connect your Gmail to automatically find CVs in your inbox
          </p>
          <Button
            variant="outline"
            onClick={handleConnect}
            loading={loading}
            className="border-red-300 text-red-600 hover:bg-red-50"
          >
            <Mail className="w-4 h-4 mr-2" />
            Connect Gmail
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Scan Controls */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-text-secondary">Scan last</label>
              <select
                value={daysBack}
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="px-2 py-1 border border-gray-200 rounded text-sm"
              >
                <option value={7}>7 days</option>
                <option value={14}>14 days</option>
                <option value={30}>30 days</option>
                <option value={60}>60 days</option>
                <option value={90}>90 days</option>
              </select>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleScan}
              loading={scanning}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${scanning ? 'animate-spin' : ''}`} />
              Scan Inbox
            </Button>
          </div>

          {/* Results */}
          {scanning ? (
            <div className="text-center py-6 text-text-secondary">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
              Scanning your inbox...
            </div>
          ) : emails.length > 0 ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">
                  Found {totalCVs} CV(s) in {emails.length} email(s)
                </span>
                {selectedCVs.size > 0 && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={handleImportSelected}
                    disabled={importing.size > 0}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Import {selectedCVs.size} Selected
                  </Button>
                )}
              </div>

              <div className="max-h-64 overflow-y-auto space-y-2">
                {emails.map((email) => (
                  <div
                    key={email.message_id}
                    className="p-3 bg-white rounded-lg border border-gray-200"
                  >
                    <div className="text-sm font-medium text-text-primary truncate">
                      {email.subject}
                    </div>
                    <div className="text-xs text-text-secondary mb-2">
                      From: {email.from_email || email.from}
                    </div>
                    <div className="space-y-1">
                      {email.attachments.map((att) => {
                        const key = `${email.message_id}:${att.attachment_id}`;
                        const isSelected = selectedCVs.has(key);
                        const isImporting = importing.has(key);
                        const isImported = imported.has(key);

                        return (
                          <div
                            key={att.attachment_id}
                            className={`
                              flex items-center gap-2 p-2 rounded cursor-pointer
                              transition-colors
                              ${isImported
                                ? 'bg-green-50 border border-green-200'
                                : isSelected
                                  ? 'bg-secondary/10 border border-secondary'
                                  : 'bg-gray-50 hover:bg-gray-100 border border-transparent'
                              }
                            `}
                            onClick={() => !isImported && !isImporting && toggleCVSelection(email.message_id, att.attachment_id)}
                          >
                            <FileText className={`w-4 h-4 ${isImported ? 'text-green-600' : 'text-gray-400'}`} />
                            <span className="flex-1 text-sm truncate">{att.filename}</span>
                            <span className="text-xs text-text-secondary">
                              {formatFileSize(att.size)}
                            </span>
                            {isImported ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : isImporting ? (
                              <RefreshCw className="w-4 h-4 text-secondary animate-spin" />
                            ) : isSelected ? (
                              <Check className="w-4 h-4 text-secondary" />
                            ) : null}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : scanned ? (
            <div className="text-center py-6 text-text-secondary">
              <Check className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p>No CV attachments found</p>
              <p className="text-xs mt-1">
                No PDF, DOC, or DOCX files in the last {daysBack} days
              </p>
            </div>
          ) : (
            <div className="text-center py-6 text-text-secondary">
              <Mail className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Gmail connected successfully!</p>
              <p className="text-xs mt-1">
                Click "Scan Inbox" to find CVs in your email
              </p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default GmailImport;
