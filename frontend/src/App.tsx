import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { BackendStatusProvider } from './context/BackendStatusContext';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage } from './pages/CasesPage';
import { EvidencePage } from './pages/EvidencePage';
import { NetworkAnalysisPage } from './pages/NetworkAnalysisPage';
import { ConnectionsPage } from './pages/ConnectionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { SystemHealthPage } from './pages/SystemHealthPage';

export const App: React.FC = () => {
  return (
    <BackendStatusProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="network" element={<NetworkAnalysisPage />} />
            <Route path="connections" element={<ConnectionsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="health" element={<SystemHealthPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </BackendStatusProvider>
  );
};

export default App;
