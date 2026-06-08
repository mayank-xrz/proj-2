"use client";

import { useEffect, useState, useCallback } from "react";
import { api, type CallLog, type Appointment } from "@/lib/api";
import { AgentStatus } from "@/components/dashboard/AgentStatus";
import { StatsRow } from "@/components/dashboard/StatsRow";
import { CallsTable } from "@/components/dashboard/CallsTable";
import { AppointmentsView } from "@/components/dashboard/AppointmentsView";
import { Spinner } from "@/components/ui/spinner";
import { Phone, Calendar, RefreshCw } from "lucide-react";

type Tab = "calls" | "appointments";

export default function DashboardPage() {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("calls");
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
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
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60_000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top nav */}
      <header className="sticky top-0 z-10 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-600">
                <Phone className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="font-bold text-gray-900 leading-tight">Voice Receptionist</p>
                <p className="text-xs text-gray-500 leading-tight">Powered by OmniDimension</p>
              </div>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
              title="Refresh data"
            >
              <RefreshCw className="h-4 w-4" />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Agent status */}
        <AgentStatus />

        {/* Error banner */}
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <strong>Connection error:</strong> {error}
          </div>
        )}

        {/* Stats */}
        {!loading && !error && (
          <StatsRow calls={calls} appointments={appointments} />
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex gap-6">
            {(
              [
                { id: "calls" as Tab, label: "Call Logs", icon: Phone },
                { id: "appointments" as Tab, label: "Appointments", icon: Calendar },
              ] as const
            ).map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center gap-2 border-b-2 pb-3 text-sm font-medium transition-colors ${
                  activeTab === id
                    ? "border-violet-600 text-violet-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <Spinner className="h-8 w-8 text-violet-500" />
            <p className="text-sm text-gray-500">Loading dashboard data…</p>
          </div>
        ) : (
          <>
            {activeTab === "calls" && <CallsTable calls={calls} />}
            {activeTab === "appointments" && (
              <AppointmentsView appointments={appointments} />
            )}
          </>
        )}

        {lastRefreshed && (
          <p className="text-center text-xs text-gray-400">
            Last updated {lastRefreshed.toLocaleTimeString()} · Auto-refreshes every 60 s
          </p>
        )}
      </main>
    </div>
  );
}
