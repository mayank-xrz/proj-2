"use client";

import { memo, useState, useCallback } from "react";
import { formatDistanceToNow, format, isValid } from "date-fns";
import type { CallLog, CallOutcome } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Phone, PhoneOff, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface CallsTableProps {
  calls: CallLog[];
}

const outcomeConfig: Record<
  CallOutcome,
  { label: string; variant: "success" | "info" | "warning" | "danger" | "muted" }
> = {
  appointment_booked: { label: "Booked", variant: "success" },
  faq_answered: { label: "FAQ", variant: "info" },
  transferred: { label: "Transferred", variant: "warning" },
  voicemail: { label: "Voicemail", variant: "muted" },
  hung_up: { label: "Hung Up", variant: "danger" },
  unknown: { label: "Unknown", variant: "muted" },
};

function formatDuration(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}m ${secs}s`;
}

function safeDate(iso: string): Date | null {
  const d = new Date(iso);
  return isValid(d) ? d : null;
}

function CallRow({ call }: { call: CallLog }) {
  const [expanded, setExpanded] = useState(false);
  const toggle = useCallback(() => setExpanded((e) => !e), []);

  const outcome = outcomeConfig[call.outcome] ?? outcomeConfig.unknown;
  const startedAt = safeDate(call.started_at);

  return (
    <>
      <tr
        className={cn(
          "border-b border-gray-100 transition-colors hover:bg-gray-50/60 cursor-pointer",
          expanded && "bg-gray-50/60"
        )}
        onClick={toggle}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggle();
          }
        }}
        tabIndex={0}
        role="button"
        aria-expanded={expanded}
        aria-label={`Call from ${call.caller_name ?? call.caller_number} — click to ${expanded ? "collapse" : "expand"}`}
      >
        <td className="py-3 px-4">
          <div className="flex items-center gap-2.5">
            <div
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                call.status === "completed" ? "bg-emerald-50" : "bg-gray-100"
              )}
              aria-hidden="true"
            >
              {call.status === "missed" ? (
                <PhoneOff className="h-4 w-4 text-red-500" />
              ) : (
                <Phone className="h-4 w-4 text-emerald-600" />
              )}
            </div>
            <div className="min-w-0">
              <p className="font-medium text-gray-900 text-sm">
                {call.caller_name ?? "Unknown Caller"}
              </p>
              <p className="text-xs text-gray-500">{call.caller_number}</p>
            </div>
          </div>
        </td>
        <td className="py-3 px-4 hidden sm:table-cell">
          <Badge variant={outcome.variant}>{outcome.label}</Badge>
        </td>
        <td className="py-3 px-4 hidden md:table-cell text-sm text-gray-600">
          {formatDuration(call.duration_seconds)}
        </td>
        <td className="py-3 px-4 text-sm text-gray-500 text-right whitespace-nowrap">
          {startedAt ? formatDistanceToNow(startedAt, { addSuffix: true }) : "—"}
        </td>
        <td className="py-3 px-4 text-gray-400" aria-hidden="true">
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-gray-50/80 border-b border-gray-100">
          <td colSpan={5} className="px-4 py-4">
            <div className="space-y-2 max-w-2xl">
              <div className="flex gap-4 text-xs text-gray-500">
                {startedAt && (
                  <span>
                    <span className="font-medium text-gray-700">Started: </span>
                    {format(startedAt, "MMM d, yyyy 'at' h:mm a")}
                  </span>
                )}
                {(() => {
                  const endedAt = call.ended_at ? safeDate(call.ended_at) : null;
                  return endedAt ? (
                    <span>
                      <span className="font-medium text-gray-700">Ended: </span>
                      {format(endedAt, "h:mm a")}
                    </span>
                  ) : null;
                })()}
              </div>
              {call.summary && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-0.5">Summary</p>
                  <p className="text-sm text-gray-600">{call.summary}</p>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

const MemoCallRow = memo(CallRow);

function CallsTableComponent({ calls }: CallsTableProps) {
  if (calls.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Calls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div
              className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 mb-4"
              aria-hidden="true"
            >
              <Phone className="h-8 w-8 text-gray-400" />
            </div>
            <p className="font-medium text-gray-700">No calls yet</p>
            <p className="mt-1 text-sm text-gray-400 max-w-xs">
              Calls will appear here once your OmniDimension voice agent starts receiving inbound
              calls.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Calls</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto" role="region" aria-label="Call logs">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="py-3 px-4 text-left" scope="col">Caller</th>
                <th className="py-3 px-4 text-left hidden sm:table-cell" scope="col">Outcome</th>
                <th className="py-3 px-4 text-left hidden md:table-cell" scope="col">Duration</th>
                <th className="py-3 px-4 text-right" scope="col">When</th>
                <th className="py-3 px-4" scope="col" aria-label="Expand" />
              </tr>
            </thead>
            <tbody>
              {calls.map((call) => (
                <MemoCallRow key={call.id} call={call} />
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export const CallsTable = memo(CallsTableComponent);
