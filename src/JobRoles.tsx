import { FormEvent, useEffect, useMemo, useState } from "react";
import { getSavedAnalyses } from "./lib/analysisStorage";
import {
  deleteJobRole,
  getJobRoles,
  JOB_ROLES_CHANGED_EVENT,
  saveJobRole,
  type JobRole,
  type JobRoleStatus,
} from "./lib/jobRoleStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";

type Props = {
  onAnalyze: (role: JobRole) => void;
  onCandidates: (role: string) => void;
  onSkillGap: (role: JobRole) => void;
};

const PAGE_SIZE = 6;
const emptyForm: Omit<JobRole, "id" | "createdAt" | "updatedAt"> = {
  title: "",
  department: "",
  description: "",
  requiredSkills: [],
  preferredSkills: [],
  level: "Intermediate",
  minExperience: 0,
  maxExperience: undefined,
  education: "",
  employmentType: "Full-time",
  location: "",
  workMode: "Hybrid",
  salary: "",
  status: "Draft",
};

const paths = {
  jobs: "M4 8h16v11H4V8Zm5 0V5h6v3M4 12h16M10 12v2h4v-2",
  active: "m6 12 4 4 8-9",
  skills: "M7 7h.01M11 7h6m-10 5h.01M11 12h6m-10 5h.01M11 17h6",
  people: "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
  search: "m20 20-4.2-4.2M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z",
  export: "M12 4v11m0-11L8 8m4-4 4 4M5 14v5h14v-5",
  plus: "M12 5v14M5 12h14",
  close: "m7 7 10 10m0-10L7 17",
  location: "M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Zm-8 2a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z",
  edit: "m4 20 4.5-1 10-10-3.5-3.5-10 10L4 20Zm9.5-13.5L17 10",
  trash: "M8 8v10m4-10v10m4-10v10M5 5h14m-11 0 1-2h6l1 2m2 0-1 16H7L6 5",
};

function RoleIcon({ name, className = "h-5 w-5" }: { name: keyof typeof paths; className?: string }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="none">
      <path d={paths[name]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function csvCell(value: string | number) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function SkillEditor({
  label,
  skills,
  onChange,
}: {
  label: string;
  skills: string[];
  onChange: (skills: string[]) => void;
}) {
  const [value, setValue] = useState("");
  function add() {
    const skill = value.trim();
    if (skill && !skills.some((item) => item.toLowerCase() === skill.toLowerCase())) onChange([...skills, skill]);
    setValue("");
  }
  return (
    <div className="role-form-field role-form-wide">
      <span>{label}</span>
      <div className="role-skill-input">
        <input value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); add(); } }} placeholder="Type a skill and press Enter" />
        <button type="button" onClick={add}>Add</button>
      </div>
      <div className="role-form-tags">
        {skills.map((skill) => <span key={skill}>{skill}<button type="button" onClick={() => onChange(skills.filter((item) => item !== skill))}>×</button></span>)}
      </div>
    </div>
  );
}

