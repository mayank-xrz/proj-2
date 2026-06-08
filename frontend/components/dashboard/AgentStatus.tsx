"use client";

import { useEffect, useState } from "react";
import { api, type HealthStatus } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Phone } from "lucide-react";

export function AgentStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const check = async () => {
      try {
        const h = await api.health();
        setHealth(h);
        setError(false);
      } catch {
        setError(true);
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  const online = !error && health?.status === "ok";

  return (
    <Card className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 sm:p-6">
      <div
        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full ${
          online ? "bg-emerald-100" : "bg-gray-100"
        }`}
      >
        <Phone
          className={`h-6 w-6 ${online ? "text-emerald-600" : "text-gray-400"}`}
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-gray-900">OmniDimension Voice Agent</span>
          <span
            className={`inline-flex h-2 w-2 rounded-full ${
              online ? "bg-emerald-500 animate-pulse" : "bg-gray-300"
            }`}
          />
          <span
            className={`text-sm font-medium ${
              online ? "text-emerald-600" : "text-gray-400"
            }`}
          >
            {error ? "Offline" : health ? "Live" : "Checking…"}
          </span>
        </div>
        <p className="mt-0.5 text-sm text-gray-500 truncate">
          {error
            ? "Backend unreachable — start the API server"
            : health
            ? `API v${health.version} · Last checked ${new Date(health.timestamp).toLocaleTimeString()}`
            : "Connecting to backend…"}
        </p>
      </div>
    </Card>
  );
}
