"use client";

import { format, isPast, isToday } from "date-fns";
import type { Appointment, AppointmentStatus } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Calendar, Clock, DollarSign, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface AppointmentsViewProps {
  appointments: Appointment[];
}

const statusConfig: Record<
  AppointmentStatus,
  { label: string; variant: "success" | "info" | "warning" | "danger" | "muted" }
> = {
  pending: { label: "Pending", variant: "warning" },
  confirmed: { label: "Confirmed", variant: "success" },
  cancelled: { label: "Cancelled", variant: "danger" },
  completed: { label: "Completed", variant: "muted" },
  no_show: { label: "No Show", variant: "danger" },
};

function AppointmentCard({ appt }: { appt: Appointment }) {
  const dt = new Date(appt.appointment_dt);
  const status = statusConfig[appt.status] ?? statusConfig.pending;
  const past = isPast(dt) && !isToday(dt);

  return (
    <div
      className={cn(
        "flex flex-col sm:flex-row gap-4 rounded-lg border border-gray-200 p-4 transition-colors",
        past && "opacity-60"
      )}
    >
      {/* Date block */}
      <div className="flex h-14 w-14 shrink-0 flex-col items-center justify-center rounded-lg bg-violet-50 text-violet-700">
        <span className="text-xs font-medium uppercase">{format(dt, "MMM")}</span>
        <span className="text-xl font-bold leading-none">{format(dt, "d")}</span>
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <p className="font-semibold text-gray-900">{appt.patient_name}</p>
          <Badge variant={status.variant}>{status.label}</Badge>
        </div>

        <p className="mt-0.5 text-sm font-medium text-violet-700">{appt.service}</p>

        <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {format(dt, "h:mm a")} · {appt.duration_minutes} min
          </span>
          <span className="flex items-center gap-1">
            <User className="h-3.5 w-3.5" />
            {appt.patient_phone}
          </span>
          {appt.price_usd != null && (
            <span className="flex items-center gap-1">
              <DollarSign className="h-3.5 w-3.5" />
              {appt.price_usd.toFixed(2)}
            </span>
          )}
        </div>

        {appt.notes && (
          <p className="mt-2 text-xs text-gray-400 italic">&ldquo;{appt.notes}&rdquo;</p>
        )}
      </div>
    </div>
  );
}

export function AppointmentsView({ appointments }: AppointmentsViewProps) {
  const upcoming = appointments.filter(
    (a) => a.status === "confirmed" || a.status === "pending"
  );
  const past = appointments.filter(
    (a) => a.status === "completed" || a.status === "no_show" || a.status === "cancelled"
  );

  if (appointments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Appointments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 mb-4">
              <Calendar className="h-8 w-8 text-gray-400" />
            </div>
            <p className="font-medium text-gray-700">No appointments yet</p>
            <p className="mt-1 text-sm text-gray-400 max-w-xs">
              Appointments booked by the voice agent will appear here automatically.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {upcoming.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Appointments ({upcoming.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {upcoming.map((a) => (
              <AppointmentCard key={a.id} appt={a} />
            ))}
          </CardContent>
        </Card>
      )}

      {past.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-gray-500">Past Appointments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {past.map((a) => (
              <AppointmentCard key={a.id} appt={a} />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
