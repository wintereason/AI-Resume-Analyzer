import { useEffect, useMemo, useState } from "react";
import { jsPDF } from "jspdf";
import {
  ANALYSES_CHANGED_EVENT,
  getSavedAnalyses,
} from "./lib/analysisStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";

type Props = {
  onAnalyze: () => void;
  onOpenCandidate: (analysis: AnalysisResult) => void;
  onOpenCandidates: (filters?: { role?: string; match?: string }) => void;
};

type DateRange =
  | "Last 7 Days"
  | "Last 30 Days"
  | "Last 90 Days"
  | "This Year"
  | "All Time"
  | "Custom Range";

const STATUS_OPTIONS = ["All Statuses", "New", "Shortlisted", "Interview Scheduled", "Rejected"];
const MATCH_OPTIONS = ["All Categories", "Strong Match", "Moderate Match", "Low Match"];
const COLORS = {
  teal: "#16ad99",
  purple: "#7868cf",
  amber: "#e3a52e",
  coral: "#df6a67",
  blue: "#4f91d2",
};

const iconPaths = {
  people:
    "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm5-1a2.5 2.5 0 0 0 0-5M19 15c1.5.6 2.5 2 2.5 3.5",
  target: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-4a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0-4a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z",
  star: "m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z",
  check: "m6 12 4 4 8-9",
  refresh: "M20 7v5h-5M4 17v-5h5m10.3-3A8 8 0 0 0 6.2 6.2L4 9m16 6-2.2 2.8A8 8 0 0 1 4.7 15",
  export: "M12 4v11m0-11L8 8m4-4 4 4M5 14v5h14v-5",
  filter: "M4 6h16M7 12h10m-7 6h4",
  chart: "M4 20V10m5 10V4m5 16v-7m5 7V7",
  activity: "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  chevron: "m9 7 5 5-5 5",
};

function AnalyticsIcon({
  name,
  className = "h-5 w-5",
}: {
  name: keyof typeof iconPaths;
  className?: string;
}) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="none">
      <path
        d={iconPaths[name]}
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function candidateKey(analysis: AnalysisResult) {
  if (analysis.candidate.email !== "Not found") return analysis.candidate.email.toLowerCase();
  if (analysis.candidate.phone !== "Not found") return analysis.candidate.phone.replace(/\D/g, "");
  return `${analysis.fileName.toLowerCase()}:${analysis.candidate.name.toLowerCase()}`;
}

function csvCell(value: string | number) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

function downloadCsv(fileName: string, headings: string[], rows: (string | number)[][]) {
  const csv = [headings, ...rows].map((row) => row.map(csvCell).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function formatShortDate(date: Date) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(date);
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="analytics-chart-empty">
      <AnalyticsIcon name="chart" />
      <p>{message}</p>
    </div>
  );
}

function RankedBars({
  rows,
  tone,
  onSelect,
  emptyMessage,
}: {
  rows: { label: string; value: number; supporting?: string }[];
  tone: "teal" | "purple" | "amber" | "coral" | "blue";
  onSelect?: (label: string) => void;
  emptyMessage: string;
}) {
  const maximum = Math.max(...rows.map((row) => row.value), 1);
  if (!rows.length) return <EmptyChart message={emptyMessage} />;
  return (
    <div className={`ranked-bars ${tone}`}>
      {rows.map((row, index) => (
        <button
          type="button"
          key={row.label}
          onClick={() => onSelect?.(row.label)}
          disabled={!onSelect}
        >
          <span className="rank-number">{index + 1}</span>
          <span className="rank-content">
            <span>
              <b>{row.label}</b>
              <em>{row.supporting}</em>
              <strong>{row.value}</strong>
            </span>
            <svg viewBox="0 0 100 5" preserveAspectRatio="none" aria-hidden="true">
              <rect width="100" height="5" rx="2.5" className="bar-track" />
              <rect width={(row.value / maximum) * 100} height="5" rx="2.5" className="bar-value" />
            </svg>
          </span>
        </button>
      ))}
    </div>
  );
}

