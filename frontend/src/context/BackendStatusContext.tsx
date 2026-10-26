import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { healthService } from '../services/healthService';
import type { HealthResponse } from '../types';

export type BackendConnectionState = 'connected' | 'connecting' | 'disconnected' | 'error';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
}

interface BackendStatusContextType {
  status: BackendConnectionState;
  health: HealthResponse | null;
  latencyMs: number | null;
  lastChecked: Date | null;
  errorMessage: string | null;
  refreshHealth: () => Promise<void>;
  toasts: ToastMessage[];
  addToast: (type: ToastMessage['type'], title: string, message?: string) => void;
  removeToast: (id: string) => void;
}

const BackendStatusContext = createContext<BackendStatusContextType | undefined>(undefined);

export const BackendStatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<BackendConnectionState>('connecting');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((type: ToastMessage['type'], title: string, message?: string) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const refreshHealth = useCallback(async () => {
    const startTime = performance.now();
    try {
      const data = await healthService.checkHealth();
      const elapsed = Math.round(performance.now() - startTime);
      setHealth(data);
      setLatencyMs(elapsed);
      setStatus('connected');
      setErrorMessage(null);
      setLastChecked(new Date());
    } catch (err: unknown) {
      setStatus('disconnected');
      setHealth(null);
      setLatencyMs(null);
      setLastChecked(new Date());
      setErrorMessage(err instanceof Error ? err.message : 'Cannot reach backend');
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 15000);
    return () => clearInterval(interval);
  }, [refreshHealth]);

  return (
    <BackendStatusContext.Provider
      value={{
        status,
        health,
        latencyMs,
        lastChecked,
        errorMessage,
        refreshHealth,
        toasts,
        addToast,
        removeToast,
      }}
    >
      {children}
    </BackendStatusContext.Provider>
  );
};

export const useBackendStatus = () => {
  const context = useContext(BackendStatusContext);
  if (!context) {
    throw new Error('useBackendStatus must be used within a BackendStatusProvider');
  }
  return context;
};
