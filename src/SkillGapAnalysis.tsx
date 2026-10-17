import { useEffect, useMemo, useState } from "react";
import { jsPDF } from "jspdf";
import { getSavedAnalyses } from "./lib/analysisStorage";
import { getJobRoles, type JobRole } from "./lib/jobRoleStorage";
import type { AnalysisResult } from "./lib/resumeAnalyzer";

type Props = {
  initialRole?: JobRole | null;
  onAnalyze: (role?: JobRole) => void;
  onCandidate: (analysis: AnalysisResult) => void;
  onCandidates: () => void;
  onJobRoles: () => void;
};

const paths = {
  compare: "M7 7h13m0 0-3-3m3 3-3 3M17 17H4m0 0 3-3m-3 3 3 3",
  person: "M16 19c0-2.2-1.8-4-4-4s-4 1.8-4 4M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
  jobs: "M4 8h16v11H4V8Zm5 0V5h6v3M4 12h16",
  check: "m6 12 4 4 8-9",
  missing: "M8 8l8 8m0-8-8 8",
  plus: "M12 7v10m-5-5h10",
  export: "M12 4v11m0-11L8 8m4-4 4 4M5 14v5h14v-5",
  tip: "M9 18h6m-5 3h4m3-11a5 5 0 1 0-8.5 3.6c.9.8 1.5 1.5 1.5 2.4h4c0-.9.6-1.6 1.5-2.4A4.8 4.8 0 0 0 17 10Z",
};