export default function RecruitmentAnalytics({
  onAnalyze,
  onOpenCandidate,
  onOpenCandidates,
}: Props) {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [dateRange, setDateRange] = useState<DateRange>("Last 30 Days");
  const [role, setRole] = useState("All Roles");
  const [candidateStatus, setCandidateStatus] = useState("All Statuses");
  const [matchCategory, setMatchCategory] = useState("All Categories");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [showExport, setShowExport] = useState(false);

  async function loadData(showSuccess = false) {
    setLoading(true);
    setError("");
    try {
      setAnalyses(await getSavedAnalyses());
      if (showSuccess) {
        setNotice("Analytics refreshed with the latest saved candidate data.");
        window.setTimeout(() => setNotice(""), 2600);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Analytics could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
    const reload = () => void loadData();
    window.addEventListener(ANALYSES_CHANGED_EVENT, reload);
    return () => window.removeEventListener(ANALYSES_CHANGED_EVENT, reload);
  }, []);

  const roles = useMemo(
    () => ["All Roles", ...Array.from(new Set(analyses.map((item) => item.role))).sort()],
    [analyses],
  );

  const period = useMemo(() => {
    const now = new Date();
    const end = dateRange === "Custom Range" && customEnd ? new Date(`${customEnd}T23:59:59`) : now;
    let start: Date | null = null;
    if (dateRange === "Last 7 Days") start = new Date(now.getTime() - 6 * 86_400_000);
    if (dateRange === "Last 30 Days") start = new Date(now.getTime() - 29 * 86_400_000);
    if (dateRange === "Last 90 Days") start = new Date(now.getTime() - 89 * 86_400_000);
    if (dateRange === "This Year") start = new Date(now.getFullYear(), 0, 1);
    if (dateRange === "Custom Range" && customStart) start = new Date(`${customStart}T00:00:00`);
    return { start, end };
  }, [customEnd, customStart, dateRange]);

  const filtered = useMemo(
    () =>
      analyses.filter((analysis) => {
        const created = new Date(analysis.createdAt);
        return (
          (!period.start || created >= period.start) &&
          created <= period.end &&
          (role === "All Roles" || analysis.role === role) &&
          (candidateStatus === "All Statuses" ||
            (analysis.recruitmentStatus ?? "New") === candidateStatus) &&
          (matchCategory === "All Categories" || analysis.status === matchCategory)
        );
      }),
    [analyses, candidateStatus, matchCategory, period, role],
  );

  const uniqueCandidates = useMemo(() => {
    const latest = new Map<string, AnalysisResult>();
    filtered.forEach((analysis) => {
      const key = candidateKey(analysis);
      const existing = latest.get(key);
      if (!existing || existing.createdAt < analysis.createdAt) latest.set(key, analysis);
    });
    return [...latest.values()];
  }, [filtered]);

  const averageScore = filtered.length
    ? Math.round(filtered.reduce((total, item) => total + item.score, 0) / filtered.length)
    : 0;
  const strongCount = uniqueCandidates.filter((item) => item.score >= 75).length;
  const shortlistedCount = uniqueCandidates.filter(
    (item) => (item.recruitmentStatus ?? "New") === "Shortlisted",
  ).length;

  const matchDistribution = ["Strong Match", "Moderate Match", "Low Match"].map((label) => ({
    label,
    value: uniqueCandidates.filter((item) => item.status === label).length,
    color:
      label === "Strong Match"
        ? COLORS.teal
        : label === "Moderate Match"
          ? COLORS.amber
          : COLORS.coral,
  }));

  const statusDistribution = ["New", "Shortlisted", "Interview Scheduled", "Rejected"].map(
    (label) => ({
      label,
      value: uniqueCandidates.filter((item) => (item.recruitmentStatus ?? "New") === label)
        .length,
      color:
        label === "New"
          ? COLORS.blue
          : label === "Shortlisted"
            ? COLORS.teal
            : label === "Interview Scheduled"
              ? COLORS.purple
              : COLORS.coral,
    }),
  );

  const roleRows = useMemo(() => {
    const values = new Map<string, { count: number; score: number }>();
    filtered.forEach((item) => {
      const current = values.get(item.role) ?? { count: 0, score: 0 };
      values.set(item.role, { count: current.count + 1, score: current.score + item.score });
    });
    return [...values.entries()]
      .map(([label, value]) => ({
        label,
        value: value.count,
        supporting: `${Math.round(value.score / value.count)}% avg. match`,
      }))
      .sort((a, b) => b.value - a.value);
  }, [filtered]);

  function aggregateSkills(field: "matchedSkills" | "missingSkills") {
    const skills = new Map<string, { label: string; value: number }>();
    filtered.forEach((analysis) => {
      new Set(analysis[field].map((skill) => skill.trim().toLowerCase())).forEach((normalized) => {
        if (!normalized) return;
        const label =
          analysis[field].find((skill) => skill.trim().toLowerCase() === normalized)?.trim() ??
          normalized;
        const current = skills.get(normalized);
        skills.set(normalized, { label: current?.label ?? label, value: (current?.value ?? 0) + 1 });
      });
    });
    return [...skills.values()]
      .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label))
      .slice(0, 6)
      .map((item) => ({
        ...item,
        supporting: filtered.length
          ? `${Math.round((item.value / filtered.length) * 100)}% of analyses`
          : "",
      }));
  }

  const matchedSkills = aggregateSkills("matchedSkills");
  const missingSkills = aggregateSkills("missingSkills");

  const trend = useMemo(() => {
    if (!filtered.length) return [];
    const useDays =
      dateRange === "Last 7 Days" ||
      dateRange === "Last 30 Days" ||
      (dateRange === "Custom Range" &&
        period.start &&
        (period.end.getTime() - period.start.getTime()) / 86_400_000 <= 31);
    const counts = new Map<string, number>();
    filtered.forEach((item) => {
      const date = new Date(item.createdAt);
      const key = useDays
        ? `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
        : `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      counts.set(key, (counts.get(key) ?? 0) + 1);
    });
    const start = period.start ?? new Date(Math.min(...filtered.map((item) => new Date(item.createdAt).getTime())));
    const cursor = new Date(start);
    const end = period.end;
    const points: { key: string; label: string; value: number }[] = [];
    while (cursor <= end && points.length < 120) {
      const key = useDays
        ? `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}-${String(cursor.getDate()).padStart(2, "0")}`
        : `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}`;
      points.push({
        key,
        label: useDays
          ? formatShortDate(cursor)
          : new Intl.DateTimeFormat("en-US", { month: "short", year: "2-digit" }).format(cursor),
        value: counts.get(key) ?? 0,
      });
      if (useDays) cursor.setDate(cursor.getDate() + 1);
      else cursor.setMonth(cursor.getMonth() + 1, 1);
    }
    return points;
  }, [dateRange, filtered, period]);

  const trendMaximum = Math.max(...trend.map((point) => point.value), 1);
  const trendCoordinates = trend.map((point, index) => ({
    ...point,
    x: trend.length === 1 ? 50 : 4 + (index / (trend.length - 1)) * 92,
    y: 82 - (point.value / trendMaximum) * 64,
  }));
  const trendPath = trendCoordinates.map((point) => `${point.x},${point.y}`).join(" ");

  const periodLabel =
    dateRange === "Custom Range"
      ? `${customStart || "Start"} – ${customEnd || "Today"}`
      : dateRange;

  function clearFilters() {
    setDateRange("Last 30 Days");
    setRole("All Roles");
    setCandidateStatus("All Statuses");
    setMatchCategory("All Categories");
    setCustomStart("");
    setCustomEnd("");
  }

  function exportSummary() {
    downloadCsv(
      "talentflow-analytics-summary.csv",
      ["Metric", "Value", "Reporting Period"],
      [
        ["Total Candidates Analyzed", uniqueCandidates.length, periodLabel],
        ["Saved Analyses", filtered.length, periodLabel],
        ["Average Match Score", `${averageScore}%`, periodLabel],
        ["Strong Matches", strongCount, periodLabel],
        ["Shortlisted Candidates", shortlistedCount, periodLabel],
      ],
    );
    setShowExport(false);
  }

  function exportChartData() {
    const rows: (string | number)[][] = [];
    matchDistribution.forEach((item) => rows.push(["Match Distribution", item.label, item.value]));
    statusDistribution.forEach((item) => rows.push(["Recruitment Status", item.label, item.value]));
    trend.forEach((item) => rows.push(["Analysis Trend", item.label, item.value]));
    roleRows.forEach((item) => rows.push(["Job Role", item.label, item.value]));
    matchedSkills.forEach((item) => rows.push(["Matched Skill", item.label, item.value]));
    missingSkills.forEach((item) => rows.push(["Missing Skill", item.label, item.value]));
    downloadCsv(
      "talentflow-analytics-chart-data.csv",
      ["Section", "Category", "Count"],
      rows,
    );
    setShowExport(false);
  }

  function exportPdf() {
    const pdf = new jsPDF();
    pdf.setTextColor(34, 41, 38);
    pdf.setFontSize(20);
    pdf.text("TalentFlow Recruitment Analytics", 18, 22);
    pdf.setFontSize(9);
    pdf.setTextColor(116, 124, 119);
    pdf.text(`Reporting period: ${periodLabel}`, 18, 30);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 18, 36);
    pdf.setTextColor(34, 41, 38);
    pdf.setFontSize(13);
    pdf.text("KPI Summary", 18, 49);
    pdf.setFontSize(10);
    [
      `Unique candidates analyzed: ${uniqueCandidates.length}`,
      `Saved analyses included: ${filtered.length}`,
      `Average estimated match score: ${averageScore}%`,
      `Strong matches: ${strongCount}`,
      `Shortlisted candidates: ${shortlistedCount}`,
    ].forEach((line, index) => pdf.text(line, 22, 59 + index * 7));
    pdf.setFontSize(13);
    pdf.text("Match Distribution", 18, 101);
    pdf.setFontSize(10);
    matchDistribution.forEach((item, index) => pdf.text(`${item.label}: ${item.value}`, 22, 111 + index * 7));
    pdf.setFontSize(13);
    pdf.text("Recruitment Status", 18, 139);
    pdf.setFontSize(10);
    statusDistribution.forEach((item, index) => pdf.text(`${item.label}: ${item.value}`, 22, 149 + index * 7));
    pdf.setFontSize(13);
    pdf.text("Top Job Roles", 18, 186);
    pdf.setFontSize(10);
    roleRows.slice(0, 6).forEach((item, index) => pdf.text(`${item.label}: ${item.value} analyses (${item.supporting})`, 22, 196 + index * 7));
    pdf.addPage();
    pdf.setFontSize(15);
    pdf.text("Skill Insights", 18, 22);
    pdf.setFontSize(12);
    pdf.text("Most Commonly Matched Skills", 18, 34);
    pdf.setFontSize(10);
    matchedSkills.forEach((item, index) => pdf.text(`${item.label}: ${item.value} (${item.supporting})`, 22, 44 + index * 7));
    pdf.setFontSize(12);
    pdf.text("Most Common Missing Skills", 18, 96);
    pdf.setFontSize(10);
    missingSkills.forEach((item, index) => pdf.text(`${item.label}: ${item.value} (${item.supporting})`, 22, 106 + index * 7));
    pdf.save("talentflow-recruitment-analytics.pdf");
    setShowExport(false);
  }

  if (loading) {
    return (
      <div className="analytics-loading">
        <span className="candidate-loader" />
        <h2>Loading recruitment analytics</h2>
        <p>Aggregating saved candidate and resume-analysis records...</p>
      </div>
    );
  }

  return (
    <>
      {notice && <div className="dashboard-toast">{notice}</div>}
      <div className="analyzer-breadcrumb">
        <span>Dashboard</span>
        <span>/</span>
        <b>Recruitment Analytics</b>
      </div>

      <div className="analytics-page-heading">
        <div>
          <h1>Recruitment Analytics</h1>
          <p>Explore candidate quality, recruitment progress, and skill insights.</p>
        </div>
        <div className="analytics-header-actions">
          <select
            value={dateRange}
            onChange={(event) => setDateRange(event.target.value as DateRange)}
            aria-label="Analytics date range"
          >
            {["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "All Time", "Custom Range"].map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <button type="button" className="secondary-action" onClick={() => void loadData(true)}>
            <AnalyticsIcon name="refresh" className="h-4 w-4" />
            Refresh Data
          </button>
          <div className="analytics-export-wrap">
            <button type="button" className="primary-action" onClick={() => setShowExport(!showExport)}>
              <AnalyticsIcon name="export" className="h-4 w-4" />
              Export Report
              <AnalyticsIcon name="chevron" className="h-3 w-3" />
            </button>
            {showExport && (
              <div className="analytics-export-menu">
                <button type="button" onClick={exportSummary}>Export summary as CSV</button>
                <button type="button" onClick={exportChartData}>Export chart data as CSV</button>
                <button type="button" onClick={exportPdf}>Download formatted PDF</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="analysis-alert error">
          <b>Analytics unavailable</b>
          <span>{error}</span>
          <button type="button" onClick={() => void loadData()}>Retry</button>
        </div>
      )}

      <section className="analytics-filter-card">
        <div className="analytics-filter-heading">
          <span><AnalyticsIcon name="filter" className="h-4 w-4" /> Global filters</span>
          <button type="button" onClick={clearFilters}>Clear filters</button>
        </div>
        <div className="analytics-filters">
          <label>
            <span>Date Range</span>
            <select value={dateRange} onChange={(event) => setDateRange(event.target.value as DateRange)}>
              {["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "All Time", "Custom Range"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            <span>Target Job Role</span>
            <select value={role} onChange={(event) => setRole(event.target.value)}>
              {roles.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            <span>Candidate Status</span>
            <select value={candidateStatus} onChange={(event) => setCandidateStatus(event.target.value)}>
              {STATUS_OPTIONS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            <span>Match Category</span>
            <select value={matchCategory} onChange={(event) => setMatchCategory(event.target.value)}>
              {MATCH_OPTIONS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          {dateRange === "Custom Range" && (
            <>
              <label>
                <span>Start Date</span>
                <input type="date" value={customStart} onChange={(event) => setCustomStart(event.target.value)} />
              </label>
              <label>
                <span>End Date</span>
                <input type="date" value={customEnd} onChange={(event) => setCustomEnd(event.target.value)} />
              </label>
            </>
          )}
        </div>
        <p className="analytics-filter-summary">
          <b>{periodLabel}</b>
          <span>·</span>
          {filtered.length} saved {filtered.length === 1 ? "analysis" : "analyses"} included
        </p>
      </section>

      {!analyses.length ? (
        <section className="analytics-empty-state">
          <div><AnalyticsIcon name="chart" className="h-7 w-7" /></div>
          <h2>Analytics will appear after resumes are saved</h2>
          <p>Analyze a candidate resume and save the result to begin tracking match quality, skills, roles, and recruitment progress.</p>
          <button type="button" className="primary-action" onClick={onAnalyze}>Analyze New Resume</button>
        </section>
      ) : !filtered.length ? (
        <section className="analytics-empty-state">
          <div><AnalyticsIcon name="filter" className="h-7 w-7" /></div>
          <h2>No records match these filters</h2>
          <p>Choose a broader reporting period or clear the active role, status, and match filters.</p>
          <button type="button" className="secondary-action" onClick={clearFilters}>Clear Filters</button>
        </section>
      ) : (
        <>
          <section className="analytics-kpi-grid">
            {[
              {
                label: "Total Candidates Analyzed",
                value: uniqueCandidates.length,
                detail: `${filtered.length} saved analyses in this view`,
                icon: "people" as const,
                tone: "teal",
              },
              {
                label: "Average Match Score",
                value: `${averageScore}%`,
                detail: "Average across filtered analyses",
                icon: "target" as const,
                tone: "blue",
                progress: averageScore,
              },
              {
                label: "Strong Matches",
                value: strongCount,
                detail: `${uniqueCandidates.length ? Math.round((strongCount / uniqueCandidates.length) * 100) : 0}% of analyzed candidates`,
                icon: "star" as const,
                tone: "purple",
              },
              {
                label: "Shortlisted Candidates",
                value: shortlistedCount,
                detail: `${uniqueCandidates.length ? Math.round((shortlistedCount / uniqueCandidates.length) * 100) : 0}% of filtered candidates`,
                icon: "check" as const,
                tone: "amber",
              },
            ].map((metric) => (
              <article className="analytics-kpi-card" key={metric.label}>
                <div className={`metric-icon ${metric.tone}`}><AnalyticsIcon name={metric.icon} /></div>
                <div>
                  <span>{metric.label}</span>
                  <strong>{metric.value}</strong>
                  {metric.progress !== undefined && (
                    <svg viewBox="0 0 100 4" preserveAspectRatio="none" aria-hidden="true">
                      <rect width="100" height="4" rx="2" className="kpi-track" />
                      <rect width={metric.progress} height="4" rx="2" className="kpi-value" />
                    </svg>
                  )}
                  <small>{metric.detail}</small>
                </div>
              </article>
            ))}
          </section>

          <section className="analytics-two-column">
            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h2>Candidate Match Distribution</h2><p>Estimated resume-to-job match categories</p></div>
                <span>Strong ≥ 75%</span>
              </div>
              <div className="distribution-list">
                {matchDistribution.map((item) => {
                  const percentage = uniqueCandidates.length ? Math.round((item.value / uniqueCandidates.length) * 100) : 0;
                  return (
                    <button type="button" key={item.label} onClick={() => onOpenCandidates({ match: item.label })}>
                      <span className={`distribution-dot ${item.label.toLowerCase().replaceAll(" ", "-")}`} />
                      <span><b>{item.label}</b><small>{percentage}% of candidates</small></span>
                      <strong>{item.value}</strong>
                      <svg viewBox="0 0 100 6" preserveAspectRatio="none" aria-hidden="true">
                        <rect width="100" height="6" rx="3" className="distribution-track" />
                        <rect width={percentage} height="6" rx="3" fill={item.color} />
                      </svg>
                    </button>
                  );
                })}
              </div>
              <p className="analytics-footnote">Match categories are estimates based on supplied job requirements, not guaranteed hiring outcomes.</p>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h2>Candidate Recruitment Status</h2><p>Current filtered candidate pipeline</p></div>
              </div>
              <div className="status-overview">
                <svg viewBox="0 0 220 220" aria-label="Recruitment status distribution">
                  <circle cx="110" cy="110" r="72" className="status-ring-base" />
                  {statusDistribution.map((item, index) => {
                    const total = Math.max(uniqueCandidates.length, 1);
                    const preceding = statusDistribution.slice(0, index).reduce((sum, entry) => sum + entry.value, 0);
                    return (
                      <circle
                        key={item.label}
                        cx="110"
                        cy="110"
                        r="72"
                        fill="none"
                        stroke={item.color}
                        strokeWidth="22"
                        strokeDasharray={`${(item.value / total) * 452.4} 452.4`}
                        strokeDashoffset={-(preceding / total) * 452.4}
                        transform="rotate(-90 110 110)"
                      >
                        <title>{`${item.label}: ${item.value}`}</title>
                      </circle>
                    );
                  })}
                  <text x="110" y="104" textAnchor="middle" className="status-total">{uniqueCandidates.length}</text>
                  <text x="110" y="124" textAnchor="middle" className="status-total-label">Candidates</text>
                </svg>
                <div>
                  {statusDistribution.map((item) => (
                    <span key={item.label}>
                      <i className={`status-legend-${item.label.toLowerCase().replaceAll(" ", "-")}`} />
                      <b>{item.label}</b>
                      <em>{item.value}</em>
                      <small>{uniqueCandidates.length ? Math.round((item.value / uniqueCandidates.length) * 100) : 0}%</small>
                    </span>
                  ))}
                </div>
              </div>
            </article>
          </section>

          <article className="analytics-card analytics-trend-card">
            <div className="analytics-card-heading">
              <div><h2>Candidate Analysis Over Time</h2><p>Saved resume analyses across {periodLabel.toLowerCase()}</p></div>
              <strong>{filtered.length} total analyses</strong>
            </div>
            {trendCoordinates.length ? (
              <div className="trend-chart">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Candidate analysis trend">
                  <defs>
                    <linearGradient id="analyticsArea" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={COLORS.teal} stopOpacity=".24" />
                      <stop offset="100%" stopColor={COLORS.teal} stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  {[18, 34, 50, 66, 82].map((y) => <line key={y} x1="4" x2="96" y1={y} y2={y} className="trend-gridline" />)}
                  {trendCoordinates.length > 1 && <polygon points={`4,82 ${trendPath} 96,82`} fill="url(#analyticsArea)" />}
                  <polyline points={trendPath} className="trend-line" />
                  {trendCoordinates.map((point) => (
                    <circle key={point.key} cx={point.x} cy={point.y} r="1.3" className="trend-point">
                      <title>{`${point.label}: ${point.value} analyses`}</title>
                    </circle>
                  ))}
                </svg>
                <div className="trend-labels">
                  {trendCoordinates.filter((_, index) => index % Math.max(1, Math.ceil(trend.length / 7)) === 0 || index === trend.length - 1).map((point) => (
                    <span key={point.key}>{point.label}</span>
                  ))}
                </div>
              </div>
            ) : <EmptyChart message="No saved analyses are available for this period." />}
          </article>

          <section className="analytics-two-column role-skill-row">
            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h2>Candidates by Job Role</h2><p>Analysis volume and average match by target role</p></div>
              </div>
              <RankedBars rows={roleRows} tone="teal" onSelect={(selectedRole) => onOpenCandidates({ role: selectedRole })} emptyMessage="No target-role data is available." />
            </article>

            <article className="analytics-card analytics-insight-card">
              <div>
                <span>Role insight</span>
                <h2>{roleRows[0]?.label ?? "Not enough data"}</h2>
                <p>
                  {roleRows.length
                    ? `This role has the highest analysis volume with ${roleRows[0].value} saved ${roleRows[0].value === 1 ? "record" : "records"}.`
                    : "Save analyses to identify the most active target roles."}
                </p>
              </div>
              {roleRows.length > 0 && (
                <button type="button" onClick={() => onOpenCandidates({ role: roleRows[0].label })}>
                  View role candidates →
                </button>
              )}
            </article>
          </section>

          <section className="analytics-two-column">
            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h2>Most Commonly Matched Skills</h2><p>Skills found against each analysis's own requirements</p></div>
              </div>
              <RankedBars rows={matchedSkills} tone="purple" emptyMessage="No matched skill data is available." />
            </article>
            <article className="analytics-card">
              <div className="analytics-card-heading">
                <div><h2>Most Common Missing Skills</h2><p>Required skills absent from relevant resumes</p></div>
                <button type="button" onClick={() => onOpenCandidates()}>View candidates →</button>
              </div>
              <RankedBars rows={missingSkills} tone="coral" emptyMessage="No missing skill data is available." />
            </article>
          </section>

          <article className="analytics-card analytics-activity-card">
            <div className="analytics-card-heading">
              <div><h2>Recent Recruitment Activity</h2><p>Latest saved resume-analysis records</p></div>
              <AnalyticsIcon name="activity" className="h-5 w-5" />
            </div>
            <div className="analytics-activity-list">
              {filtered.slice(0, 6).map((analysis) => (
                <button type="button" key={analysis.id} onClick={() => onOpenCandidate(analysis)}>
                  <span className="activity-icon"><AnalyticsIcon name="check" className="h-4 w-4" /></span>
                  <span>
                    <b>Resume analysis saved</b>
                    <small>{analysis.candidate.name} · {analysis.role}</small>
                  </span>
                  <em>{new Date(analysis.createdAt).toLocaleString()}</em>
                  <strong>{analysis.score}%</strong>
                </button>
              ))}
            </div>
          </article>
        </>
      )}
    </>
  );
}
