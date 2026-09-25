import { useEffect, useState } from 'react';
import { ApplicationMonitorItem } from '../types';

export function useAdminWebSocket(onNewApplicant?: (applicant: ApplicationMonitorItem) => void) {
  const [realtimeApps, setRealtimeApps] = useState<ApplicationMonitorItem[]>([]);

  useEffect(() => {
    const backendHost = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
    const wsUrl = backendHost.replace(/^http/, 'ws');
    let socket: WebSocket | null = null;

    function connect() {
      try {
        socket = new WebSocket(wsUrl);
        socket.onopen = () => console.log('[Admin WS] Connected to shared backend WebSockets');
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'NEW_APPLICANT_REGISTERED') {
              const newApp: ApplicationMonitorItem = {
                id: `APP-${Date.now().toString().slice(-4)}`,
                applicationNumber: data.data.applicationNumber || `SP-REG-${Date.now().toString().slice(-6)}`,
                applicantId: data.data.email,
                applicantName: data.data.fullName || data.data.name || data.data.email.split('@')[0],
                email: data.data.email,
                scholarshipId: 'SCH-TN-001',
                scholarshipTitle: data.data.role === 'school' ? 'State Board School Merit Scholarship' : 'Pudhumai Penn Higher Education Grant',
                status: 'SUBMITTED',
                activeFieldLocks: [],
                veriflowStatus: 'normal',
                currentFactSnapshotVersion: 1,
                veriflowEvents: [],
                recoveryDecisions: [],
                createdAt: data.data.timestamp || new Date().toISOString(),
                updatedAt: new Date().toISOString(),
              };

              setRealtimeApps((prev) => [newApp, ...prev]);
              if (onNewApplicant) onNewApplicant(newApp);
            }
          } catch (e) {
            console.error('[Admin WS] Parse error:', e);
          }
        };
        socket.onclose = () => setTimeout(connect, 3000);
      } catch (err) {
        console.error('[Admin WS] Connection error:', err);
      }
    }

    connect();

    return () => {
      if (socket) socket.close();
    };
  }, []);

  return realtimeApps;
}
