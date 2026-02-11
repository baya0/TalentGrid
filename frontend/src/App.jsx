// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import PrivateRoute from '@/components/auth/PrivateRoute';
import Layout from '@/components/layout/Layout';

// Pages
import Login from '@/pages/Auth/Login';
import Register from '@/pages/Auth/Register';
import Onboarding from '@/pages/Onboarding/Onboarding';
import Dashboard from '@/pages/Dashboard/Dashboard';
import Search from '@/pages/Search/Search';
import CandidateProfile from '@/pages/CandidateProfile/CandidateProfile';
import Import from '@/pages/Import/Import';
import Analytics from '@/pages/Analytics/Analytics';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Onboarding */}
            <Route path="/onboarding" element={<Onboarding />} />

            {/* Protected Routes */}
            <Route element={<PrivateRoute />}>
              <Route element={<Layout />}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/sourcing" element={<Search />} />
                <Route path="/candidates/:id" element={<CandidateProfile />} />
                <Route path="/import" element={<Import />} />
                <Route path="/analytics" element={<Analytics />} />
              </Route>
            </Route>

            {/* 404 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
