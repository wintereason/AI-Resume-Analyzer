import { useEffect, useMemo, useState } from "react";
import {
  ANALYSES_CHANGED_EVENT,
  deleteAnalysis,
  getSavedAnalyses,
  updateRecruitmentStatus,
} from "./lib/analysisStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";

type RecruitmentStatus = NonNullable<AnalysisResult["recruitmentStatus"]>;
type SortKey = "name" | "score" | "date" | "role";

type Props = {
  onAnalyze: () => void;
  onViewAnalysis: (analysis: AnalysisResult) => void;
  initialRole?: string;
  initialMatch?: string;
  initialProfile?: AnalysisResult | null;
};

const STATUSES: RecruitmentStatus[] = [
  "New",
  "Shortlisted",
  "Interview Scheduled",
  "Rejected",
];
const PAGE_SIZE = 8;

const iconPaths = {
  people:
    "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm5-1a2.5 2.5 0 0 0 0-5M19 15c1.5.6 2.5 2 2.5 3.5",
  star: "m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z",
  trend: "M4 17 9 12l3 3 7-8m-5 0h5v5",
  clock: "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  search: "m20 20-4.2-4.2M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z",
  export: "M12 4v11m0-11L8 8m4-4 4 4M5 14v5h14v-5",
  plus: "M12 5v14M5 12h14",
  filter: "M4 6h16M7 12h10m-7 6h4",
  chevron: "m9 7 5 5-5 5",
  close: "m7 7 10 10m0-10L7 17",
  trash: "M8 8v10m4-10v10m4-10v10M5 5h14m-11 0 1-2h6l1 2m2 0-1 16H7L6 5",
  file: "M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm7 0v5h4M9 13h6m-6 4h4",
};

