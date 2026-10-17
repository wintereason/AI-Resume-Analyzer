import { FormEvent, useEffect, useState } from "react";
import ResumeAnalyzer from "./ResumeAnalyzer";
import CandidateManagement from "./CandidateManagement";
import RecruitmentAnalytics from "./RecruitmentAnalytics";
import JobRoles from "./JobRoles";
import SkillGapAnalysis from "./SkillGapAnalysis";
import InterviewScheduler from "./InterviewScheduler";
import { ANALYSES_CHANGED_EVENT, getSavedAnalyses } from "./lib/analysisStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";
import { getJobRoles, type JobRole } from "./lib/jobRoleStorage";
import { getInterviews, INTERVIEWS_CHANGED_EVENT, type Interview } from "./lib/interviewStorage";
import { hasAuthToken, loginRecruiter, logoutRecruiter } from "./lib/api";
import { migrateIndexedDbToSupabase } from "./lib/migrateIndexedDbToSupabase";

const recruiterImage =
  "https://images.unsplash.com/photo-1590650153855-d9e808231d41?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&ixlib=rb-4.1.0&q=88&w=1400";

function Logo() {
  return (
    <div className="flex items-center gap-3" aria-label="TalentFlow">
      <div className="grid h-10 w-10 place-items-center rounded-[13px] bg-[#2e246b] text-white shadow-[0_8px_22px_rgba(46,36,107,0.18)]">
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="h-[22px] w-[22px]"
          fill="none"
        >
          <path
            d="M7 6.5h10M12 6.5v11M8.5 10.5 12 14l3.5-3.5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <span className="text-[21px] font-extrabold tracking-[-0.045em] text-[#211c45]">
        talent<span className="text-[#f06f61]">flow</span>
      </span>
    </div>
  );
}

type IconName =
  | "dashboard"
  | "candidates"
  | "resume"
  | "jobs"
  | "calendar"
  | "compare"
  | "chart"
  | "settings"
  | "search"
  | "upload"
  | "sparkles"
  | "bell"
  | "refresh"
  | "logout";

const iconPaths: Record<IconName, string> = {
  dashboard: "M4 13h6V4H4v9Zm10 7h6v-9h-6v9ZM4 20h6v-3H4v3Zm10-13h6V4h-6v3Z",
  candidates:
    "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm5-1a2.5 2.5 0 0 0 0-5M19 15c1.5.6 2.5 2 2.5 3.5M7 11a2.5 2.5 0 0 1 0-5M5 15a3.8 3.8 0 0 0-2.5 3.5",
  resume:
    "M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm7 0v5h4M9 13h6M9 17h6",
  jobs: "M4 8h16v11H4V8Zm5 0V5h6v3M4 12h16M10 12v2h4v-2",
  calendar:
    "M5 5h14a2 2 0 0 1 2 2v12H3V7a2 2 0 0 1 2-2Zm2-2v4m10-4v4M3 10h18M7 14h3m2 0h3m2 0h1M7 17h3m2 0h3",
  compare: "M7 7h13m0 0-3-3m3 3-3 3M17 17H4m0 0 3-3m-3 3 3 3",
  chart: "M4 20V10m5 10V4m5 16v-7m5 7V7",
  settings:
    "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm0-12v2m0 13v2m8.5-8.5h-2m-13 0h-2m14.5-6-1.5 1.5m-9 9L6 18m12 0-1.5-1.5m-9-9L6 6",
  search: "m20 20-4.2-4.2M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z",
  upload: "M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v5h14v-5",
  sparkles:
    "m12 3 1.2 3.2L16.5 7.5l-3.3 1.3L12 12l-1.2-3.2-3.3-1.3 3.3-1.3L12 3Zm6 9 .8 2.2L21 15l-2.2.8L18 18l-.8-2.2L15 15l2.2-.8L18 12ZM6 13l1 2.8 3 1.2-3 1.2L6 21l-1-2.8L2 17l3-1.2L6 13Z",
  bell: "M18 9a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7Zm-8 10h4",
  refresh: "M20 7v5h-5M4 17v-5h5m10.3-3A8 8 0 0 0 6.2 6.2L4 9m16 6-2.2 2.8A8 8 0 0 1 4.7 15",
  logout: "M10 5H5v14h5m5-4 4-3-4-3m4 3H9",
};

function Icon({ name, className = "h-5 w-5" }: { name: IconName; className?: string }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className={className}
      fill="none"
    >
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

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [refreshed, setRefreshed] = useState(false);
  const [notice, setNotice] = useState("");
  const [page, setPage] = useState<"dashboard" | "analyzer" | "candidates" | "analytics" | "jobs" | "skillgap" | "interviews">("dashboard");
  const [candidateCount, setCandidateCount] = useState(0);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [jobRoles, setJobRoles] = useState<JobRole[]>([]);
  const [openJobRoleCount, setOpenJobRoleCount] = useState(0);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResult | null>(null);
  const [selectedCandidateProfile, setSelectedCandidateProfile] = useState<AnalysisResult | null>(null);
  const [selectedJobRole, setSelectedJobRole] = useState<JobRole | null>(null);
  const [upcomingInterviews, setUpcomingInterviews] = useState<Interview[]>([]);
  const [openInterviewForm, setOpenInterviewForm] = useState(false);
  const [candidateFilters, setCandidateFilters] = useState<{ role?: string; match?: string }>({});
  const storedUser = JSON.parse(localStorage.getItem("talentflow-user") ?? "{}") as {
    name?: string;
    email?: string;
    role?: string;
  };
  const userName = storedUser.name ?? "Suraj Jangde";
  const userEmail = storedUser.email ?? "surajjangde1312@gmail.com";
  const userRole = storedUser.role ?? "Admin";
  const userInitials = userName.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
  const currentDate = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date());

  useEffect(() => {
    const loadCount = () =>
      getSavedAnalyses()
        .then((items) => {
          setAnalyses(items);
          setCandidateCount(
            new Set(
              items.map((item) =>
                item.candidate.email !== "Not found"
                  ? item.candidate.email.toLowerCase()
                  : `${item.fileName}:${item.candidate.name}`,
              ),
            ).size,
          );
        })
        .catch(() => {
          setAnalyses([]);
          setCandidateCount(0);
        });
    void loadCount();
    window.addEventListener(ANALYSES_CHANGED_EVENT, loadCount);
    return () => window.removeEventListener(ANALYSES_CHANGED_EVENT, loadCount);
  }, []);

  useEffect(() => {
    const loadRoles = () =>
      getJobRoles()
        .then((items) => {
          setJobRoles(items);
          setOpenJobRoleCount(items.filter((role) => role.status === "Active").length);
        })
        .catch(() => {
          setJobRoles([]);
          setOpenJobRoleCount(0);
        });
    void loadRoles();
    window.addEventListener("talentflow-job-roles-changed", loadRoles);
    return () => window.removeEventListener("talentflow-job-roles-changed", loadRoles);
  }, []);

  useEffect(() => {
    const loadUpcoming = () =>
      getInterviews()
        .then((items) =>
          setUpcomingInterviews(
            items
              .filter((item) => new Date(`${item.date}T${item.startTime}`).getTime() >= Date.now() && !["Completed", "Cancelled"].includes(item.status))
              .slice(0, 5),
          ),
        )
        .catch(() => setUpcomingInterviews([]));
    void loadUpcoming();
    window.addEventListener(INTERVIEWS_CHANGED_EVENT, loadUpcoming);
    return () => window.removeEventListener(INTERVIEWS_CHANGED_EVENT, loadUpcoming);
  }, []);

  function refreshDashboard() {
    setRefreshed(true);
    window.setTimeout(() => setRefreshed(false), 700);
  }

  function showNotice(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2200);
  }

  const recentCandidates = [...analyses].sort((left, right) => right.createdAt.localeCompare(left.createdAt)).slice(0, 4);
  const statusLabels = ["New", "Shortlisted", "Interview Scheduled", "Rejected"];
  const statusCounts = statusLabels.map((label) => ({
    label,
    value: analyses.filter((analysis) => (analysis.recruitmentStatus ?? "New") === label).length,
  }));
  const totalCandidates = statusCounts.reduce((total, item) => total + item.value, 0);
  const skillCounts = new Map<string, number>();
  jobRoles.filter((role) => role.status === "Active").forEach((role) => {
    [...role.requiredSkills, ...role.preferredSkills].forEach((skill) => {
      const normalized = skill.trim();
      if (normalized) skillCounts.set(normalized, (skillCounts.get(normalized) ?? 0) + 1);
    });
  });
  const topSkills = [...skillCounts.entries()].sort((left, right) => right[1] - left[1]).slice(0, 4);
  const maxSkillCount = topSkills[0]?.[1] ?? 1;
  const recentActivities = [
    ...analyses.map((analysis) => ({
      icon: "resume" as IconName,
      title: "Resume analyzed",
      body: `${analysis.candidate.name} scored ${analysis.score} for ${analysis.role}`,
      date: analysis.createdAt,
      theme: "teal",
    })),
    ...jobRoles.map((role) => ({
      icon: "jobs" as IconName,
      title: "Job role updated",
      body: `${role.title} is ${role.status.toLowerCase()}`,
      date: role.updatedAt,
      theme: "amber",
    })),
    ...upcomingInterviews.map((interview) => ({
      icon: "calendar" as IconName,
      title: "Interview scheduled",
      body: `${interview.candidateName} for ${interview.jobRoleTitle}`,
      date: interview.createdAt,
      theme: "purple",
    })),
  ].sort((left, right) => right.date.localeCompare(left.date)).slice(0, 3);

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="flex h-[78px] items-center gap-3 border-b border-white/7 px-6">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-[#12b9a4] text-white shadow-[0_8px_24px_rgba(18,185,164,0.32)]">
            <Icon name="sparkles" className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[17px] font-extrabold tracking-[-0.03em] text-white">TalentFlow AI</p>
            <p className="text-[11px] text-white/40">Recruitment Suite</p>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-5">
          <p className="px-3 pb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/25">Main navigation</p>
          <button className={`side-nav ${page === "dashboard" ? "active" : ""}`} type="button" onClick={() => setPage("dashboard")}>
            <Icon name="dashboard" />
            <span>Dashboard</span>
          </button>
          <button className={`side-nav ${page === "analyzer" ? "active" : ""}`} type="button" onClick={() => { setSelectedAnalysis(null); setSelectedJobRole(null); setPage("analyzer"); }}>
            <Icon name="resume" />
            <span>Resume Analyzer</span>
            <span className="ml-auto rounded-md bg-[#18b9a4]/15 px-2 py-0.5 text-[9px] font-bold text-[#31d3bd]">AI</span>
          </button>
          <button className={`side-nav ${page === "candidates" ? "active" : ""}`} type="button" onClick={() => { setCandidateFilters({}); setSelectedCandidateProfile(null); setPage("candidates"); }}>
            <Icon name="candidates" />
            <span>Candidates</span>
            <span className="ml-auto text-[11px] text-white/35">{candidateCount}</span>
          </button>
          <button className={`side-nav ${page === "analytics" ? "active" : ""}`} type="button" onClick={() => setPage("analytics")}>
            <Icon name="chart" />
            <span>Recruitment Analytics</span>
          </button>
          <button className={`side-nav ${page === "jobs" ? "active" : ""}`} type="button" onClick={() => setPage("jobs")}>
            <Icon name="jobs" />
            <span>Job Roles</span>
          </button>
          <button className={`side-nav ${page === "skillgap" ? "active" : ""}`} type="button" onClick={() => { setSelectedJobRole(null); setPage("skillgap"); }}>
            <Icon name="compare" />
            <span>Skill Gap Analysis</span>
          </button>
          <button className={`side-nav ${page === "interviews" ? "active" : ""}`} type="button" onClick={() => { setOpenInterviewForm(false); setPage("interviews"); }}>
            <Icon name="calendar" />
            <span>Interview Scheduler</span>
          </button>
        </nav>

        <div className="border-t border-white/7 p-4">
          <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 p-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-[#e9dffd] text-xs font-extrabold text-[#6c4eb5]">{userInitials}</div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-bold text-white">{userName}</p>
              <p className="truncate text-[10px] text-white/35">{userEmail}</p>
            </div>
          </div>
          <button type="button" onClick={onLogout} className="side-nav w-full">
            <Icon name="logout" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="dashboard-topbar">
          <div className="dashboard-search">
            <Icon name="search" className="h-[18px] w-[18px]" />
            <input aria-label="Search dashboard" placeholder={page === "analyzer" ? "Search saved analyses..." : page === "candidates" ? "Search candidates, roles, skills..." : page === "analytics" ? "Search analytics, roles, skills..." : page === "jobs" ? "Search job roles and requirements..." : page === "skillgap" ? "Search candidates and skills..." : "Search candidates, jobs, skills..."} />
            <kbd>⌘ K</kbd>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <button type="button" className="top-icon-button" aria-label="Notifications">
              <Icon name="bell" />
              <span className="notification-dot">3</span>
            </button>
            <div className="hidden items-center gap-3 border-l border-[#e9e8e4] pl-4 sm:flex">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-[#13aa98] text-xs font-extrabold text-white">{userInitials}</div>
              <div>
                <p className="text-xs font-extrabold text-[#222725]">{userName}</p>
                <p className="text-[10px] font-semibold text-[#989c99]">{userRole}</p>
              </div>
            </div>
          </div>
        </header>

        <main className="dashboard-content">
          {notice && <div className="dashboard-toast">{notice}</div>}

          {page === "analyzer" ? (
            <ResumeAnalyzer initialAnalysis={selectedAnalysis} initialJobRole={selectedJobRole} onReturn={() => setPage(selectedAnalysis ? "candidates" : selectedJobRole ? "jobs" : "dashboard")} />
          ) : page === "candidates" ? (
            <CandidateManagement
              key={`${candidateFilters.role ?? ""}-${candidateFilters.match ?? ""}-${selectedCandidateProfile?.id ?? ""}`}
              initialRole={candidateFilters.role}
              initialMatch={candidateFilters.match}
              initialProfile={selectedCandidateProfile}
              onAnalyze={() => { setSelectedAnalysis(null); setPage("analyzer"); }}
              onViewAnalysis={(analysis) => { setSelectedAnalysis(analysis); setPage("analyzer"); }}
            />
          ) : page === "analytics" ? (
            <RecruitmentAnalytics
              onAnalyze={() => { setSelectedAnalysis(null); setPage("analyzer"); }}
              onOpenCandidate={(analysis) => { setSelectedAnalysis(analysis); setPage("analyzer"); }}
              onOpenCandidates={(filters = {}) => { setSelectedCandidateProfile(null); setCandidateFilters(filters); setPage("candidates"); }}
            />
          ) : page === "jobs" ? (
            <JobRoles
              onAnalyze={(role) => { setSelectedAnalysis(null); setSelectedJobRole(role); setPage("analyzer"); }}
              onCandidates={(role) => { setSelectedCandidateProfile(null); setCandidateFilters({ role }); setPage("candidates"); }}
              onSkillGap={(role) => { setSelectedJobRole(role); setPage("skillgap"); }}
            />
          ) : page === "skillgap" ? (
            <SkillGapAnalysis
              initialRole={selectedJobRole}
              onAnalyze={(role) => { setSelectedAnalysis(null); setSelectedJobRole(role ?? null); setPage("analyzer"); }}
              onCandidate={(analysis) => { setSelectedCandidateProfile(analysis); setCandidateFilters({}); setPage("candidates"); }}
              onCandidates={() => { setSelectedCandidateProfile(null); setCandidateFilters({}); setPage("candidates"); }}
              onJobRoles={() => setPage("jobs")}
            />
          ) : page === "interviews" ? (
            <InterviewScheduler
              key={openInterviewForm ? "interview-create" : "interview-list"}
              openCreate={openInterviewForm}
              onOpenCandidate={(analysis) => { setSelectedCandidateProfile(analysis); setCandidateFilters({}); setPage("candidates"); }}
            />
          ) : (
            <>
          <div className="mb-7 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <p className="mb-1 text-xs font-semibold text-[#8d918f]">{currentDate}</p>
              <h1 className="text-[30px] font-extrabold tracking-[-0.045em] text-[#171c1a] sm:text-[34px]">Recruitment overview</h1>
              <p className="mt-1 text-sm text-[#777c79]">Welcome back, {userName}. Here’s what’s happening with your talent pipeline.</p>
            </div>
            <div className="flex gap-2">
              <button type="button" onClick={refreshDashboard} className="secondary-action">
                <Icon name="refresh" className={`h-4 w-4 ${refreshed ? "animate-spin" : ""}`} />
                Refresh
              </button>
              <button type="button" onClick={() => setPage("analyzer")} className="primary-action">
                <Icon name="upload" className="h-4 w-4" />
                Upload resume
              </button>
            </div>
          </div>

          <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              { label: "Total resumes", value: analyses.length.toLocaleString(), icon: "resume" as IconName, theme: "teal" },
              { label: "Total candidates", value: candidateCount.toLocaleString(), icon: "candidates" as IconName, theme: "blue" },
              {
                label: "Average ATS score",
                value: analyses.length
                  ? (analyses.reduce((total, analysis) => total + analysis.score, 0) / analyses.length).toFixed(1)
                  : "0",
                icon: "sparkles" as IconName,
                theme: "purple",
              },
              { label: "Open job roles", value: openJobRoleCount.toLocaleString(), icon: "jobs" as IconName, theme: "amber" },
            ].map((metric) => (
              <article key={metric.label} className="metric-card">
                <div className={`metric-icon ${metric.theme}`}><Icon name={metric.icon} /></div>
                <div className="mt-5 flex items-end justify-between gap-2">
                  <div>
                    <p className="text-[12px] font-semibold text-[#888d8a]">{metric.label}</p>
                    <p className="mt-1 text-[27px] font-extrabold tracking-[-0.04em] text-[#1c211f]">{metric.value}</p>
                  </div>
                </div>
              </article>
            ))}
          </section>

          <section className="mb-6 grid gap-5 xl:grid-cols-[1.7fr_1fr]">
            <article className="dashboard-card">
              <div className="card-heading">
                <div>
                  <h2>Resume uploads</h2>
                  <p>Applications received over the last 7 months</p>
                </div>
                <select aria-label="Resume chart period" defaultValue="7-months">
                  <option value="7-months">Last 7 months</option>
                  <option value="year">This year</option>
                </select>
              </div>
              <div className="chart-wrap">
                {analyses.length ? (
                  <div className="flex h-full items-end justify-around gap-3 px-4 pb-2">
                    {Array.from({ length: 7 }, (_, index) => {
                      const date = new Date();
                      date.setMonth(date.getMonth() - (6 - index), 1);
                      const count = analyses.filter((analysis) => {
                        const created = new Date(analysis.createdAt);
                        return created.getFullYear() === date.getFullYear() && created.getMonth() === date.getMonth();
                      }).length;
                      const max = Math.max(
                        1,
                        ...Array.from({ length: 7 }, (_, monthIndex) => {
                          const month = new Date();
                          month.setMonth(month.getMonth() - (6 - monthIndex), 1);
                          return analyses.filter((analysis) => {
                            const created = new Date(analysis.createdAt);
                            return created.getFullYear() === month.getFullYear() && created.getMonth() === month.getMonth();
                          }).length;
                        }),
                      );
                      return (
                        <div key={date.toISOString()} className="flex h-full flex-1 flex-col items-center justify-end gap-2">
                          <span className="text-xs font-bold text-[#5f6964]">{count}</span>
                          <span className="w-full max-w-10 rounded-t-md bg-[#12aa98]" style={{ height: `${Math.max(count ? 8 : 2, (count / max) * 78)}%` }} />
                          <span className="text-xs text-[#929693]">{date.toLocaleDateString("en-US", { month: "short" })}</span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="dashboard-interview-empty"><p>No resume upload data yet</p></div>
                )}
              </div>
            </article>

            <article className="dashboard-card">
              <div className="card-heading">
                <div><h2>Candidate status</h2><p>Current pipeline distribution</p></div>
                <button type="button" onClick={() => showNotice("Pipeline details opened")} className="text-xs font-bold text-[#159c8c]">View all</button>
              </div>
              <div className="flex items-center justify-center gap-8 py-4">
              <div className="status-donut"><div><strong>{totalCandidates}</strong><span>Total</span></div></div>
              <div className="space-y-3">
                {statusCounts.map(({ label, value }, index) => (
                  <div key={label} className="flex min-w-[120px] items-center gap-2 text-xs">
                    <span className={`h-2 w-2 rounded-full ${["bg-[#15b8a5]", "bg-[#7468d7]", "bg-[#f2b84b]", "bg-[#ec6f78]"][index]}`} />
                    <span className="flex-1 text-[#717673]">{label}</span>
                    <b className="text-[#2b302e]">{value}</b>
                  </div>
                  ))}
                </div>
              </div>
            </article>
          </section>

          <section className="mb-6 grid gap-5 xl:grid-cols-[1.7fr_1fr]">
            <article className="dashboard-card overflow-hidden">
              <div className="card-heading">
                <div><h2>Recent candidates</h2><p>Latest resume submissions and AI analysis</p></div>
                <button type="button" onClick={() => showNotice("Candidate directory opened")} className="view-link">View all candidates →</button>
              </div>
              <div className="overflow-x-auto">
                <table className="candidate-table">
                  <thead><tr><th>Candidate</th><th>Target role</th><th>ATS score</th><th>Uploaded</th><th>Status</th><th /></tr></thead>
                  <tbody>
                    {recentCandidates.map((analysis, index) => {
                      const candidateName = analysis.candidate.name;
                      const initials = candidateName === "Not found"
                        ? "NA"
                        : candidateName.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
                      const status = analysis.recruitmentStatus ?? "New";
                      return (
                        <tr key={analysis.id}>
                          <td><div className="flex items-center gap-3"><span className={`candidate-avatar ${["mint", "purple", "amber", "blue"][index % 4]}`}>{initials}</span><b>{candidateName}</b></div></td>
                          <td>{analysis.role}</td>
                          <td><div className="flex items-center gap-2"><span className="score-track"><i className={`score-fill score-${analysis.score}`} /></span><b>{analysis.score}</b></div></td>
                          <td>{new Date(analysis.createdAt).toLocaleDateString()}</td>
                          <td><span className={`status-pill ${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span></td>
                          <td><button type="button" onClick={() => { setSelectedAnalysis(analysis); setPage("analyzer"); }} className="row-action">•••</button></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {!recentCandidates.length && <div className="dashboard-interview-empty"><p>No resumes analyzed yet</p><button type="button" onClick={() => setPage("analyzer")}>Analyze a resume →</button></div>}
              </div>
            </article>

            <article className="dashboard-card">
              <div className="card-heading">
                <div><h2>Upcoming interviews</h2><p>Your schedule for today</p></div>
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-[#effaf8] text-[#13a795]"><Icon name="calendar" className="h-4 w-4" /></div>
              </div>
              <div className="space-y-3">
                {upcomingInterviews.length ? upcomingInterviews.slice(0, 5).map((interview, index) => (
                  <div key={interview.id} className="interview-row">
                    <div className="w-12 text-center"><b>{new Date(`${interview.date}T${interview.startTime}`).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</b><span>{new Date(`${interview.date}T00:00:00`).toLocaleDateString([], { month: "short", day: "numeric" })}</span></div>
                    <span className={`candidate-avatar ${["mint", "purple", "amber", "blue"][index % 4]}`}>{interview.candidateName.split(/\s+/).slice(0, 2).map((part) => part[0]).join("")}</span>
                    <div className="min-w-0 flex-1"><p>{interview.candidateName}</p><span>{interview.jobRoleTitle} · {interview.type}</span></div>
                    <button type="button" onClick={() => { setOpenInterviewForm(false); setPage("interviews"); }}>View</button>
                  </div>
                )) : <div className="dashboard-interview-empty"><p>No upcoming interviews</p><button type="button" onClick={() => { setOpenInterviewForm(true); setPage("interviews"); }}>Schedule one →</button></div>}
              </div>
            </article>
          </section>

          <section className="grid gap-5 lg:grid-cols-2">
            <article className="dashboard-card">
              <div className="card-heading"><div><h2>Top skills in demand</h2><p>Based on active job requirements</p></div></div>
              <div className="space-y-4">
                {topSkills.map(([skill, count]) => (
                  <div key={skill}>
                    <div className="mb-1.5 flex justify-between text-xs"><b className="text-[#424744]">{skill}</b><span className="font-bold text-[#929693]">{count}</span></div>
                    <div className="skill-track"><span style={{ width: `${(count / maxSkillCount) * 100}%` }} /></div>
                  </div>
                ))}
                {!topSkills.length && <div className="dashboard-interview-empty"><p>No active job role skills yet</p><button type="button" onClick={() => setPage("jobs")}>Create a job role →</button></div>}
              </div>
            </article>
            <article className="dashboard-card">
              <div className="card-heading"><div><h2>Recent activity</h2><p>Latest updates across recruitment</p></div></div>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={`${activity.title}-${activity.date}`} className="activity-row">
                    <div className={`metric-icon ${activity.theme}`}><Icon name={activity.icon} className="h-4 w-4" /></div>
                    <div className="min-w-0 flex-1"><p>{activity.title}</p><span>{activity.body}</span></div>
                    <time>{new Date(activity.date).toLocaleDateString()}</time>
                  </div>
                ))}
                {!recentActivities.length && <div className="dashboard-interview-empty"><p>No recent activity</p></div>}
              </div>
            </article>
          </section>

          <section className="dashboard-quick-actions">
            <article>
              <div className="metric-icon amber"><Icon name="jobs" /></div>
              <div><h2>Job Roles</h2><p>Create and manage job requirements.</p></div>
              <button type="button" onClick={() => setPage("jobs")}>Manage Job Roles →</button>
            </article>
            <article>
              <div className="metric-icon purple"><Icon name="compare" /></div>
              <div><h2>Skill Gap Analysis</h2><p>Compare candidate skills with job requirements.</p></div>
              <button type="button" onClick={() => { setSelectedJobRole(null); setPage("skillgap"); }}>Analyze Skill Gaps →</button>
            </article>
            <article>
              <div className="metric-icon blue"><Icon name="calendar" /></div>
              <div><h2>Schedule Interview</h2><p>Coordinate candidates, roles, and interviewers.</p></div>
              <button type="button" onClick={() => { setOpenInterviewForm(true); setPage("interviews"); }}>Schedule Interview →</button>
            </article>
          </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function App() {
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "done">("idle");
  const [authenticated, setAuthenticated] = useState(hasAuthToken());
  const [email, setEmail] = useState("surajjangde1312@gmail.com");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  useEffect(() => {
    if (!authenticated) return;
    migrateIndexedDbToSupabase().catch((migrationError) => {
      console.error("IndexedDB migration could not be completed:", migrationError);
    });
  }, [authenticated]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setLoginError("");
    try {
      await loginRecruiter(email, password);
      setStatus("done");
      setAuthenticated(true);
    } catch (error) {
      setStatus("idle");
      setLoginError(error instanceof Error ? error.message : "Sign in failed.");
    }
  }

  if (authenticated) {
    return (
      <Dashboard
        onLogout={() => {
          logoutRecruiter();
          setAuthenticated(false);
          setStatus("idle");
        }}
      />
    );
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#f8f7fb] px-5 py-5 text-[#26213f] selection:bg-[#f7afa7] lg:px-8 lg:py-8">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <div className="relative mx-auto grid min-h-[calc(100vh-40px)] max-w-[1480px] overflow-hidden rounded-[30px] border border-white/80 bg-white/76 shadow-[0_30px_80px_rgba(57,42,103,0.10)] backdrop-blur-sm lg:min-h-[calc(100vh-64px)] lg:grid-cols-[1.03fr_0.97fr]">
        <section className="relative hidden overflow-hidden bg-[#ece8f6] lg:block">
          <div className="absolute inset-0">
            <img
              src={recruiterImage}
              alt="Recruitment professional working from a bright modern office"
              className="h-full w-full object-cover object-[54%_center]"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[#302961]/5 via-transparent to-[#29205b]/55" />
            <div className="absolute inset-0 bg-[#6049a8]/8 mix-blend-color" />
          </div>

          <div className="absolute left-10 top-10 rounded-2xl bg-white/92 px-5 py-3.5 shadow-[0_16px_35px_rgba(39,28,76,0.14)] backdrop-blur-md">
            <Logo />
          </div>

          <div className="absolute bottom-0 left-0 right-0 p-10 xl:p-14">
            <div className="max-w-[570px] text-white">
              <div className="mb-5 flex -space-x-2">
                {["JD", "MA", "KL"].map((initials, index) => (
                  <span
                    key={initials}
                    className={`grid h-10 w-10 place-items-center rounded-full border-2 border-white/80 text-[11px] font-bold ${
                      ["bg-[#f48b7d]", "bg-[#7565aa]", "bg-[#e0a65d]"][index]
                    }`}
                  >
                    {initials}
                  </span>
                ))}
                <span className="grid h-10 w-10 place-items-center rounded-full border-2 border-white/80 bg-white text-xs font-extrabold text-[#443875]">
                  +8
                </span>
              </div>
              <h2 className="max-w-[520px] text-4xl font-bold leading-[1.12] tracking-[-0.045em] xl:text-[46px]">
                Hire the people who move your mission forward.
              </h2>
              <p className="mt-4 max-w-[480px] text-[15px] leading-7 text-white/80">
                AI-powered sourcing, screening, and insights—built to help
                modern teams hire with clarity.
              </p>
            </div>
          </div>
        </section>

        <section className="relative flex min-h-[calc(100vh-40px)] flex-col bg-[#fffefe] px-6 py-7 sm:px-12 lg:min-h-0 lg:px-16 lg:py-10 xl:px-24">
          <div className="flex items-center justify-between lg:justify-end">
            <div className="lg:hidden">
              <Logo />
            </div>
            <p className="hidden text-sm text-[#736e82] sm:block">
              New to TalentFlow?{" "}
              <a
                href="#signup"
                className="font-bold text-[#493c8b] transition-colors hover:text-[#f06f61]"
              >
                Create an account
              </a>
            </p>
          </div>

          <div className="mx-auto flex w-full max-w-[465px] flex-1 flex-col justify-center py-12 lg:py-10">
            <div className="mb-9">
              <div className="mb-5 grid h-12 w-12 place-items-center rounded-2xl bg-[#fcede9] text-[#ed6f61]">
                <svg
                  aria-hidden="true"
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M4 13h16M6 13v7M18 13v7M8 13V7h8v6M10.5 10h3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <p className="mb-2 text-xs font-extrabold uppercase tracking-[0.2em] text-[#f07163]">
                Welcome back
              </p>
              <h1 className="text-[36px] font-extrabold leading-tight tracking-[-0.045em] text-[#241f43] sm:text-[42px]">
                Sign in to your workspace
              </h1>
              <p className="mt-3 text-[15px] leading-6 text-[#777286]">
                Continue building stronger teams, one great match at a time.
              </p>
            </div>

            <form className="space-y-5" onSubmit={handleSubmit}>
              {loginError && <div className="analysis-alert error"><span>{loginError}</span></div>}
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-[13px] font-bold text-[#37314e]"
                >
                  Work email
                </label>
                <div className="field-wrap">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="field-icon"
                    fill="none"
                  >
                    <path
                      d="M4 7.5 12 13l8-5.5M5.5 19h13a1.5 1.5 0 0 0 1.5-1.5v-11A1.5 1.5 0 0 0 18.5 5h-13A1.5 1.5 0 0 0 4 6.5v11A1.5 1.5 0 0 0 5.5 19Z"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    autoComplete="email"
                    placeholder="you@company.com"
                    className="field-input"
                  />
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="text-[13px] font-bold text-[#37314e]"
                  >
                    Password
                  </label>
                  <a
                    href="#forgot"
                    className="text-[12px] font-bold text-[#594b9b] hover:text-[#ee7062]"
                  >
                    Forgot password?
                  </a>
                </div>
                <div className="field-wrap">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="field-icon"
                    fill="none"
                  >
                    <path
                      d="M7 10V8a5 5 0 0 1 10 0v2m-10 0h10a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2Z"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                  </svg>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    required
                    minLength={8}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    className="field-input pr-12"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 rounded-lg p-1 text-[#8e899a] transition hover:bg-[#f4f1f8] hover:text-[#4f438e] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8377bc]"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-5 w-5"
                      fill="none"
                    >
                      {showPassword ? (
                        <>
                          <path
                            d="m4 4 16 16M10.6 10.7a2 2 0 0 0 2.7 2.7M9.8 5.2A10.4 10.4 0 0 1 12 5c5 0 8.5 5 8.5 7a7.4 7.4 0 0 1-1.6 2.8M6.2 6.2C4.5 7.4 3.5 9 3.5 12c0 2 3.5 7 8.5 7a9 9 0 0 0 3-.5"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinecap="round"
                          />
                        </>
                      ) : (
                        <>
                          <path
                            d="M3.5 12c0-2 3.5-7 8.5-7s8.5 5 8.5 7-3.5 7-8.5 7-8.5-5-8.5-7Z"
                            stroke="currentColor"
                            strokeWidth="1.8"
                          />
                          <circle
                            cx="12"
                            cy="12"
                            r="2.5"
                            stroke="currentColor"
                            strokeWidth="1.8"
                          />
                        </>
                      )}
                    </svg>
                  </button>
                </div>
              </div>

              <label className="flex w-fit cursor-pointer items-center gap-2.5 text-[13px] text-[#656073]">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-[#cfcad8] accent-[#4b3e8c]"
                />
                Keep me signed in
              </label>

              <button
                type="submit"
                disabled={status === "loading"}
                className="flex h-[54px] w-full items-center justify-center gap-2 rounded-[14px] bg-[#302768] text-sm font-extrabold text-white shadow-[0_14px_28px_rgba(48,39,104,0.22)] transition hover:-translate-y-0.5 hover:bg-[#3c317e] hover:shadow-[0_17px_32px_rgba(48,39,104,0.26)] focus:outline-none focus-visible:ring-4 focus-visible:ring-[#cfc8ed] disabled:cursor-wait disabled:opacity-80"
              >
                {status === "loading" && <span className="spinner" />}
                {status === "idle"
                  ? "Sign in to dashboard"
                  : status === "loading"
                    ? "Signing you in..."
                    : "You're all set"}
                {status === "idle" && (
                  <span aria-hidden="true" className="text-lg leading-none">
                    →
                  </span>
                )}
              </button>
            </form>

            <div className="my-7 flex items-center gap-4">
              <span className="h-px flex-1 bg-[#ebe8ef]" />
              <span className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#aaa5b3]">
                or continue with
              </span>
              <span className="h-px flex-1 bg-[#ebe8ef]" />
            </div>

            <button
              type="button"
              className="flex h-[50px] items-center justify-center gap-3 rounded-[14px] border border-[#dedbe5] bg-white text-sm font-bold text-[#3a354d] transition hover:border-[#bdb6d5] hover:bg-[#faf9fc] focus:outline-none focus-visible:ring-4 focus-visible:ring-[#e1ddf2]"
            >
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5">
                <path
                  fill="#4285F4"
                  d="M21.6 12.23c0-.71-.06-1.24-.2-1.8H12v3.4h5.52a4.7 4.7 0 0 1-2.05 3.08l-.02.11 2.97 2.3.2.02c1.85-1.7 2.98-4.22 2.98-7.11Z"
                />
                <path
                  fill="#34A853"
                  d="M12 22c2.68 0 4.93-.88 6.58-2.4l-3.15-2.43c-.84.57-1.98.97-3.43.97a5.96 5.96 0 0 1-5.64-4.12l-.1.01-3.09 2.4-.04.1A9.94 9.94 0 0 0 12 22Z"
                />
                <path
                  fill="#FBBC05"
                  d="M6.36 14.02a6.12 6.12 0 0 1-.34-2.02c0-.7.12-1.38.33-2.02v-.12L3.22 7.43l-.1.05A10 10 0 0 0 2 12c0 1.62.39 3.15 1.12 4.52l3.24-2.5Z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.86c1.86 0 3.12.8 3.84 1.47l2.8-2.74A9.5 9.5 0 0 0 12 2a9.94 9.94 0 0 0-8.87 5.48l3.23 2.5A5.98 5.98 0 0 1 12 5.86Z"
                />
              </svg>
              Continue with Google
            </button>

            <p className="mt-8 text-center text-xs leading-5 text-[#928d9d] sm:hidden">
              New to TalentFlow?{" "}
              <a href="#signup" className="font-bold text-[#493c8b]">
                Create an account
              </a>
            </p>
          </div>

          <p className="text-center text-[11px] leading-5 text-[#aaa5b2]">
            By continuing, you agree to our{" "}
            <a href="#terms" className="underline underline-offset-2">
              Terms
            </a>{" "}
            and{" "}
            <a href="#privacy" className="underline underline-offset-2">
              Privacy Policy
            </a>
            .
          </p>
        </section>
      </div>
    </main>
  );
}

export default App;
