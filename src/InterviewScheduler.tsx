import { FormEvent, useEffect, useMemo, useState } from "react";
import { getSavedAnalyses } from "./lib/analysisStorage";
import {
  getInterviews,
  INTERVIEWS_CHANGED_EVENT,
  saveInterview,
  type Interview,
  type InterviewStatus,
  type InterviewType,
} from "./lib/interviewStorage";
import { getJobRoles, type JobRole } from "./lib/jobRoleStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";

type CalendarView = "Month" | "Week" | "Day";
type DateRange = "Next 7 Days" | "Next 30 Days" | "Next 90 Days" | "All Time";

type Props = {
  openCreate?: boolean;
  onOpenCandidate: (analysis: AnalysisResult) => void;
};

const PAGE_SIZE = 8;
const statuses: InterviewStatus[] = ["Scheduled", "Completed", "Rescheduled", "Cancelled"];

const paths = {
  calendar: "M5 5h14a2 2 0 0 1 2 2v12H3V7a2 2 0 0 1 2-2Zm2-2v4m10-4v4M3 10h18m-14 4h3m2 0h3m2 0h1m-11 3h3m2 0h3",
  upcoming: "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  check: "m6 12 4 4 8-9",
  alert: "M12 8v5m0 3h.01M10 3h4l8 16H2L10 3Z",
  plus: "M12 5v14M5 12h14",
  export: "M12 4v11m0-11L8 8m4-4 4 4M5 14v5h14v-5",
  search: "m20 20-4.2-4.2M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z",
  left: "m14 7-5 5 5 5",
  right: "m10 7 5 5-5 5",
  close: "m7 7 10 10m0-10L7 17",
  video: "M4 7h11v10H4V7Zm11 3 5-3v10l-5-3",
  location: "M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Zm-8 2a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z",
  phone: "M6 3h4l2 5-3 2a15 15 0 0 0 5 5l2-3 5 2v4c0 2-2 3-4 3A18 18 0 0 1 3 7c0-2 1-4 3-4Z",
  person: "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
  edit: "m4 20 4.5-1 10-10-3.5-3.5-10 10L4 20Zm9.5-13.5L17 10",
};