function CandidateIcon({
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
  const { candidate } = analysis;
  if (candidate.email !== "Not found") return `email:${candidate.email.toLowerCase()}`;
  if (candidate.phone !== "Not found") return `phone:${candidate.phone.replace(/\D/g, "")}`;
  return `resume:${analysis.fileName.toLowerCase()}:${candidate.name.toLowerCase()}`;
}

function initials(name: string) {
  if (name === "Not found") return "NA";
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function safeDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function csvCell(value: string | number) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

function StatusSelect({
  value,
  onChange,
  label,
}: {
  value: RecruitmentStatus;
  onChange: (status: RecruitmentStatus) => void;
  label: string;
}) {
  return (
    <select
      className={`candidate-status-select status-${value.toLowerCase().replaceAll(" ", "-")}`}
      value={value}
      onChange={(event) => onChange(event.target.value as RecruitmentStatus)}
      aria-label={label}
    >
      {STATUSES.map((status) => (
        <option key={status}>{status}</option>
      ))}
    </select>
  );
}

export default function CandidateManagement({
  onAnalyze,
  onViewAnalysis,
  initialRole = "All Roles",
  initialMatch = "All Scores",
  initialProfile = null,
}: Props) {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  const [role, setRole] = useState(initialRole);
  const [match, setMatch] = useState(initialMatch);
  const [level, setLevel] = useState("All Levels");
  const [dateRange, setDateRange] = useState("All Time");
  const [candidateStatus, setCandidateStatus] = useState("All Statuses");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [profile, setProfile] = useState<AnalysisResult | null>(initialProfile);
  const [deleteTarget, setDeleteTarget] = useState<AnalysisResult | null>(null);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  async function loadAnalyses() {
    setLoading(true);
    setError("");
    try {
      setAnalyses(await getSavedAnalyses());
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Candidate records could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAnalyses();
    const reload = () => void loadAnalyses();
    window.addEventListener(ANALYSES_CHANGED_EVENT, reload);
    return () => window.removeEventListener(ANALYSES_CHANGED_EVENT, reload);
  }, []);

  useEffect(() => setPage(1), [query, role, match, level, dateRange, candidateStatus]);

  function flash(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2600);
  }

  const roles = useMemo(
    () => [
      "All Roles",
      ...Array.from(new Set(analyses.map((analysis) => analysis.role))).sort(),
    ],
    [analyses],
  );

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const days =
      dateRange === "Last 7 Days"
        ? 7
        : dateRange === "Last 30 Days"
          ? 30
          : dateRange === "Last 90 Days"
            ? 90
            : 0;
    const cutoff = days ? Date.now() - days * 86_400_000 : 0;
    return analyses
      .filter((analysis) => {
        const searchable = [
          analysis.candidate.name,
          analysis.candidate.email,
          analysis.candidate.phone,
          analysis.role,
          ...analysis.candidate.skills,
          ...analysis.matchedSkills,
          ...analysis.additionalSkills,
        ]
          .join(" ")
          .toLowerCase();
        return (
          (!normalizedQuery || searchable.includes(normalizedQuery)) &&
          (role === "All Roles" || analysis.role === role) &&
          (match === "All Scores" || analysis.status === match) &&
          (level === "All Levels" || analysis.level === level) &&
          (candidateStatus === "All Statuses" ||
            (analysis.recruitmentStatus ?? "New") === candidateStatus) &&
          (!cutoff || new Date(analysis.createdAt).getTime() >= cutoff)
        );
      })
      .sort((a, b) => {
        const values = {
          name: [a.candidate.name, b.candidate.name],
          score: [a.score, b.score],
          date: [a.createdAt, b.createdAt],
          role: [a.role, b.role],
        }[sortKey];
        const comparison =
          typeof values[0] === "number"
            ? Number(values[0]) - Number(values[1])
            : String(values[0]).localeCompare(String(values[1]));
        return sortDirection === "asc" ? comparison : -comparison;
      });
  }, [analyses, candidateStatus, dateRange, level, match, query, role, sortDirection, sortKey]);

  const uniqueCandidates = useMemo(() => {
    const groups = new Map<string, AnalysisResult[]>();
    analyses.forEach((analysis) => {
      const key = candidateKey(analysis);
      groups.set(key, [...(groups.get(key) ?? []), analysis]);
    });
    return [...groups.values()];
  }, [analyses]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const average = analyses.length
    ? Math.round(analyses.reduce((sum, analysis) => sum + analysis.score, 0) / analyses.length)
    : 0;
  const recentCutoff = Date.now() - 7 * 86_400_000;
  const strongCount = uniqueCandidates.filter((items) =>
    items.some((analysis) => analysis.score >= 75),
  ).length;
  const recentCount = uniqueCandidates.filter((items) =>
    items.some((analysis) => new Date(analysis.createdAt).getTime() >= recentCutoff),
  ).length;

  function clearFilters() {
    setQuery("");
    setRole("All Roles");
    setMatch("All Scores");
    setLevel("All Levels");
    setDateRange("All Time");
    setCandidateStatus("All Statuses");
  }

  function changeSort(next: SortKey) {
    if (sortKey === next) setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
    else {
      setSortKey(next);
      setSortDirection("asc");
    }
  }

  async function changeStatus(analysis: AnalysisResult, status: RecruitmentStatus) {
    try {
      const updated = await updateRecruitmentStatus(analysis.id, status);
      setAnalyses((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setProfile((current) => (current?.id === updated.id ? updated : current));
      flash(`${analysis.candidate.name}'s status was updated to ${status}.`);
    } catch (statusError) {
      setError(
        statusError instanceof Error ? statusError.message : "The status could not be updated.",
      );
    }
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      await deleteAnalysis(deleteTarget.id);
      setDeleteTarget(null);
      setProfile((current) => (current?.id === deleteTarget.id ? null : current));
      flash("The saved analysis was deleted. The original PDF was not removed.");
    } catch (deleteError) {
      setError(
        deleteError instanceof Error ? deleteError.message : "The record could not be deleted.",
      );
    }
  }

  function exportRows(rows: AnalysisResult[], fileName = "talentflow-candidates.csv") {
    if (!rows.length) {
      flash("No candidate records are available to export.");
      return;
    }
    setExporting(true);
    const headings = [
      "Candidate Name",
      "Email",
      "Phone",
      "Target Role",
      "Match Score",
      "Matched Skills",
      "Missing Skills",
      "Experience",
      "Recruitment Status",
      "Date Added",
    ];
    const csv = [
      headings.map(csvCell).join(","),
      ...rows.map((analysis) =>
        [
          analysis.candidate.name,
          analysis.candidate.email,
          analysis.candidate.phone,
          analysis.role,
          `${analysis.score}%`,
          analysis.matchedSkills.join("; "),
          analysis.missingSkills.join("; "),
          analysis.candidate.experience.join("; ") || "Not found",
          analysis.recruitmentStatus ?? "New",
          safeDate(analysis.createdAt),
        ]
          .map(csvCell)
          .join(","),
      ),
    ].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(url);
    window.setTimeout(() => setExporting(false), 350);
    flash(`${rows.length} candidate ${rows.length === 1 ? "record was" : "records were"} exported.`);
  }

  const profileHistory = profile
    ? analyses.filter((analysis) => candidateKey(analysis) === candidateKey(profile))
    : [];

  return (
    <>
      {notice && <div className="dashboard-toast">{notice}</div>}
      <div className="analyzer-breadcrumb">
        <span>Dashboard</span>
        <span>/</span>
        <b>Saved Resumes</b>
      </div>

      <div className="candidate-page-heading">
        <div>
          <h1>Saved Resumes</h1>
          <p>Manage candidates, review resume matches, and track recruitment progress.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="secondary-action"
            onClick={() => exportRows(filtered)}
            disabled={exporting}
          >
            <CandidateIcon name="export" className="h-4 w-4" />
            {exporting ? "Exporting..." : "Export Candidates"}
          </button>
          <button type="button" className="primary-action" onClick={onAnalyze}>
            <CandidateIcon name="plus" className="h-4 w-4" />
            Analyze New Resume
          </button>
        </div>
      </div>

      {error && (
        <div className="analysis-alert error">
          <b>Something went wrong</b>
          <span>{error}</span>
          <button type="button" onClick={() => void loadAnalyses()}>
            Try again
          </button>
        </div>
      )}

      <section className="candidate-summary-grid">
        {[
          {
            label: "Total Candidates",
            value: uniqueCandidates.length,
            supporting: `${analyses.length} saved ${analyses.length === 1 ? "analysis" : "analyses"}`,
            icon: "people" as const,
            tone: "teal",
          },
          {
            label: "Strong Matches",
            value: strongCount,
            supporting: "75% match score or higher",
            icon: "star" as const,
            tone: "purple",
          },
          {
            label: "Average Match Score",
            value: `${average}%`,
            supporting: analyses.length ? "Across all saved analyses" : "No scores available yet",
            icon: "trend" as const,
            tone: "blue",
          },
          {
            label: "Recently Added",
            value: recentCount,
            supporting: "Saved within the last 7 days",
            icon: "clock" as const,
            tone: "amber",
          },
        ].map((metric) => (
          <article key={metric.label} className="candidate-summary-card">
            <div className={`metric-icon ${metric.tone}`}>
              <CandidateIcon name={metric.icon} />
            </div>
            <div>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.supporting}</small>
            </div>
          </article>
        ))}
      </section>

      <section className="candidate-directory">
        <div className="candidate-toolbar">
          <div className="candidate-search-field">
            <CandidateIcon name="search" className="h-[18px] w-[18px]" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by name, email, phone, role, or skill..."
              aria-label="Search saved candidates"
            />
          </div>
          <div className="candidate-filter-title">
            <CandidateIcon name="filter" className="h-4 w-4" />
            Filters
          </div>
          <button type="button" className="clear-filter-button" onClick={clearFilters}>
            Clear all
          </button>
        </div>
        <div className="candidate-filters">
          {[
            ["Target Job Role", role, setRole, roles],
            [
              "Match Score",
              match,
              setMatch,
              ["All Scores", "Strong Match", "Moderate Match", "Low Match"],
            ],
            [
              "Experience Level",
              level,
              setLevel,
              ["All Levels", "Fresher", "Entry Level", "Intermediate", "Experienced"],
            ],
            [
              "Date Added",
              dateRange,
              setDateRange,
              ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            ],
            [
              "Candidate Status",
              candidateStatus,
              setCandidateStatus,
              ["All Statuses", ...STATUSES],
            ],
          ].map(([label, value, setter, options]) => (
            <label key={label as string}>
              <span>{label as string}</span>
              <select
                value={value as string}
                onChange={(event) => (setter as (value: string) => void)(event.target.value)}
              >
                {(options as string[]).map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </label>
          ))}
        </div>

        <div className="directory-heading">
          <div>
            <h2>Candidate Directory</h2>
            <p>
              {filtered.length} matching {filtered.length === 1 ? "candidate record" : "candidate records"}
            </p>
          </div>
          <span>Strong match threshold: 75%</span>
        </div>

        {loading ? (
          <div className="candidate-state">
            <span className="candidate-loader" />
            <h3>Loading saved candidates</h3>
            <p>Retrieving saved resume analyses from the recruitment database...</p>
          </div>
        ) : !analyses.length ? (
          <div className="candidate-state">
            <div className="candidate-state-icon">
              <CandidateIcon name="file" className="h-7 w-7" />
            </div>
            <h3>No saved resumes yet</h3>
            <p>Analyze and save a resume to start building your candidate directory.</p>
            <button type="button" className="primary-action" onClick={onAnalyze}>
              Analyze your first resume
            </button>
          </div>
        ) : !filtered.length ? (
          <div className="candidate-state">
            <div className="candidate-state-icon">
              <CandidateIcon name="search" className="h-7 w-7" />
            </div>
            <h3>No candidates match these filters</h3>
            <p>Try a broader search or clear the active filters.</p>
            <button type="button" className="secondary-action" onClick={clearFilters}>
              Clear Filters
            </button>
          </div>
        ) : (
          <>
            <div className="candidate-table-wrap">
              <table className="management-table">
                <thead>
                  <tr>
                    <th>
                      <button type="button" onClick={() => changeSort("name")}>
                        Candidate <span>↕</span>
                      </button>
                    </th>
                    <th>
                      <button type="button" onClick={() => changeSort("role")}>
                        Target Role <span>↕</span>
                      </button>
                    </th>
                    <th>
                      <button type="button" onClick={() => changeSort("score")}>
                        Match Score <span>↕</span>
                      </button>
                    </th>
                    <th>Skills Match</th>
                    <th>Experience</th>
                    <th>Status</th>
                    <th>
                      <button type="button" onClick={() => changeSort("date")}>
                        Date Added <span>↕</span>
                      </button>
                    </th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((analysis, index) => {
                    const required = analysis.matchedSkills.length + analysis.missingSkills.length;
                    return (
                      <tr key={analysis.id}>
                        <td>
                          <div className="candidate-person">
                            <span className={`candidate-avatar ${["mint", "purple", "amber", "blue"][index % 4]}`}>
                              {initials(analysis.candidate.name)}
                            </span>
                            <div>
                              <b>{analysis.candidate.name}</b>
                              <span>{analysis.candidate.email}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <b className="role-name">{analysis.role}</b>
                          <span className="table-subtext">{analysis.level}</span>
                        </td>
                        <td>
                          <div className="management-score">
                            <b>{analysis.score}%</b>
                            <span>
                              <i className={`score-width-${Math.round(analysis.score / 5) * 5}`} />
                            </span>
                          </div>
                        </td>
                        <td>
                          <b className="skill-ratio">
                            {analysis.matchedSkills.length}/{required || 0}
                          </b>
                          <span className="table-subtext">
                            {analysis.matchedSkills.slice(0, 2).join(", ") || "None found"}
                          </span>
                        </td>
                        <td>
                          <b className="experience-label">{analysis.level}</b>
                          <span className="table-subtext">
                            {analysis.candidate.experience.length
                              ? `${analysis.candidate.experience.length} item${analysis.candidate.experience.length === 1 ? "" : "s"} found`
                              : "Not found"}
                          </span>
                        </td>
                        <td>
                          <StatusSelect
                            value={analysis.recruitmentStatus ?? "New"}
                            label={`Update ${analysis.candidate.name}'s status`}
                            onChange={(status) => void changeStatus(analysis, status)}
                          />
                        </td>
                        <td>
                          <b className="date-label">{safeDate(analysis.createdAt)}</b>
                          <span className="table-subtext">
                            {new Date(analysis.createdAt).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </td>
                        <td>
                          <div className="candidate-actions">
                            <button
                              type="button"
                              className="profile-button"
                              onClick={() => setProfile(analysis)}
                            >
                              View
                            </button>
                            <button
                              type="button"
                              className="more-button"
                              aria-label={`More actions for ${analysis.candidate.name}`}
                              onClick={() =>
                                setOpenMenu((current) => (current === analysis.id ? null : analysis.id))
                              }
                            >
                              •••
                            </button>
                            {openMenu === analysis.id && (
                              <div className="row-menu">
                                <button type="button" onClick={() => onViewAnalysis(analysis)}>
                                  View full analysis
                                </button>
                                <button type="button" onClick={onAnalyze}>
                                  Re-analyze resume
                                </button>
                                <button
                                  type="button"
                                  className="danger"
                                  onClick={() => {
                                    setDeleteTarget(analysis);
                                    setOpenMenu(null);
                                  }}
                                >
                                  Delete record
                                </button>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="candidate-mobile-list">
              {visible.map((analysis) => (
                <article key={analysis.id} className="candidate-mobile-card">
                  <div className="candidate-person">
                    <span className="candidate-avatar mint">{initials(analysis.candidate.name)}</span>
                    <div>
                      <b>{analysis.candidate.name}</b>
                      <span>{analysis.candidate.email}</span>
                    </div>
                    <strong>{analysis.score}%</strong>
                  </div>
                  <div className="mobile-candidate-meta">
                    <span>
                      <small>Target role</small>
                      <b>{analysis.role}</b>
                    </span>
                    <span>
                      <small>Skills match</small>
                      <b>
                        {analysis.matchedSkills.length}/
                        {analysis.matchedSkills.length + analysis.missingSkills.length}
                      </b>
                    </span>
                  </div>
                  <StatusSelect
                    value={analysis.recruitmentStatus ?? "New"}
                    label={`Update ${analysis.candidate.name}'s status`}
                    onChange={(status) => void changeStatus(analysis, status)}
                  />
                  <div className="flex gap-2">
                    <button type="button" className="secondary-action flex-1" onClick={() => setProfile(analysis)}>
                      View Profile
                    </button>
                    <button type="button" className="secondary-action flex-1" onClick={() => onViewAnalysis(analysis)}>
                      Analysis
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <div className="candidate-pagination">
              <p>
                Showing {(page - 1) * PAGE_SIZE + 1}–
                {Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}
              </p>
              <div>
                <button type="button" disabled={page === 1} onClick={() => setPage(page - 1)}>
                  Previous
                </button>
                {Array.from({ length: totalPages }, (_, index) => index + 1)
                  .slice(Math.max(0, page - 3), Math.min(totalPages, page + 2))
                  .map((number) => (
                    <button
                      type="button"
                      className={number === page ? "active" : ""}
                      key={number}
                      onClick={() => setPage(number)}
                    >
                      {number}
                    </button>
                  ))}
                <button
                  type="button"
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </section>

      {profile && (
        <div className="candidate-modal" role="dialog" aria-modal="true" aria-label="Candidate profile">
          <button
            type="button"
            className="candidate-modal-backdrop"
            onClick={() => setProfile(null)}
            aria-label="Close candidate profile"
          />
          <section className="candidate-profile-panel">
            <div className="profile-topbar">
              <div>
                <span>Candidate Profile</span>
                <p>Saved recruitment record</p>
              </div>
              <button type="button" onClick={() => setProfile(null)} aria-label="Close profile">
                <CandidateIcon name="close" />
              </button>
            </div>
            <div className="profile-hero">
              <span className="profile-avatar">{initials(profile.candidate.name)}</span>
              <div className="profile-identity">
                <h2>{profile.candidate.name}</h2>
                <p>
                  {profile.candidate.email} · {profile.candidate.phone}
                </p>
                <div>
                  <span>{profile.role}</span>
                  <span>{safeDate(profile.createdAt)}</span>
                </div>
              </div>
              <div className="profile-score">
                <strong>{profile.score}%</strong>
                <span>{profile.status}</span>
              </div>
            </div>
            <div className="profile-actions">
              <StatusSelect
                value={profile.recruitmentStatus ?? "New"}
                label="Update recruitment status"
                onChange={(status) => void changeStatus(profile, status)}
              />
              <button type="button" className="secondary-action" onClick={() => onViewAnalysis(profile)}>
                View Analysis
              </button>
              <button
                type="button"
                className="secondary-action"
                onClick={() => exportRows([profile], `${profile.candidate.name}-profile.csv`)}
              >
                Export Profile
              </button>
            </div>
            <div className="profile-content">
              <section className="profile-section">
                <h3>Resume Overview</h3>
                <div className="profile-overview-grid">
                  {[
                    ["Education", profile.candidate.education.join("; ") || "Not found"],
                    ["Experience", profile.candidate.experience.join("; ") || "Not found"],
                    ["Key skills", profile.candidate.skills.join(", ") || "Not found"],
                    ["Projects", profile.candidate.projects.join("; ") || "Not found"],
                    ["Certifications", profile.candidate.certifications.join("; ") || "Not found"],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <span>{label}</span>
                      <p>{value}</p>
                    </div>
                  ))}
                </div>
              </section>
              <section className="profile-section">
                <h3>Skill Comparison</h3>
                <div className="profile-skills-grid">
                  {[
                    ["Matched skills", profile.matchedSkills, "matched"],
                    ["Missing skills", profile.missingSkills, "missing"],
                    ["Additional skills", profile.additionalSkills, "additional"],
                  ].map(([label, items, tone]) => (
                    <div key={label as string} className={tone as string}>
                      <b>{label as string}</b>
                      <div>
                        {(items as string[]).length ? (
                          (items as string[]).map((item) => <span key={item}>{item}</span>)
                        ) : (
                          <span>Not found</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
              <section className="profile-section">
                <h3>Recommendations</h3>
                <div className="profile-recommendations">
                  {profile.suggestions.map((suggestion, index) => (
                    <div key={suggestion}>
                      <span>{index + 1}</span>
                      <p>{suggestion}</p>
                    </div>
                  ))}
                </div>
              </section>
              <section className="profile-section">
                <h3>Analysis History</h3>
                <div className="profile-history">
                  {profileHistory.map((history) => (
                    <article key={history.id}>
                      <div>
                        <b>{history.role}</b>
                        <span>{safeDate(history.createdAt)} · {history.level}</span>
                      </div>
                      <strong>{history.score}%</strong>
                      <button type="button" onClick={() => onViewAnalysis(history)}>
                        Open
                      </button>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          </section>
        </div>
      )}

      {deleteTarget && (
        <div className="confirm-overlay" role="alertdialog" aria-modal="true">
          <button
            type="button"
            className="candidate-modal-backdrop"
            aria-label="Cancel deletion"
            onClick={() => setDeleteTarget(null)}
          />
          <section className="confirm-dialog">
            <div className="confirm-icon">
              <CandidateIcon name="trash" />
            </div>
            <h2>Delete saved analysis?</h2>
            <p>
              This will permanently remove the {deleteTarget.role} analysis for{" "}
              <b>{deleteTarget.candidate.name}</b>. The original PDF will not be deleted.
            </p>
            <div>
              <button type="button" className="secondary-action" onClick={() => setDeleteTarget(null)}>
                Cancel
              </button>
              <button type="button" className="danger-action" onClick={() => void confirmDelete()}>
                Delete record
              </button>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
