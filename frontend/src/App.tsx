import { useState, useEffect, useCallback } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { SystemHealthView } from './views/SystemHealthView';
import { ArchitectureView } from './views/ArchitectureView';
import { DataPipelineView } from './views/DataPipelineView';
import { FinancialDataEngineView } from './views/FinancialDataEngineView';
import { FundamentalAnalysisView } from './views/FundamentalAnalysisView';
import { ApiService } from './services/api';
import { HealthResponse } from './types/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('fundamental');
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ApiService.getHealth();
      setHealthData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const systemStatus = healthData?.status || (error ? 'unhealthy' : 'checking');
  const version = healthData?.version || '0.1.0';

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      systemStatus={systemStatus}
      version={version}
    >
      {currentTab === 'fundamental' && <FundamentalAnalysisView />}
      {currentTab === 'financials' && <FinancialDataEngineView />}
      {currentTab === 'health' && (
        <SystemHealthView
          healthData={healthData}
          loading={loading}
          error={error}
          onRefresh={fetchHealth}
        />
      )}
      {currentTab === 'architecture' && <ArchitectureView />}
      {currentTab === 'pipeline' && <DataPipelineView />}
    </AppLayout>
  );
}

export default App;

