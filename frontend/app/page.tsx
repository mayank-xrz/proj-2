"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { api, type CallLog, type Appointment } from "@/lib/api";
import { AgentStatus } from "@/components/dashboard/AgentStatus";
import { StatsRow } from "@/components/dashboard/StatsRow";
import { CallsTable } from "@/components/dashboard/CallsTable";
import { AppointmentsView } from "@/components/dashboard/AppointmentsView";
import { Spinner } from "@/components/ui/spinner";
import { Phone, Calendar, RefreshCw } from "lucide-react";

type Tab = "calls" | "appointments";

const TABS = [
  { id: "calls" as Tab, label: "Call Logs", icon: Phone },
  { id: "appointments" as Tab, label: "Appointments", icon: Calendar },
] as const;

export default function DashboardPage() {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [initialLoading, setInitialLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("calls");
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  const fetchData = useCallback(async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      const [callData, apptData] = await Promise.all([
        api.calls.list(0, 50),
        api.appointments.list(0, 50),
      ]);
      setCalls(callData.items);
      setAppointments(apptData.items);
      setError(null);
      setLastRefreshed(new Date());
    } catch {
      setError(
        "Could not reach the backend API. Make sure the server is running on port 8000."
      );
    } finally {
      setInitialLoading(false);
      if (isManual) setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60_000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const hasData = calls.length > 0 || appointments.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top nav */}
      <header className="sticky top-0 z-10 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600"
                aria-hidden="true"
              >
                <Phone className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="font-bold text-gray-900 leading-tight">Voice Receptionist</p>
                <p className="text-xs text-gray-500 leading-tight">Powered by OmniDimension</p>
              </div>
            </div>
            <button
              onClick={() => fetchData(true)}
              disabled={refreshing}
              aria-label="Refresh dashboard data"
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">{refreshing ? "Refreshing…" : "Refresh"}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Agent status */}
        <AgentStatus />

        {/* Error banner */}
        {error && (
          <div
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            <strong>Connection error:</strong> {error}
          </div>
        )}

        {/* Stats — shown as soon as we have data, even during subsequent refreshes */}
        {hasData && (
          <StatsRow calls={calls} appointments={appointments} />
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav role="tablist" aria-label="Dashboard sections" className="-mb-px flex gap-6">
            {TABS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                role="tab"
                aria-selected={activeTab === id}
                aria-controls={`panel-${id}`}
                id={`tab-${id}`}
                onClick={() => setActiveTab(id)}
                className={`flex items-center gap-2 border-b-2 pb-3 text-sm font-medium transition-colors ${
                  activeTab === id
                    ? "border-violet-600 text-violet-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        {initialLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <Spinner className="h-8 w-8 text-violet-500" />
            <p className="text-sm text-gray-500">Loading dashboard data…</p>
          </div>
        ) : (
          <>
            {activeTab === "calls" && (
              <div id="panel-calls" role="tabpanel" aria-labelledby="tab-calls">
                <CallsTable calls={calls} />
              </div>
            )}
            {activeTab === "appointments" && (
              <div id="panel-appointments" role="tabpanel" aria-labelledby="tab-appointments">
                <AppointmentsView appointments={appointments} />
              </div>
            )}
          </>
        )}

        {lastRefreshed && (
          <p className="text-center text-xs text-gray-400" aria-live="polite">
            Last updated {lastRefreshed.toLocaleTimeString()} · Auto-refreshes every 60 s
          </p>
        )}
      </main>
    </div>
  );
}
