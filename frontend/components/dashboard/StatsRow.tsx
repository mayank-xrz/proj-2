"use client";

import { memo, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { PhoneCall, CalendarCheck, MessageSquare, TrendingUp } from "lucide-react";
import type { CallLog, Appointment } from "@/lib/api";

interface StatsRowProps {
  calls: CallLog[];
  appointments: Appointment[];
}

const STAT_ICONS = [PhoneCall, CalendarCheck, MessageSquare, TrendingUp] as const;

function StatsRowComponent({ calls, appointments }: StatsRowProps) {
  const stats = useMemo(() => {
    const totalCalls = calls.length;
    const booked = calls.filter((c) => c.outcome === "appointment_booked").length;
    const faqAnswered = calls.filter((c) => c.outcome === "faq_answered").length;
    const upcomingAppts = appointments.filter((a) => a.status === "confirmed").length;
    const bookingRate = totalCalls > 0 ? Math.round((booked / totalCalls) * 100) : 0;

    return [
      {
        label: "Total Calls",
        value: totalCalls,
        sub: "last 14 days",
        icon: STAT_ICONS[0],
        color: "text-blue-600",
        bg: "bg-blue-50",
      },
      {
        label: "Appointments Booked",
        value: booked,
        sub: `${bookingRate}% booking rate`,
        icon: STAT_ICONS[1],
        color: "text-emerald-600",
        bg: "bg-emerald-50",
      },
      {
        label: "FAQs Answered",
        value: faqAnswered,
        sub: "by the AI agent",
        icon: STAT_ICONS[2],
        color: "text-violet-600",
        bg: "bg-violet-50",
      },
      {
        label: "Upcoming",
        value: upcomingAppts,
        sub: "confirmed appointments",
        icon: STAT_ICONS[3],
        color: "text-amber-600",
        bg: "bg-amber-50",
      },
    ];
  }, [calls, appointments]);

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {stats.map((stat, i) => (
        <Card key={i}>
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-500 truncate">{stat.label}</p>
                <p className="mt-1 text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="mt-1 text-xs text-gray-400 truncate">{stat.sub}</p>
              </div>
              <div className={`shrink-0 rounded-lg p-2.5 ${stat.bg}`} aria-hidden="true">
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export const StatsRow = memo(StatsRowComponent);