function SchedulerIcon({ name, className = "h-5 w-5" }: { name: keyof typeof paths; className?: string }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="none"><path d={paths[name]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

function localDateKey(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function parseDate(value: string) {
  return new Date(`${value}T00:00:00`);
}

function interviewTime(interview: Interview) {
  return new Date(`${interview.date}T${interview.startTime}`).getTime();
}

function formatDate(value: string, options?: Intl.DateTimeFormatOptions) {
  return new Intl.DateTimeFormat("en-US", options ?? { month: "short", day: "numeric", year: "numeric" }).format(parseDate(value));
}

function formatTime(value: string) {
  const [hours, minutes] = value.split(":").map(Number);
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(new Date(2025, 0, 1, hours, minutes));
}

function initials(name: string) {
  return name === "Not found" ? "NA" : name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function candidateKey(item: AnalysisResult) {
  if (item.candidateId) return item.candidateId;
  if (item.candidate.email !== "Not found") return item.candidate.email.toLowerCase();
  if (item.candidate.phone !== "Not found") return item.candidate.phone.replace(/\D/g, "");
  return `${item.fileName}:${item.candidate.name}`;
}

function blankInterview(): Omit<Interview, "id" | "createdAt" | "updatedAt" | "history"> {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return {
    candidateId: "",
    candidateName: "",
    candidateEmail: "",
    candidatePhone: "",
    jobRoleId: "",
    jobRoleTitle: "",
    date: localDateKey(tomorrow),
    startTime: "10:00",
    endTime: "10:45",
    type: "Online",
    interviewerName: "",
    interviewerEmail: "",
    meetingLink: "",
    location: "",
    notes: "",
    preparation: "",
    feedback: "",
    status: "Scheduled",
  };
}

export default function InterviewScheduler({ openCreate = false, onOpenCandidate }: Props) {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  const [dateRange, setDateRange] = useState<DateRange>("Next 30 Days");
  const [statusFilter, setStatusFilter] = useState("All Statuses");
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [roleFilter, setRoleFilter] = useState("All Roles");
  const [sort, setSort] = useState<"date" | "candidate">("date");
  const [page, setPage] = useState(1);
  const [view, setView] = useState<CalendarView>("Month");
  const [viewDate, setViewDate] = useState(new Date());
  const [form, setForm] = useState(blankInterview());
  const [editing, setEditing] = useState<Interview | null>(null);
  const [rescheduling, setRescheduling] = useState(false);
  const [showForm, setShowForm] = useState(openCreate);
  const [detail, setDetail] = useState<Interview | null>(null);
  const [cancelTarget, setCancelTarget] = useState<Interview | null>(null);
  const [feedback, setFeedback] = useState("");
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [savedInterviews, savedAnalyses, savedRoles] = await Promise.all([
        getInterviews(),
        getSavedAnalyses(),
        getJobRoles(),
      ]);
      setInterviews(savedInterviews);
      setAnalyses(savedAnalyses);
      setRoles(savedRoles);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Interview data could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    const reload = () => void load();
    window.addEventListener(INTERVIEWS_CHANGED_EVENT, reload);
    return () => window.removeEventListener(INTERVIEWS_CHANGED_EVENT, reload);
  }, []);

  const candidates = useMemo(() => {
    const latest = new Map<string, AnalysisResult>();
    analyses.forEach((item) => {
      const key = candidateKey(item);
      const existing = latest.get(key);
      if (!existing || existing.createdAt < item.createdAt) latest.set(key, item);
    });
    return [...latest.values()];
  }, [analyses]);

  const rangeFiltered = useMemo(() => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const limit = new Date(now);
    if (dateRange === "Next 7 Days") limit.setDate(limit.getDate() + 7);
    if (dateRange === "Next 30 Days") limit.setDate(limit.getDate() + 30);
    if (dateRange === "Next 90 Days") limit.setDate(limit.getDate() + 90);
    return interviews.filter((item) => {
      const date = parseDate(item.date);
      return dateRange === "All Time" || (date >= now && date <= limit);
    });
  }, [dateRange, interviews]);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return rangeFiltered
      .filter((item) =>
        (!normalized || `${item.candidateName} ${item.jobRoleTitle} ${item.interviewerName} ${item.interviewerEmail}`.toLowerCase().includes(normalized)) &&
        (statusFilter === "All Statuses" || item.status === statusFilter) &&
        (typeFilter === "All Types" || item.type === typeFilter) &&
        (roleFilter === "All Roles" || item.jobRoleTitle === roleFilter),
      )
      .sort((a, b) => sort === "candidate" ? a.candidateName.localeCompare(b.candidateName) : interviewTime(a) - interviewTime(b));
  }, [query, rangeFiltered, roleFilter, sort, statusFilter, typeFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const now = Date.now();
  const upcoming = rangeFiltered.filter((item) => interviewTime(item) >= now && !["Completed", "Cancelled"].includes(item.status)).length;
  const completed = rangeFiltered.filter((item) => item.status === "Completed").length;
  const changed = rangeFiltered.filter((item) => ["Rescheduled", "Cancelled"].includes(item.status)).length;

  const calendarDays = useMemo(() => {
    if (view === "Day") return [new Date(viewDate)];
    if (view === "Week") {
      const start = new Date(viewDate);
      const day = start.getDay() || 7;
      start.setDate(start.getDate() - day + 1);
      return Array.from({ length: 7 }, (_, index) => {
        const date = new Date(start);
        date.setDate(start.getDate() + index);
        return date;
      });
    }
    const start = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1);
    start.setDate(start.getDate() - start.getDay());
    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(start);
      date.setDate(start.getDate() + index);
      return date;
    });
  }, [view, viewDate]);

  function flash(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2700);
  }

  function openNew(date?: string) {
    setEditing(null);
    setRescheduling(false);
    setForm({ ...blankInterview(), ...(date ? { date } : {}) });
    setShowForm(true);
  }

  function openEdit(interview: Interview, reschedule = false) {
    setEditing(interview);
    setRescheduling(reschedule);
    setForm({
      candidateId: interview.candidateId,
      candidateName: interview.candidateName,
      candidateEmail: interview.candidateEmail,
      candidatePhone: interview.candidatePhone,
      jobRoleId: interview.jobRoleId,
      jobRoleTitle: interview.jobRoleTitle,
      date: interview.date,
      startTime: interview.startTime,
      endTime: interview.endTime,
      type: interview.type,
      interviewerName: interview.interviewerName,
      interviewerEmail: interview.interviewerEmail,
      meetingLink: interview.meetingLink,
      location: interview.location,
      notes: interview.notes,
      preparation: interview.preparation,
      feedback: interview.feedback,
      status: interview.status,
    });
    setDetail(null);
    setOpenMenu(null);
    setShowForm(true);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const candidate = candidates.find((item) => candidateKey(item) === form.candidateId);
    const role = roles.find((item) => item.id === form.jobRoleId);
    if (!candidate || !role || !form.date || !form.startTime || !form.endTime || !form.type || !form.interviewerName.trim() || !form.interviewerEmail.trim()) {
      setError("Complete the candidate, job role, date, time, interview type, and interviewer fields.");
      return;
    }
    if (form.endTime <= form.startTime) {
      setError("End time must be later than the start time.");
      return;
    }
    if (form.type === "Online") {
      try {
        const url = new URL(form.meetingLink);
        if (!["http:", "https:"].includes(url.protocol)) throw new Error();
      } catch {
        setError("Add a valid HTTPS meeting link for an online interview.");
        return;
      }
    }
    const conflict = interviews.find((item) =>
      item.id !== editing?.id &&
      item.status !== "Cancelled" &&
      item.date === form.date &&
      item.interviewerEmail.toLowerCase() === form.interviewerEmail.trim().toLowerCase() &&
      form.startTime < item.endTime &&
      form.endTime > item.startTime,
    );
    if (conflict) {
      setError(`${form.interviewerName} already has an overlapping interview with ${conflict.candidateName}.`);
      return;
    }
    const timestamp = new Date().toISOString();
    const changedSchedule = editing && (editing.date !== form.date || editing.startTime !== form.startTime || editing.endTime !== form.endTime);
    const history = editing ? [...editing.history] : [];
    if (changedSchedule) history.push({ at: timestamp, action: "Interview rescheduled", previousDate: editing.date, previousStartTime: editing.startTime, previousEndTime: editing.endTime });
    const record: Interview = {
      ...form,
      id: editing?.id ?? `interview-${crypto.randomUUID()}`,
      candidateName: candidate.candidate.name,
      candidateEmail: candidate.candidate.email,
      candidatePhone: candidate.candidate.phone,
      jobRoleTitle: role.title,
      status: changedSchedule || rescheduling ? "Rescheduled" : editing?.status ?? "Scheduled",
      history: editing ? history : [{ at: timestamp, action: "Interview scheduled" }],
      createdAt: editing?.createdAt ?? timestamp,
      updatedAt: timestamp,
    };
    try {
      await saveInterview(record);
      setShowForm(false);
      setEditing(null);
      flash(changedSchedule || rescheduling ? "Interview rescheduled successfully." : editing ? "Interview updated successfully." : "Interview scheduled successfully.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "The interview could not be saved.");
    }
  }

  async function setStatus(interview: Interview, status: InterviewStatus, action: string) {
    const timestamp = new Date().toISOString();
    const updated = {
      ...interview,
      status,
      updatedAt: timestamp,
      history: [...interview.history, { at: timestamp, action }],
    };
    await saveInterview(updated);
    setDetail(updated);
    setOpenMenu(null);
    flash(action);
  }

  async function confirmCancel() {
    if (!cancelTarget) return;
    await setStatus(cancelTarget, "Cancelled", "Interview cancelled");
    setCancelTarget(null);
    setDetail(null);
  }

  async function saveFeedback() {
    if (!detail) return;
    const timestamp = new Date().toISOString();
    const updated = { ...detail, feedback: feedback.trim(), updatedAt: timestamp, history: [...detail.history, { at: timestamp, action: "Interview feedback updated" }] };
    await saveInterview(updated);
    setDetail(updated);
    flash("Interview feedback saved.");
  }

  function navigateCalendar(direction: number) {
    const next = new Date(viewDate);
    if (view === "Month") next.setMonth(next.getMonth() + direction);
    if (view === "Week") next.setDate(next.getDate() + direction * 7);
    if (view === "Day") next.setDate(next.getDate() + direction);
    setViewDate(next);
  }

  function exportSchedule() {
    if (!filtered.length) {
      flash("No interview records are available to export.");
      return;
    }
    const headings = ["Candidate", "Email", "Job Role", "Date", "Start Time", "End Time", "Type", "Interviewer", "Interviewer Email", "Status"];
    const rows = filtered.map((item) => [item.candidateName, item.candidateEmail, item.jobRoleTitle, item.date, item.startTime, item.endTime, item.type, item.interviewerName, item.interviewerEmail, item.status]);
    const quote = (value: string) => `"${value.replaceAll('"', '""')}"`;
    const csv = [headings, ...rows].map((row) => row.map(quote).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "talentflow-interview-schedule.csv";
    link.click();
    URL.revokeObjectURL(url);
    flash(`${filtered.length} interview records exported.`);
  }

  if (loading) return <div className="analytics-loading"><span className="candidate-loader" /><h2>Loading interview schedule</h2><p>Retrieving candidate, role, and interview records...</p></div>;

  return (
    <>
      {notice && <div className="dashboard-toast">{notice}</div>}
      <div className="analyzer-breadcrumb"><span>Dashboard</span><span>/</span><b>Interview Scheduler</b></div>
      <div className="scheduler-heading">
        <div><h1>Interview Scheduler</h1><p>Schedule interviews, manage upcoming meetings, and track interview progress.</p></div>
        <div className="scheduler-heading-actions">
          <select value={dateRange} onChange={(event) => setDateRange(event.target.value as DateRange)}>{["Next 7 Days", "Next 30 Days", "Next 90 Days", "All Time"].map((item) => <option key={item}>{item}</option>)}</select>
          <button type="button" className="secondary-action" onClick={exportSchedule}><SchedulerIcon name="export" className="h-4 w-4" />Export Schedule</button>
          <button type="button" className="primary-action" onClick={() => openNew()}><SchedulerIcon name="plus" className="h-4 w-4" />Schedule Interview</button>
        </div>
      </div>

      {error && <div className="analysis-alert error"><b>Unable to continue</b><span>{error}</span><button type="button" onClick={() => setError("")}>Dismiss</button></div>}

      <div className="scheduler-search-row">
        <div className="candidate-search-field"><SchedulerIcon name="search" className="h-4 w-4" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search candidates, job roles, or interviewers..." /></div>
        <p><b>{dateRange}</b> · {rangeFiltered.length} records included</p>
      </div>

      <section className="scheduler-kpi-grid">
        {[
          ["Total Interviews", rangeFiltered.length, "Within the selected period", "calendar", "blue"],
          ["Upcoming Interviews", upcoming, "Scheduled for the future", "upcoming", "teal"],
          ["Completed Interviews", completed, "Marked as completed", "check", "purple"],
          ["Rescheduled / Cancelled", changed, "Schedule changes in period", "alert", "amber"],
        ].map(([label, value, detailText, icon, tone]) => <article key={label as string} className="analytics-kpi-card"><div className={`metric-icon ${tone}`}><SchedulerIcon name={icon as keyof typeof paths} /></div><div><span>{label}</span><strong>{value}</strong><small>{detailText}</small></div></article>)}
      </section>

      <section className="scheduler-calendar-card">
        <div className="scheduler-calendar-toolbar">
          <div><button type="button" onClick={() => navigateCalendar(-1)} aria-label="Previous period"><SchedulerIcon name="left" className="h-4 w-4" /></button><button type="button" onClick={() => setViewDate(new Date())}>Today</button><button type="button" onClick={() => navigateCalendar(1)} aria-label="Next period"><SchedulerIcon name="right" className="h-4 w-4" /></button></div>
          <h2>{view === "Month" ? new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" }).format(viewDate) : view === "Week" ? `Week of ${formatDate(localDateKey(calendarDays[0]), { month: "short", day: "numeric" })}` : new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric" }).format(viewDate)}</h2>
          <div className="calendar-view-toggle">{(["Month", "Week", "Day"] as CalendarView[]).map((item) => <button type="button" key={item} className={view === item ? "active" : ""} onClick={() => setView(item)}>{item}</button>)}</div>
        </div>
        <div className={`scheduler-calendar-grid view-${view.toLowerCase()}`}>
          {view !== "Day" && calendarDays.slice(0, view === "Month" ? 7 : calendarDays.length).map((date) => <div key={`head-${localDateKey(date)}`} className="calendar-day-head">{new Intl.DateTimeFormat("en-US", { weekday: "short" }).format(date)}</div>)}
          {calendarDays.map((date) => {
            const key = localDateKey(date);
            const events = interviews.filter((item) => item.date === key);
            const outside = view === "Month" && date.getMonth() !== viewDate.getMonth();
            return <div key={key} className={`calendar-cell ${outside ? "outside" : ""} ${key === localDateKey(new Date()) ? "today" : ""}`} onDoubleClick={() => openNew(key)}>
              <button type="button" className="calendar-date" onClick={() => { setViewDate(date); if (view === "Month") setView("Day"); }}>{view === "Day" ? new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric" }).format(date) : date.getDate()}</button>
              <div className="calendar-events">{events.slice(0, view === "Month" ? 3 : 8).map((event) => <button type="button" key={event.id} className={`calendar-event status-${event.status.toLowerCase()}`} onClick={() => { setDetail(event); setFeedback(event.feedback); }}><span>{formatTime(event.startTime)}</span><b>{event.candidateName}</b><small>{event.jobRoleTitle}</small></button>)}{events.length > 3 && view === "Month" && <span className="calendar-more">+{events.length - 3} more</span>}</div>
            </div>;
          })}
        </div>
        {!interviews.length && <div className="calendar-empty"><SchedulerIcon name="calendar" /><h3>No interviews scheduled</h3><p>Choose Schedule Interview or double-click a calendar date to add the first meeting.</p><button type="button" className="primary-action" onClick={() => openNew()}>Schedule Interview</button></div>}
      </section>

      <section className="scheduler-table-card">
        <div className="scheduler-table-heading"><div><h2>Upcoming Interviews</h2><p>{filtered.length} matching interview {filtered.length === 1 ? "record" : "records"}</p></div><div>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>{["All Statuses", ...statuses].map((item) => <option key={item}>{item}</option>)}</select>
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>{["All Types", "Online", "In-person", "Phone"].map((item) => <option key={item}>{item}</option>)}</select>
          <select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}><option>All Roles</option>{roles.map((item) => <option key={item.id}>{item.title}</option>)}</select>
        </div></div>
        {!filtered.length ? <div className="candidate-state"><div className="candidate-state-icon"><SchedulerIcon name="calendar" /></div><h3>No interviews match this view</h3><p>Adjust the reporting period or filters, or schedule a new interview.</p></div> : <>
          <div className="candidate-table-wrap"><table className="scheduler-table"><thead><tr><th><button type="button" onClick={() => setSort("candidate")}>Candidate Name ↕</button></th><th>Job Role</th><th><button type="button" onClick={() => setSort("date")}>Interview Date ↕</button></th><th>Time</th><th>Type</th><th>Interviewer</th><th>Status</th><th>Actions</th></tr></thead><tbody>{visible.map((item, index) => <tr key={item.id}>
            <td><div className="candidate-person"><span className={`candidate-avatar ${["mint", "purple", "amber", "blue"][index % 4]}`}>{initials(item.candidateName)}</span><div><b>{item.candidateName}</b><span>{item.candidateEmail}</span></div></div></td>
            <td><b className="role-name">{item.jobRoleTitle}</b></td><td><b className="date-label">{formatDate(item.date)}</b></td><td>{formatTime(item.startTime)}–{formatTime(item.endTime)}</td>
            <td><span className={`interview-type type-${item.type.toLowerCase().replace("-", "")}`}><SchedulerIcon name={item.type === "Online" ? "video" : item.type === "Phone" ? "phone" : "location"} className="h-3 w-3" />{item.type}</span></td>
            <td><b className="interviewer-name">{item.interviewerName}</b><span className="table-subtext">{item.interviewerEmail}</span></td><td><span className={`interview-status status-${item.status.toLowerCase()}`}>{item.status}</span></td>
            <td><div className="candidate-actions"><button type="button" className="profile-button" onClick={() => { setDetail(item); setFeedback(item.feedback); }}>View</button><button type="button" className="more-button" onClick={() => setOpenMenu(openMenu === item.id ? null : item.id)}>•••</button>{openMenu === item.id && <div className="row-menu"><button type="button" onClick={() => { setDetail(item); setOpenMenu(null); }}>View Details</button><button type="button" onClick={() => openEdit(item)}>Edit</button><button type="button" onClick={() => openEdit(item, true)}>Reschedule</button><button type="button" onClick={() => void setStatus(item, "Completed", "Interview marked completed")}>Mark Completed</button><button type="button" className="danger" onClick={() => { setCancelTarget(item); setOpenMenu(null); }}>Cancel Interview</button></div>}</div></td>
          </tr>)}</tbody></table></div>
          <div className="candidate-pagination"><p>Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}</p><div><button type="button" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><button type="button" className="active">{page}</button><button type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}>Next</button></div></div>
        </>}
      </section>

      {showForm && <div className="candidate-modal" role="dialog" aria-modal="true" aria-label={editing ? "Edit interview" : "Schedule interview"}><button type="button" className="candidate-modal-backdrop" onClick={() => setShowForm(false)} /><form className="interview-form-panel" onSubmit={(event) => void submit(event)}>
        <div className="profile-topbar"><div><span>{rescheduling ? "Reschedule Interview" : editing ? "Edit Interview" : "Schedule Interview"}</span><p>Coordinate the candidate, role, interviewer, and meeting details.</p></div><button type="button" onClick={() => setShowForm(false)}><SchedulerIcon name="close" /></button></div>
        <div className="interview-form-content">
          <section><h2>Candidate and role</h2><div className="role-form-grid"><label className="role-form-field"><span>Candidate *</span><select required value={form.candidateId} onChange={(event) => setForm({ ...form, candidateId: event.target.value })}><option value="">Select candidate</option>{candidates.map((item) => <option key={candidateKey(item)} value={candidateKey(item)}>{item.candidate.name} · {item.candidate.email}</option>)}</select></label><label className="role-form-field"><span>Job Role *</span><select required value={form.jobRoleId} onChange={(event) => setForm({ ...form, jobRoleId: event.target.value })}><option value="">Select job role</option>{roles.map((item) => <option key={item.id} value={item.id}>{item.title} · {item.status}</option>)}</select></label></div>{!candidates.length && <p className="form-help error">No saved candidates are available. Save a resume analysis first.</p>}{!roles.length && <p className="form-help error">No job roles are available. Create a job role first.</p>}</section>
          <section><h2>Date and time</h2><div className="interview-form-grid"><label className="role-form-field"><span>Interview Date *</span><input required type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} /></label><label className="role-form-field"><span>Start Time *</span><input required type="time" value={form.startTime} onChange={(event) => setForm({ ...form, startTime: event.target.value })} /></label><label className="role-form-field"><span>End Time *</span><input required type="time" value={form.endTime} onChange={(event) => setForm({ ...form, endTime: event.target.value })} /></label><label className="role-form-field"><span>Interview Type *</span><select value={form.type} onChange={(event) => setForm({ ...form, type: event.target.value as InterviewType })}>{["Online", "In-person", "Phone"].map((item) => <option key={item}>{item}</option>)}</select></label></div></section>
          <section><h2>Interviewer and meeting</h2><div className="role-form-grid"><label className="role-form-field"><span>Interviewer Name *</span><input required value={form.interviewerName} onChange={(event) => setForm({ ...form, interviewerName: event.target.value })} placeholder="Full name" /></label><label className="role-form-field"><span>Interviewer Email *</span><input required type="email" value={form.interviewerEmail} onChange={(event) => setForm({ ...form, interviewerEmail: event.target.value })} placeholder="name@company.com" /></label>{form.type === "Online" && <label className="role-form-field role-form-wide"><span>Meeting Link *</span><input required type="url" value={form.meetingLink} onChange={(event) => setForm({ ...form, meetingLink: event.target.value })} placeholder="https://meet.example.com/..." /></label>}{form.type === "In-person" && <label className="role-form-field role-form-wide"><span>Location *</span><input required value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} placeholder="Office, room, and address" /></label>}</div></section>
          <section><h2>Notes and preparation</h2><div className="role-form-grid"><label className="role-form-field role-form-wide"><span>Interview Notes</span><textarea rows={4} value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} placeholder="Agenda, topics, or internal notes..." /></label><label className="role-form-field role-form-wide"><span>Preparation Instructions</span><textarea rows={3} value={form.preparation} onChange={(event) => setForm({ ...form, preparation: event.target.value })} placeholder="Optional instructions for the candidate or interviewer..." /></label></div></section>
        </div><div className="role-form-actions"><button type="button" className="secondary-action" onClick={() => setShowForm(false)}>Cancel</button><button type="submit" className="primary-action" disabled={!candidates.length || !roles.length}>Save Interview</button></div>
      </form></div>}

      {detail && <div className="candidate-modal" role="dialog" aria-modal="true" aria-label="Interview details"><button type="button" className="candidate-modal-backdrop" onClick={() => setDetail(null)} /><section className="interview-detail-panel">
        <div className="profile-topbar"><div><span>Interview Details</span><p>Created {new Date(detail.createdAt).toLocaleString()}</p></div><button type="button" onClick={() => setDetail(null)}><SchedulerIcon name="close" /></button></div>
        <div className="interview-detail-hero"><span className="profile-avatar">{initials(detail.candidateName)}</span><div><span className={`interview-status status-${detail.status.toLowerCase()}`}>{detail.status}</span><h2>{detail.candidateName}</h2><p>{detail.candidateEmail} · {detail.candidatePhone}</p></div><div><strong>{formatDate(detail.date, { weekday: "short", month: "short", day: "numeric" })}</strong><span>{formatTime(detail.startTime)}–{formatTime(detail.endTime)}</span></div></div>
        <div className="interview-detail-actions"><button type="button" className="secondary-action" onClick={() => openEdit(detail)}>Edit</button><button type="button" className="secondary-action" onClick={() => openEdit(detail, true)}>Reschedule</button><button type="button" className="primary-action" disabled={detail.status === "Completed"} onClick={() => void setStatus(detail, "Completed", "Interview marked completed")}>Mark Completed</button><button type="button" className="cancel-interview-action" disabled={detail.status === "Cancelled"} onClick={() => setCancelTarget(detail)}>Cancel</button></div>
        <div className="interview-detail-content">
          <article><h3>Meeting Overview</h3><div className="interview-overview-grid"><span><small>Job Role</small><b>{detail.jobRoleTitle}</b></span><span><small>Interview Type</small><b>{detail.type}</b></span><span><small>Interviewer</small><b>{detail.interviewerName}</b><em>{detail.interviewerEmail}</em></span><span><small>{detail.type === "Online" ? "Meeting Link" : detail.type === "In-person" ? "Location" : "Contact"}</small><b>{detail.type === "Online" ? detail.meetingLink : detail.type === "In-person" ? detail.location : detail.candidatePhone}</b></span></div></article>
          <article><h3>Notes and Preparation</h3><div className="detail-copy"><span><b>Interview notes</b><p>{detail.notes || "Not provided"}</p></span><span><b>Preparation instructions</b><p>{detail.preparation || "Not provided"}</p></span></div></article>
          {detail.status === "Completed" && <article><h3>Interview Feedback</h3><textarea rows={5} value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="Optional interview feedback and follow-up notes..." /><button type="button" className="secondary-action" onClick={() => void saveFeedback()}>Save Feedback</button></article>}
          <article><h3>Interview History</h3><div className="interview-history">{detail.history.slice().reverse().map((entry, index) => <span key={`${entry.at}-${index}`}><i /><div><b>{entry.action}</b><small>{new Date(entry.at).toLocaleString()}</small>{entry.previousDate && <em>Previously {formatDate(entry.previousDate)} · {formatTime(entry.previousStartTime ?? "")}–{formatTime(entry.previousEndTime ?? "")}</em>}</div></span>)}</div></article>
        </div><div className="role-context-actions"><button type="button" onClick={() => { const candidate = analyses.find((item) => candidateKey(item) === detail.candidateId); if (candidate) onOpenCandidate(candidate); }}>Open Candidate Profile</button><span>Last updated {new Date(detail.updatedAt).toLocaleString()}</span></div>
      </section></div>}

      {cancelTarget && <div className="confirm-overlay" role="alertdialog" aria-modal="true"><button type="button" className="candidate-modal-backdrop" onClick={() => setCancelTarget(null)} /><section className="confirm-dialog"><div className="confirm-icon"><SchedulerIcon name="alert" /></div><h2>Cancel this interview?</h2><p>The meeting with <b>{cancelTarget.candidateName}</b> will remain in interview history and be marked cancelled.</p><div><button type="button" className="secondary-action" onClick={() => setCancelTarget(null)}>Keep Interview</button><button type="button" className="danger-action" onClick={() => void confirmCancel()}>Cancel Interview</button></div></section></div>}
    </>
  );
}