function GapIcon({ name, className = "h-5 w-5" }: { name: keyof typeof paths; className?: string }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="none"><path d={paths[name]} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

function candidateKey(analysis: AnalysisResult) {
  if (analysis.candidate.email !== "Not found") return analysis.candidate.email.toLowerCase();
  if (analysis.candidate.phone !== "Not found") return analysis.candidate.phone.replace(/\D/g, "");
  return `${analysis.fileName}:${analysis.candidate.name}`;
}

function csvCell(value: string | number) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

export default function SkillGapAnalysis({
  initialRole,
  onAnalyze,
  onCandidate,
  onCandidates,
  onJobRoles,
}: Props) {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [candidateId, setCandidateId] = useState("");
  const [roleId, setRoleId] = useState(initialRole?.id ?? "");
  const [compared, setCompared] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    Promise.all([getSavedAnalyses(), getJobRoles()])
      .then(([savedAnalyses, savedRoles]) => {
        setAnalyses(savedAnalyses);
        setRoles(savedRoles);
        if (initialRole) setRoleId(initialRole.id);
      })
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Comparison data could not be loaded."))
      .finally(() => setLoading(false));
  }, [initialRole]);

  const candidates = useMemo(() => {
    const latest = new Map<string, AnalysisResult>();
    analyses.forEach((analysis) => {
      const key = candidateKey(analysis);
      const existing = latest.get(key);
      if (!existing || existing.createdAt < analysis.createdAt) latest.set(key, analysis);
    });
    return [...latest.values()];
  }, [analyses]);

  const candidate = candidates.find((item) => candidateKey(item) === candidateId) ?? null;
  const role = roles.find((item) => item.id === roleId) ?? initialRole ?? null;

  const comparison = useMemo(() => {
    if (!candidate || !role) return null;
    const availableMap = new Map<string, string>();
    [...candidate.candidate.skills, ...candidate.matchedSkills, ...candidate.additionalSkills].forEach((skill) => availableMap.set(skill.trim().toLowerCase(), skill));
    const requiredMap = new Map(role.requiredSkills.map((skill) => [skill.trim().toLowerCase(), skill]));
    const matched = role.requiredSkills.filter((skill) => availableMap.has(skill.trim().toLowerCase()));
    const missing = role.requiredSkills.filter((skill) => !availableMap.has(skill.trim().toLowerCase()));
    const additional = [...availableMap.entries()].filter(([key]) => !requiredMap.has(key)).map(([, label]) => label);
    const coverage = role.requiredSkills.length ? Math.round((matched.length / role.requiredSkills.length) * 100) : null;
    const sameRoleAnalysis = analyses.find((item) => candidateKey(item) === candidateId && item.role === role.title);
    return { matched, missing, additional, coverage, sameRoleAnalysis };
  }, [analyses, candidate, candidateId, role]);

  function flash(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2500);
  }

  function exportCsv() {
    if (!candidate || !role || !comparison) return;
    const rows = [
      ["Candidate", candidate.candidate.name],
      ["Email", candidate.candidate.email],
      ["Job Role", role.title],
      ["Analysis Date", new Date(candidate.createdAt).toLocaleString()],
      ["Estimated Match Score", comparison.sameRoleAnalysis ? `${comparison.sameRoleAnalysis.score}%` : "Not available for this role"],
      ["Skill Coverage", comparison.coverage === null ? "Not available" : `${comparison.coverage}%`],
      ["Matched Skills", comparison.matched.join("; ") || "None identified"],
      ["Missing Skills", comparison.missing.join("; ") || "None identified"],
      ["Additional Skills", comparison.additional.join("; ") || "None identified"],
    ];
    const csv = [["Field", "Value"], ...rows].map((row) => row.map(csvCell).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${candidate.candidate.name}-${role.title}-skill-gap.csv`;
    link.click();
    URL.revokeObjectURL(url);
    flash("Skill gap CSV summary exported.");
  }

  function exportPdf() {
    if (!candidate || !role || !comparison) return;
    const pdf = new jsPDF();
    pdf.setTextColor(35, 42, 38);
    pdf.setFontSize(20);
    pdf.text("TalentFlow Skill Gap Report", 18, 22);
    pdf.setFontSize(10);
    pdf.text(`Candidate: ${candidate.candidate.name}`, 18, 34);
    pdf.text(`Job role: ${role.title}`, 18, 41);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 18, 48);
    pdf.text(`Estimated match score: ${comparison.sameRoleAnalysis ? `${comparison.sameRoleAnalysis.score}%` : "Not available for this role"}`, 18, 58);
    pdf.text(`Skill coverage: ${comparison.coverage === null ? "Not available" : `${comparison.coverage}%`}`, 18, 65);
    let y = 79;
    [["Matched Skills", comparison.matched], ["Missing Skills", comparison.missing], ["Additional Skills", comparison.additional]].forEach(([title, skills]) => {
      pdf.setFontSize(13);
      pdf.text(title as string, 18, y);
      y += 8;
      pdf.setFontSize(10);
      const lines = pdf.splitTextToSize((skills as string[]).join(", ") || "None identified", 170);
      pdf.text(lines, 22, y);
      y += lines.length * 6 + 10;
    });
    pdf.setFontSize(13);
    pdf.text("Recommended Next Steps", 18, y);
    y += 9;
    pdf.setFontSize(10);
    const recommendations = comparison.missing.length
      ? [
          `Prioritize evidence or development for: ${comparison.missing.slice(0, 4).join(", ")}.`,
          "Add truthful project or work examples that demonstrate relevant required skills.",
          "Tailor resume language to the role description without claiming unsupported qualifications.",
        ]
      : ["No required skill gaps were identified in the extracted resume evidence. Review depth and outcomes for each skill."];
    recommendations.forEach((item, index) => {
      const lines = pdf.splitTextToSize(`${index + 1}. ${item}`, 168);
      pdf.text(lines, 22, y);
      y += lines.length * 6 + 4;
    });
    pdf.save(`${candidate.candidate.name}-${role.title}-skill-gap.pdf`);
    flash("Skill gap PDF report exported.");
  }

  if (loading) return <div className="analytics-loading"><span className="candidate-loader" /><h2>Loading comparison data</h2><p>Retrieving saved candidates and job requirements...</p></div>;

  return (
    <>
      {notice && <div className="dashboard-toast">{notice}</div>}
      <div className="analyzer-breadcrumb"><span>Dashboard</span><span>/</span><b>Skill Gap Analysis</b></div>
      <div className="gap-page-heading">
        <div><h1>Skill Gap Analysis</h1><p>Compare candidate skills with job requirements and identify areas for improvement.</p></div>
        <button type="button" className="secondary-action" disabled={!comparison || !compared} onClick={exportPdf}><GapIcon name="export" className="h-4 w-4" />Export Skill Gap Report</button>
      </div>
      {error && <div className="analysis-alert error"><b>Analysis unavailable</b><span>{error}</span></div>}

      {!candidates.length ? (
        <section className="analytics-empty-state"><div><GapIcon name="person" /></div><h2>No saved candidates yet</h2><p>Analyze and save a resume before comparing candidate evidence with a job role.</p><button type="button" className="primary-action" onClick={() => onAnalyze()}>Analyze New Resume</button></section>
      ) : !roles.length ? (
        <section className="analytics-empty-state"><div><GapIcon name="jobs" /></div><h2>No job roles created yet</h2><p>Create a role with required skills before starting a skill gap comparison.</p><button type="button" className="primary-action" onClick={onJobRoles}>Create Job Role</button></section>
      ) : (
        <>
          <section className="gap-selector-card">
            <div className="gap-selector-heading"><div className="metric-icon teal"><GapIcon name="compare" /></div><div><h2>Build a skill comparison</h2><p>Select a saved candidate and a job role. Closed roles remain available for historical review.</p></div></div>
            <div className="gap-selectors">
              <label><span>Candidate</span><select value={candidateId} onChange={(event) => { setCandidateId(event.target.value); setCompared(false); }}><option value="">Select a saved candidate</option>{candidates.map((item) => <option key={candidateKey(item)} value={candidateKey(item)}>{item.candidate.name} · {item.candidate.email}</option>)}</select></label>
              <div className="gap-connector"><GapIcon name="compare" /></div>
              <label><span>Job Role</span><select value={roleId} onChange={(event) => { setRoleId(event.target.value); setCompared(false); }}><option value="">Select a job role</option>{roles.map((item) => <option key={item.id} value={item.id}>{item.title} · {item.status}</option>)}</select></label>
              <button type="button" className="primary-action" disabled={!candidate || !role} onClick={() => setCompared(true)}>Compare Skills</button>
            </div>
            {candidate && <button type="button" className="gap-profile-link" onClick={() => onCandidate(candidate)}>Open selected candidate profile →</button>}
          </section>

          {!compared ? (
            <section className="gap-ready-state"><div><GapIcon name="compare" /></div><h2>Select both records to compare</h2><p>The comparison uses extracted resume evidence and the selected role's saved required skills.</p></section>
          ) : comparison && candidate && role ? (
            <>
              <section className="gap-comparison-hero">
                <div className="gap-identity"><span className="candidate-avatar mint">{candidate.candidate.name === "Not found" ? "NA" : candidate.candidate.name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("")}</span><div><small>Candidate</small><h2>{candidate.candidate.name}</h2><p>{candidate.candidate.email} · {candidate.recruitmentStatus ?? "New"}</p></div></div>
                <div className="gap-versus"><GapIcon name="compare" /><span>compared with</span></div>
                <div className="gap-identity"><span className="role-card-icon"><GapIcon name="jobs" /></span><div><small>Job Role</small><h2>{role.title}</h2><p>{role.department} · {role.status}</p></div></div>
                <div className="gap-score"><strong>{comparison.sameRoleAnalysis ? `${comparison.sameRoleAnalysis.score}%` : "N/A"}</strong><span>Estimated match score</span><small>{comparison.sameRoleAnalysis ? new Date(comparison.sameRoleAnalysis.createdAt).toLocaleDateString() : "No saved analysis for this role"}</small></div>
              </section>

              <section className="gap-kpi-grid">
                {[
                  ["Required Skills", role.requiredSkills.length, "Defined for selected role", "jobs", "blue"],
                  ["Matched Skills", comparison.matched.length, "Identified in resume evidence", "check", "teal"],
                  ["Missing Skills", comparison.missing.length, "Not identified in resume", "missing", "coral"],
                  ["Additional Skills", comparison.additional.length, "Beyond required skills", "plus", "purple"],
                ].map(([label, value, detail, icon, tone]) => <article key={label as string} className="analytics-kpi-card"><div className={`metric-icon ${tone}`}><GapIcon name={icon as keyof typeof paths} /></div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></article>)}
              </section>

              <section className="gap-main-grid">
                <article className="analytics-card gap-coverage-card">
                  <div className="analytics-card-heading"><div><h2>Visual Skill Comparison</h2><p>Coverage of required role skills</p></div></div>
                  <div className="coverage-score"><strong>{comparison.coverage === null ? "N/A" : `${comparison.coverage}%`}</strong><span>Skill coverage</span></div>
                  <svg viewBox="0 0 100 8" preserveAspectRatio="none" aria-label="Skill coverage"><rect width="100" height="8" rx="4" className="coverage-track" /><rect width={comparison.coverage ?? 0} height="8" rx="4" className="coverage-value" /></svg>
                  <div className="coverage-legend"><span><i className="matched" />{comparison.matched.length} matched</span><span><i className="missing" />{comparison.missing.length} missing</span></div>
                  <p>Skill Coverage = Matched Required Skills ÷ Total Required Skills × 100</p>
                  <small>Skill coverage is separate from the overall estimated match score, which also considers keywords and experience evidence.</small>
                </article>
                <article className="analytics-card gap-context-card"><div className="analytics-card-heading"><div><h2>Comparison Context</h2><p>Available evidence used for this view</p></div></div><div><span>Saved analysis role<b>{candidate.role}</b></span><span>Selected comparison role<b>{role.title}</b></span><span>Resume evidence items<b>{candidate.candidate.experience.length + candidate.candidate.projects.length}</b></span><span>Analysis availability<b>{comparison.sameRoleAnalysis ? "Exact role analysis found" : "Skill-only comparison"}</b></span></div></article>
              </section>

              <section className="gap-skill-columns">
                <article className="gap-skill-card matched"><div className="gap-skill-title"><span><GapIcon name="check" /></span><div><h2>Matched Skills</h2><p>Required skills identified in extracted resume evidence</p></div><strong>{comparison.matched.length}</strong></div><div className="gap-skill-list">{comparison.matched.length ? comparison.matched.map((skill) => <div key={skill}><span><GapIcon name="check" className="h-4 w-4" /></span><div><b>{skill}</b><p>Skill term identified in the extracted resume content. Review the source resume to assess depth and proficiency.</p></div></div>) : <p className="gap-list-empty">No required skill matches were identified.</p>}</div></article>
                <article className="gap-skill-card missing"><div className="gap-skill-title"><span><GapIcon name="missing" /></span><div><h2>Missing Skills</h2><p>Required skills not identified in available resume text</p></div><strong>{comparison.missing.length}</strong></div><div className="gap-skill-list">{comparison.missing.length ? comparison.missing.map((skill, index) => <div key={skill}><span><GapIcon name="missing" className="h-4 w-4" /></span><div><b>{skill}<em>{index < Math.ceil(comparison.missing.length / 2) ? "Higher priority" : "Review"}</em></b><p>Required by {role.title}. Consider adding truthful evidence or developing a relevant practical project.</p></div></div>) : <p className="gap-list-empty">No required skill gaps were identified in the extracted evidence.</p>}</div><small className="gap-disclaimer">“Missing” means not identified in the available resume content; it does not prove the candidate lacks the skill.</small></article>
                <article className="gap-skill-card additional"><div className="gap-skill-title"><span><GapIcon name="plus" /></span><div><h2>Additional Skills</h2><p>Relevant extracted skills beyond this role's requirements</p></div><strong>{comparison.additional.length}</strong></div><div className="gap-skill-list">{comparison.additional.length ? comparison.additional.map((skill) => <div key={skill}><span><GapIcon name="plus" className="h-4 w-4" /></span><div><b>{skill}</b><p>Present in saved resume evidence but not listed as a required skill for this role.</p></div></div>) : <p className="gap-list-empty">No additional skills were identified.</p>}</div></article>
              </section>

              <article className="analytics-card gap-recommendations"><div className="analytics-card-heading"><div><h2>Recommended Next Steps</h2><p>Explainable recommendations based on the selected requirements and saved evidence</p></div><GapIcon name="tip" /></div><div>{(comparison.missing.length ? [`Prioritize the most important missing requirements: ${comparison.missing.slice(0, 4).join(", ")}.`, "Add truthful project or work examples that demonstrate required skills already possessed.", `Tailor the resume summary and evidence to the ${role.title} description without adding unsupported claims.`, "Use measurable outcomes to make existing experience and project evidence easier to evaluate."] : ["No required skill gaps were identified. Review whether each matched skill is supported by clear, outcome-focused evidence.", "Tailor the resume summary to the selected role while preserving factual accuracy."]).map((item, index) => <span key={item}><b>{index + 1}</b><p>{item}</p></span>)}</div></article>

              <div className="gap-report-actions"><button type="button" className="primary-action" onClick={exportPdf}>Export PDF Report</button><button type="button" className="secondary-action" onClick={exportCsv}>Export CSV Summary</button><button type="button" className="secondary-action" onClick={() => onCandidate(candidate)}>View Candidate Profile</button><button type="button" className="secondary-action" onClick={onCandidates}>Return to Candidates</button></div>
            </>
          ) : null}
        </>
      )}
    </>
  );
}