export default function JobRoles({ onAnalyze, onCandidates, onSkillGap }: Props) {
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("All");
  const [level, setLevel] = useState("All Levels");
  const [type, setType] = useState("All Types");
  const [date, setDate] = useState("All Time");
  const [page, setPage] = useState(1);
  const [form, setForm] = useState<(typeof emptyForm) & { id?: string; createdAt?: string }>({ ...emptyForm });
  const [showForm, setShowForm] = useState(false);
  const [detail, setDetail] = useState<JobRole | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<JobRole | null>(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [savedRoles, savedAnalyses] = await Promise.all([getJobRoles(), getSavedAnalyses()]);
      setRoles(savedRoles);
      setAnalyses(savedAnalyses);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Job roles could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    const reload = () => void load();
    window.addEventListener(JOB_ROLES_CHANGED_EVENT, reload);
    return () => window.removeEventListener(JOB_ROLES_CHANGED_EVENT, reload);
  }, []);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const cutoff = date === "Last 30 Days" ? Date.now() - 30 * 86_400_000 : date === "Last 90 Days" ? Date.now() - 90 * 86_400_000 : 0;
    return roles.filter((role) =>
      (!normalized || `${role.title} ${role.department} ${role.description}`.toLowerCase().includes(normalized)) &&
      (status === "All" || role.status === status) &&
      (level === "All Levels" || role.level === level) &&
      (type === "All Types" || role.employmentType === type) &&
      (!cutoff || new Date(role.createdAt).getTime() >= cutoff),
    );
  }, [date, level, query, roles, status, type]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const allSkills = new Set(roles.flatMap((role) => role.requiredSkills.map((skill) => skill.toLowerCase())));
  const matchedCandidateCount = new Set(analyses.filter((analysis) => roles.some((role) => role.title === analysis.role)).map((analysis) => analysis.candidate.email !== "Not found" ? analysis.candidate.email : analysis.id)).size;

  function flash(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2500);
  }

  function openCreate() {
    setForm({ ...emptyForm, requiredSkills: [], preferredSkills: [] });
    setShowForm(true);
  }

  function openEdit(role: JobRole) {
    setForm({ ...role });
    setDetail(null);
    setShowForm(true);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await persistRole(form.status);
  }

  async function persistRole(nextStatus: JobRoleStatus) {
    if (!form.title.trim() || !form.department.trim() || !form.description.trim() || !form.requiredSkills.length) {
      setError("Add a title, department, description, and at least one required skill.");
      return;
    }
    const now = new Date().toISOString();
    const role: JobRole = {
      ...form,
      id: form.id ?? `job-${crypto.randomUUID()}`,
      title: form.title.trim(),
      department: form.department.trim(),
      description: form.description.trim(),
      status: nextStatus,
      createdAt: form.createdAt ?? now,
      updatedAt: now,
    };
    try {
      await saveJobRole(role);
      setShowForm(false);
      flash(`${role.title} was ${form.id ? "updated" : "created"} successfully.`);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "The role could not be saved.");
    }
  }

  async function updateStatus(role: JobRole, nextStatus: JobRoleStatus) {
    await saveJobRole({ ...role, status: nextStatus, updatedAt: new Date().toISOString() });
    setDetail((current) => current?.id === role.id ? { ...role, status: nextStatus } : current);
    flash(`${role.title} is now ${nextStatus.toLowerCase()}.`);
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      await deleteJobRole(deleteTarget.id);
      setDeleteTarget(null);
      setDetail(null);
      flash("The job role was deleted. Saved candidate analyses were preserved.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "The role could not be deleted.");
    }
  }

  function exportRoles() {
    if (!filtered.length) {
      flash("No job roles are available to export.");
      return;
    }
    const rows = filtered.map((role) => [role.title, role.department, role.status, role.employmentType, role.level, role.workMode, role.location, role.requiredSkills.join("; "), role.preferredSkills.join("; "), formatDate(role.createdAt)]);
    const csv = [["Job Title", "Department", "Status", "Employment Type", "Experience Level", "Work Mode", "Location", "Required Skills", "Preferred Skills", "Date Created"], ...rows].map((row) => row.map(csvCell).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "talentflow-job-roles.csv";
    link.click();
    URL.revokeObjectURL(url);
    flash(`${filtered.length} job roles exported.`);
  }

  function roleStats(role: JobRole) {
    const related = analyses.filter((analysis) => analysis.role === role.title);
    return {
      count: new Set(related.map((item) => item.candidate.email !== "Not found" ? item.candidate.email : item.id)).size,
      average: related.length ? Math.round(related.reduce((sum, item) => sum + item.score, 0) / related.length) : null,
    };
  }

  return (
    <>
      {notice && <div className="dashboard-toast">{notice}</div>}
      <div className="analyzer-breadcrumb"><span>Dashboard</span><span>/</span><b>Job Roles</b></div>
      <div className="role-page-heading">
        <div><h1>Job Roles</h1><p>Manage job openings, define required skills, and review candidate suitability.</p></div>
        <div className="flex gap-2">
          <button type="button" className="secondary-action" onClick={exportRoles}><RoleIcon name="export" className="h-4 w-4" />Export Job Roles</button>
          <button type="button" className="primary-action" onClick={openCreate}><RoleIcon name="plus" className="h-4 w-4" />Create Job Role</button>
        </div>
      </div>

      {error && <div className="analysis-alert error"><b>Unable to continue</b><span>{error}</span><button type="button" onClick={() => setError("")}>Dismiss</button></div>}

      <section className="role-summary-grid">
        {[
          ["Total Job Roles", roles.length, "Saved role definitions", "jobs", "teal"],
          ["Active Job Roles", roles.filter((role) => role.status === "Active").length, "Open for candidate matching", "active", "blue"],
          ["Total Required Skills", allSkills.size, "Unique requirements across roles", "skills", "purple"],
          ["Candidates Matched to Roles", matchedCandidateCount, "From saved resume analyses", "people", "amber"],
        ].map(([label, value, detailText, icon, tone]) => (
          <article key={label as string} className="candidate-summary-card">
            <div className={`metric-icon ${tone}`}><RoleIcon name={icon as keyof typeof paths} /></div>
            <div><span>{label}</span><strong>{value}</strong><small>{detailText}</small></div>
          </article>
        ))}
      </section>

      <section className="roles-directory">
        <div className="roles-toolbar">
          <div className="candidate-search-field"><RoleIcon name="search" className="h-4 w-4" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search job titles and descriptions..." /></div>
          {[
            ["Status", status, setStatus, ["All", "Active", "Draft", "Closed"]],
            ["Experience", level, setLevel, ["All Levels", "Fresher", "Entry Level", "Intermediate", "Experienced"]],
            ["Employment", type, setType, ["All Types", "Full-time", "Part-time", "Internship", "Contract"]],
            ["Created", date, setDate, ["All Time", "Last 30 Days", "Last 90 Days"]],
          ].map(([label, value, setter, options]) => (
            <label key={label as string}><span>{label as string}</span><select value={value as string} onChange={(event) => (setter as (value: string) => void)(event.target.value)}>{(options as string[]).map((option) => <option key={option}>{option}</option>)}</select></label>
          ))}
          <button type="button" className="clear-filter-button" onClick={() => { setQuery(""); setStatus("All"); setLevel("All Levels"); setType("All Types"); setDate("All Time"); }}>Clear filters</button>
        </div>
        <div className="directory-heading"><div><h2>All Job Roles</h2><p>{filtered.length} matching {filtered.length === 1 ? "role" : "roles"}</p></div></div>

        {loading ? <div className="candidate-state"><span className="candidate-loader" /><h3>Loading job roles</h3></div> : !roles.length ? (
          <div className="candidate-state"><div className="candidate-state-icon"><RoleIcon name="jobs" /></div><h3>No job roles created yet</h3><p>Create the first role to define requirements for resume analysis and skill comparisons.</p><button type="button" className="primary-action" onClick={openCreate}>Create Job Role</button></div>
        ) : !filtered.length ? (
          <div className="candidate-state"><div className="candidate-state-icon"><RoleIcon name="search" /></div><h3>No roles match these filters</h3><p>Try changing the search or clearing filters.</p></div>
        ) : (
          <>
            <div className="job-role-grid">
              {visible.map((role) => {
                const stats = roleStats(role);
                return (
                  <article key={role.id} className="job-role-card">
                    <div className="job-role-card-top"><span className={`role-status ${role.status.toLowerCase()}`}>{role.status}</span><button type="button" onClick={() => openEdit(role)} aria-label={`Edit ${role.title}`}><RoleIcon name="edit" className="h-4 w-4" /></button></div>
                    <div className="role-card-icon"><RoleIcon name="jobs" /></div>
                    <h3>{role.title}</h3>
                    <p>{role.department} · {role.employmentType}</p>
                    <div className="role-location"><RoleIcon name="location" className="h-3 w-3" />{role.workMode}{role.location ? ` · ${role.location}` : ""}</div>
                    <div className="role-tags">{role.requiredSkills.slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}{role.requiredSkills.length > 4 && <span>+{role.requiredSkills.length - 4}</span>}</div>
                    <div className="role-card-stats"><span><b>{role.requiredSkills.length}</b>Required skills</span><span><b>{stats.count}</b>Candidates</span><span><b>{stats.average === null ? "—" : `${stats.average}%`}</b>Avg. match</span></div>
                    <div className="role-card-footer"><span>{formatDate(role.createdAt)}</span><button type="button" onClick={() => setDetail(role)}>View details →</button></div>
                  </article>
                );
              })}
            </div>
            <div className="candidate-pagination"><p>Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}</p><div><button type="button" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><button type="button" className="active">{page}</button><button type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}>Next</button></div></div>
          </>
        )}
      </section>

      {showForm && (
        <div className="candidate-modal" role="dialog" aria-modal="true" aria-label={form.id ? "Edit job role" : "Create job role"}>
          <button type="button" className="candidate-modal-backdrop" onClick={() => setShowForm(false)} aria-label="Close form" />
          <form className="role-form-panel" onSubmit={(event) => void submit(event)}>
            <div className="profile-topbar"><div><span>{form.id ? "Edit Job Role" : "Create Job Role"}</span><p>Define requirements used across candidate analysis.</p></div><button type="button" onClick={() => setShowForm(false)}><RoleIcon name="close" /></button></div>
            <div className="role-form-content">
              <div className="role-form-section"><h2>Role information</h2><div className="role-form-grid">
                <label className="role-form-field"><span>Job Title *</span><input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder="e.g. Senior Data Analyst" /></label>
                <label className="role-form-field"><span>Department *</span><input required value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} placeholder="e.g. Data & Insights" /></label>
                <label className="role-form-field role-form-wide"><span>Job Description *</span><textarea required rows={6} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Describe responsibilities, outcomes, and requirements..." /></label>
                <SkillEditor label="Required Skills *" skills={form.requiredSkills} onChange={(requiredSkills) => setForm({ ...form, requiredSkills })} />
                <SkillEditor label="Preferred Skills" skills={form.preferredSkills} onChange={(preferredSkills) => setForm({ ...form, preferredSkills })} />
              </div></div>
              <div className="role-form-section"><h2>Employment details</h2><div className="role-form-grid">
                <label className="role-form-field"><span>Experience Level</span><select value={form.level} onChange={(event) => setForm({ ...form, level: event.target.value as JobRole["level"] })}>{["Fresher", "Entry Level", "Intermediate", "Experienced"].map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="role-form-field"><span>Employment Type</span><select value={form.employmentType} onChange={(event) => setForm({ ...form, employmentType: event.target.value as JobRole["employmentType"] })}>{["Full-time", "Part-time", "Internship", "Contract"].map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="role-form-field"><span>Minimum Experience</span><input type="number" min="0" value={form.minExperience} onChange={(event) => setForm({ ...form, minExperience: Number(event.target.value) })} /></label>
                <label className="role-form-field"><span>Maximum Experience</span><input type="number" min="0" value={form.maxExperience ?? ""} onChange={(event) => setForm({ ...form, maxExperience: event.target.value ? Number(event.target.value) : undefined })} /></label>
                <label className="role-form-field"><span>Education</span><input value={form.education} onChange={(event) => setForm({ ...form, education: event.target.value })} placeholder="Optional education requirement" /></label>
                <label className="role-form-field"><span>Work Mode</span><select value={form.workMode} onChange={(event) => setForm({ ...form, workMode: event.target.value as JobRole["workMode"] })}>{["Remote", "Hybrid", "On-site"].map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="role-form-field"><span>Location</span><input value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} placeholder="City, country, or region" /></label>
                <label className="role-form-field"><span>Salary Range</span><input value={form.salary} onChange={(event) => setForm({ ...form, salary: event.target.value })} placeholder="Optional" /></label>
              </div></div>
            </div>
            <div className="role-form-actions"><button type="button" className="secondary-action" onClick={() => setShowForm(false)}>Cancel</button><button type="button" className="secondary-action" onClick={() => void persistRole("Draft")}>Save as Draft</button><button type="button" className="primary-action" onClick={() => void persistRole("Active")}>Publish Job</button></div>
          </form>
        </div>
      )}

      {detail && (
        <div className="candidate-modal" role="dialog" aria-modal="true" aria-label="Job role details">
          <button type="button" className="candidate-modal-backdrop" onClick={() => setDetail(null)} aria-label="Close details" />
          <section className="role-detail-panel">
            <div className="profile-topbar"><div><span>Job Role Details</span><p>Created {formatDate(detail.createdAt)} · Updated {formatDate(detail.updatedAt)}</p></div><button type="button" onClick={() => setDetail(null)}><RoleIcon name="close" /></button></div>
            <div className="role-detail-hero"><div className="role-card-icon"><RoleIcon name="jobs" /></div><div><span className={`role-status ${detail.status.toLowerCase()}`}>{detail.status}</span><h2>{detail.title}</h2><p>{detail.department} · {detail.employmentType} · {detail.workMode}</p></div><strong>{roleStats(detail).average === null ? "No score" : `${roleStats(detail).average}% avg.`}</strong></div>
            <div className="role-detail-actions"><button type="button" className="secondary-action" onClick={() => openEdit(detail)}>Edit Job</button><button type="button" className="secondary-action" onClick={() => void updateStatus(detail, detail.status === "Active" ? "Closed" : "Active")}>{detail.status === "Active" ? "Close Job" : "Activate Job"}</button><button type="button" className="primary-action" onClick={() => onCandidates(detail.title)}>View Matching Candidates</button></div>
            <div className="role-detail-content">
              <article><h3>Job Description</h3><p>{detail.description}</p></article>
              <article><h3>Skills & Requirements</h3><b>Required skills</b><div className="role-detail-tags">{detail.requiredSkills.map((skill) => <span key={skill}>{skill}</span>)}</div><b>Preferred skills</b><div className="role-detail-tags preferred">{detail.preferredSkills.length ? detail.preferredSkills.map((skill) => <span key={skill}>{skill}</span>) : <p>Not specified</p>}</div></article>
              <article><h3>Employment Requirements</h3><div className="role-requirement-grid"><span><small>Experience</small><b>{detail.minExperience}{detail.maxExperience ? `–${detail.maxExperience}` : "+"} years · {detail.level}</b></span><span><small>Education</small><b>{detail.education || "Not specified"}</b></span><span><small>Location</small><b>{detail.location || "Not specified"} · {detail.workMode}</b></span><span><small>Salary</small><b>{detail.salary || "Not specified"}</b></span></div></article>
              <article><h3>Candidate Matching</h3><div className="role-match-summary"><span><b>{roleStats(detail).count}</b>Matching candidates</span><span><b>{roleStats(detail).average === null ? "—" : `${roleStats(detail).average}%`}</b>Average match</span></div></article>
            </div>
            <div className="role-context-actions"><button type="button" onClick={() => onAnalyze(detail)}>Analyze a Resume for This Role</button><button type="button" onClick={() => onSkillGap(detail)}>Open Skill Gap Analysis</button><button type="button" className="danger" onClick={() => setDeleteTarget(detail)}>Delete Role</button></div>
          </section>
        </div>
      )}

      {deleteTarget && <div className="confirm-overlay" role="alertdialog" aria-modal="true"><button type="button" className="candidate-modal-backdrop" onClick={() => setDeleteTarget(null)} /><section className="confirm-dialog"><div className="confirm-icon"><RoleIcon name="trash" /></div><h2>Delete this job role?</h2><p><b>{deleteTarget.title}</b> will be removed. Candidate profiles and historical resume analyses will remain intact.</p><div><button type="button" className="secondary-action" onClick={() => setDeleteTarget(null)}>Cancel</button><button type="button" className="danger-action" onClick={() => void confirmDelete()}>Delete Role</button></div></section></div>}
    </>
  );
}
