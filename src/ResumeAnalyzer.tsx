import { ChangeEvent, DragEvent, FormEvent, useEffect, useRef, useState } from "react";
import { downloadAnalysisReport } from "./lib/analysisReport";
import { deleteAnalysis, getSavedAnalyses, saveAnalysis } from "./lib/analysisStorage";
import { extractPdfText, MAX_PDF_SIZE } from "./lib/pdfParser";
import {
  AnalysisResult,
  ROLE_DESCRIPTIONS,
  ROLE_SKILLS,
  analyzeResume,
  inferTargetRole,
} from "./lib/resumeAnalyzer";
import { getJobRoles, type JobRole } from "./lib/jobRoleStorage";

type Props = {
  onReturn: () => void;
  initialAnalysis?: AnalysisResult | null;
  initialJobRole?: JobRole | null;
};

function UploadIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-8 w-8" fill="none">
      <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v5h14v-5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ResultIcon({ type }: { type: "check" | "missing" | "plus" | "tip" }) {
  const paths = {
    check: "m7 12 3 3 7-7",
    missing: "M8 8l8 8m0-8-8 8",
    plus: "M12 7v10m-5-5h10",
    tip: "M9 18h6m-5 3h4m3-11a5 5 0 1 0-8.5 3.6c.9.8 1.5 1.5 1.5 2.4h4c0-.9.6-1.6 1.5-2.4A4.8 4.8 0 0 0 17 10Z",
  };
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none">
      <path d={paths[type]} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function SkillsGroup({
  title,
  description,
  skills,
  type,
}: {
  title: string;
  description: string;
  skills: string[];
  type: "matched" | "missing" | "additional";
}) {
  return (
    <article className={`analysis-skill-card ${type}`}>
      <div className="flex items-start gap-3">
        <span className="analysis-skill-icon">
          <ResultIcon type={type === "matched" ? "check" : type === "missing" ? "missing" : "plus"} />
        </span>
        <div>
          <h3>{title} <span>{skills.length}</span></h3>
          <p>{description}</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {skills.length ? skills.map((skill) => <span key={skill} className="analysis-tag">{skill}</span>) : <span className="text-xs text-[#929793]">None identified</span>}
      </div>
    </article>
  );
}

export default function ResumeAnalyzer({ onReturn, initialAnalysis, initialJobRole }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [role, setRole] = useState("");
  const [level, setLevel] = useState("Intermediate");
  const [jobDescription, setJobDescription] = useState("");
  const [skillInput, setSkillInput] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isReading, setIsReading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [resumeText, setResumeText] = useState("");
  const [roleSuggestion, setRoleSuggestion] = useState<ReturnType<typeof inferTargetRole>>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [feedback, setFeedback] = useState("");
  const [showSaved, setShowSaved] = useState(false);
  const [savedAnalyses, setSavedAnalyses] = useState<AnalysisResult[]>([]);
  const [jobRoles, setJobRoles] = useState<JobRole[]>([]);

  useEffect(() => {
    getSavedAnalyses()
      .then(setSavedAnalyses)
      .catch(() => setFeedback("Saved analyses could not be loaded in this browser."));
  }, []);

  useEffect(() => {
    getJobRoles().then(setJobRoles).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (initialAnalysis) {
      setResult(initialAnalysis);
      window.setTimeout(
        () => document.getElementById("analysis-results")?.scrollIntoView({ block: "start" }),
        50,
      );
    }
  }, [initialAnalysis]);

  useEffect(() => {
    if (initialJobRole) {
      setRole(initialJobRole.title);
      setLevel(initialJobRole.level);
      setJobDescription(initialJobRole.description);
      setSkills(initialJobRole.requiredSkills);
    }
  }, [initialJobRole]);

  const selectedSavedRole = jobRoles.find((item) => item.title === role);
  const selectedRoleSkills = ROLE_SKILLS[role] ?? selectedSavedRole?.requiredSkills ?? [];

  const canAnalyze = Boolean(file && role && (jobDescription.trim().length >= 20 || skills.length));

  async function validateFile(candidate: File) {
    setError("");
    setResult(null);
    setRoleSuggestion(null);
    setResumeText("");
    if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
      setFile(null);
      setError("Unsupported file format. Please choose a PDF resume.");
      return;
    }
    if (!candidate.size) {
      setFile(null);
      setError("This file is empty. Please choose a valid PDF.");
      return;
    }
    if (candidate.size > MAX_PDF_SIZE) {
      setFile(null);
      setError("This PDF is larger than 10 MB. Please upload a smaller file.");
      return;
    }
    setFile(candidate);
    setIsReading(true);
    try {
      const text = await extractPdfText(candidate);
      const suggestion = inferTargetRole(text);
      setResumeText(text);
      setRoleSuggestion(suggestion);
      if (suggestion) {
        setRole(suggestion.role);
        setJobDescription(ROLE_DESCRIPTIONS[suggestion.role]);
      }
    } catch (readError) {
      setFile(null);
      setError(readError instanceof Error ? readError.message : "The PDF could not be read.");
    } finally {
      setIsReading(false);
    }
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const candidate = event.target.files?.[0];
    if (candidate) void validateFile(candidate);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const candidate = event.dataTransfer.files?.[0];
    if (candidate) void validateFile(candidate);
  }

  function addSkill() {
    const value = skillInput.trim();
    if (value && !skills.some((skill) => skill.toLowerCase() === value.toLowerCase())) {
      setSkills([...skills, value]);
    }
    setSkillInput("");
  }

  async function runAnalysis(event: FormEvent) {
    event.preventDefault();
    if (!file || !canAnalyze) return;
    setError("");
    setFeedback("");
    setIsAnalyzing(true);
    setResult(null);
    try {
      const text = resumeText || await extractPdfText(file);
      const analysis = analyzeResume({
        text,
        fileName: file.name,
        role,
        level,
        jobDescription,
        customSkills: skills,
      });
      setResult(analysis);
      window.setTimeout(() => document.getElementById("analysis-results")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch (analysisError) {
      setError(analysisError instanceof Error ? analysisError.message : "The resume could not be analyzed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function saveCurrentAnalysis() {
    if (!result) return;
    try {
      const saved = await saveAnalysis(result);
      setSavedAnalyses(await getSavedAnalyses());
      setFeedback(saved ? "Analysis saved to the local recruitment database." : "This analysis has already been saved.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "The analysis could not be saved.");
    }
  }

  function resetAnalyzer() {
    setFile(null);
    setRole("");
    setJobDescription("");
    setSkills([]);
    setSkillInput("");
    setResumeText("");
    setRoleSuggestion(null);
    setResult(null);
    setError("");
    setFeedback("");
    if (inputRef.current) inputRef.current.value = "";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <>
      <div className="analyzer-breadcrumb">
        <button type="button" onClick={onReturn}>Dashboard</button>
        <span>/</span>
        <b>Resume Analyzer</b>
      </div>

      <div className="mb-7 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <span className="rounded-md bg-[#e9f9f6] px-2 py-1 text-[9px] font-extrabold uppercase tracking-[0.12em] text-[#129783]">AI-powered</span>
          </div>
          <h1 className="text-[30px] font-extrabold tracking-[-0.045em] text-[#171c1a] sm:text-[34px]">Resume Analyzer</h1>
          <p className="mt-1 text-sm text-[#777c79]">Analyze resumes, identify skill gaps, and evaluate candidate suitability.</p>
        </div>
        <button type="button" onClick={() => setShowSaved(true)} className="secondary-action">
          View Saved Analyses <span className="saved-count">{savedAnalyses.length}</span>
        </button>
      </div>

      {error && <div className="analysis-alert error"><b>Unable to continue</b><span>{error}</span></div>}
      {feedback && <div className="analysis-alert success"><b>Success</b><span>{feedback}</span></div>}

      <form onSubmit={runAnalysis}>
        <section className="grid gap-5 xl:grid-cols-[1.02fr_0.98fr]">
          <article className="dashboard-card analyzer-card">
            <div className="card-heading">
              <div><h2>Upload candidate resume</h2><p>We process the file locally in your browser and do not upload it to an external AI service.</p></div>
              <span className="step-label">Step 1</span>
            </div>

            <div
              className={`pdf-dropzone ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
              onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
              onDragOver={(event) => event.preventDefault()}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
            >
              <input ref={inputRef} type="file" accept="application/pdf,.pdf" onChange={onFileChange} className="sr-only" aria-label="Upload resume PDF" />
              {file ? (
                <div className="selected-file">
                  <div className="pdf-file-icon">PDF</div>
                  <div className="min-w-0 flex-1">
                    <p>{file.name}</p>
                    <span>{(file.size / 1024 / 1024).toFixed(2)} MB · {isReading ? "Reading resume and identifying target role..." : "Ready to analyze"}</span>
                    <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[#dfece9]"><div className={`h-full rounded-full bg-[#14ad98] ${isReading ? "w-2/3 animate-pulse" : "w-full"}`} /></div>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => inputRef.current?.click()}>Replace</button>
                    <button type="button" className="remove" onClick={() => { setFile(null); setResult(null); setResumeText(""); setRoleSuggestion(null); if (inputRef.current) inputRef.current.value = ""; }}>Remove</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="upload-illustration"><UploadIcon /><span>PDF</span></div>
                  <h3>Drop your resume PDF here</h3>
                  <p>or choose a file from your computer</p>
                  <button type="button" onClick={() => inputRef.current?.click()} className="browse-button">Browse files</button>
                  <span className="upload-limit">PDF only · Maximum file size 10 MB</span>
                </>
              )}
            </div>

            <div className="upload-privacy">
              <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none"><path d="M7 10V8a5 5 0 0 1 10 0v2m-10 0h10a2 2 0 0 1 2 2v7H5v-7a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.8" /></svg>
              <span>Your resume is analyzed locally and is not stored unless you explicitly save the analysis.</span>
            </div>
            {roleSuggestion && (
              <div className="role-detection">
                <div className="role-detection-icon"><ResultIcon type="tip" /></div>
                <div>
                  <span>Likely target role detected</span>
                  <h3>{roleSuggestion.role}</h3>
                  <p>
                    The resume contains {roleSuggestion.detectedSkills.length} of {ROLE_SKILLS[roleSuggestion.role].length} core skills for this role. Review the suggestion before analyzing.
                  </p>
                </div>
                <b>{roleSuggestion.confidence}% evidence</b>
              </div>
            )}
          </article>

          <article className="dashboard-card analyzer-card">
            <div className="card-heading">
              <div><h2>Job requirements</h2><p>Define the role so the analysis can compare relevant evidence.</p></div>
              <span className="step-label">Step 2</span>
            </div>

            <div className="analysis-form-grid">
              <label className="analysis-field">
                <span>Target job role <b>*</b></span>
                <select
                  value={role}
                  onChange={(event) => {
                    const nextRole = event.target.value;
                    setRole(nextRole);
                    if (nextRole) {
                      const savedRole = jobRoles.find((item) => item.title === nextRole);
                      setJobDescription(ROLE_DESCRIPTIONS[nextRole] ?? savedRole?.description ?? "");
                      if (savedRole) {
                        setLevel(savedRole.level);
                        setSkills(savedRole.requiredSkills);
                      }
                    }
                  }}
                  required
                >
                  <option value="">Select a target role</option>
                  {Array.from(new Set([...Object.keys(ROLE_SKILLS), ...jobRoles.filter((item) => item.status !== "Closed").map((item) => item.title)])).map((option) => <option key={option}>{option}</option>)}
                </select>
              </label>
              <label className="analysis-field">
                <span>Experience level</span>
                <select value={level} onChange={(event) => setLevel(event.target.value)}>
                  {["Fresher", "Entry Level", "Intermediate", "Experienced"].map((option) => <option key={option}>{option}</option>)}
                </select>
              </label>
            </div>

            <label className="analysis-field mt-4">
              <span>Job description <small>Optional with required skills</small></span>
              <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} rows={5} placeholder="Paste the responsibilities, qualifications, and requirements for this role..." />
              <em>{jobDescription.length} characters</em>
            </label>

            <div className="analysis-field mt-4">
              <span>Required skills <small>Add at least one if no job description is provided</small></span>
              {role && (
                <div className="suggested-requirements">
                  <p>Suggested core requirements for {role}</p>
                  <div>
                    {selectedRoleSkills.map((skill) => (
                      <span
                        key={skill}
                        className={
                          roleSuggestion?.role === role && roleSuggestion.detectedSkills.includes(skill)
                            ? "found"
                            : roleSuggestion?.role === role && roleSuggestion.missingSkills.includes(skill)
                              ? "gap"
                              : ""
                        }
                      >
                        {roleSuggestion?.role === role && roleSuggestion.detectedSkills.includes(skill) ? "✓ " : roleSuggestion?.role === role && roleSuggestion.missingSkills.includes(skill) ? "– " : ""}
                        {skill}
                      </span>
                    ))}
                  </div>
                  {roleSuggestion && (
                    <small>
                      Checkmarks are supported by resume text. Dashes indicate skills the candidate may need to develop or demonstrate.
                    </small>
                  )}
                </div>
              )}
              <div className="skill-input-wrap">
                <input value={skillInput} onChange={(event) => setSkillInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); addSkill(); } }} placeholder="Type a skill and press Enter" />
                <button type="button" onClick={addSkill}>Add</button>
              </div>
              <div className="mt-2 flex min-h-7 flex-wrap gap-2">
                {skills.map((skill) => (
                  <span key={skill} className="editable-skill">{skill}<button type="button" aria-label={`Remove ${skill}`} onClick={() => setSkills(skills.filter((item) => item !== skill))}>×</button></span>
                ))}
              </div>
            </div>

            <div className="scoring-note">
              <ResultIcon type="tip" />
              <p><b>Transparent scoring:</b> 60% required skills, 25% job-description keywords, and 15% experience/project evidence.</p>
            </div>

            <button type="submit" disabled={!canAnalyze || isAnalyzing || isReading} className="analyze-button">
              {isAnalyzing ? <><span className="spinner" /> Extracting and analyzing...</> : <><UploadIcon /> Analyze resume</>}
            </button>
            {!canAnalyze && <p className="mt-2 text-center text-[9px] text-[#999e9a]">Add a PDF, target role, and either a job description or required skill.</p>}
          </article>
        </section>
      </form>

      {!result && !isAnalyzing && (
        <section className="analysis-empty-state">
          <div className="empty-bars"><span /><span /><span /></div>
          <div><h2>Your analysis will appear here</h2><p>Upload a readable PDF and define the target role to see match scoring, candidate details, skill gaps, and practical suggestions.</p></div>
        </section>
      )}

      {isAnalyzing && (
        <section className="analysis-loading">
          <div className="analysis-orbit"><span /></div>
          <div><h2>Analyzing resume evidence</h2><p>Extracting PDF text, normalizing skills, and comparing the resume with your requirements...</p></div>
        </section>
      )}

      {result && (
        <section id="analysis-results" className="analysis-results">
          <div className="results-heading">
            <div><span>Analysis complete</span><h2>Estimated Resume-to-Job Match</h2><p>This is a reproducible estimate, not an official score from an external ATS.</p></div>
            <div className="flex flex-wrap gap-2">
              <button type="button" className="secondary-action" onClick={saveCurrentAnalysis}>Save analysis</button>
              <button type="button" className="primary-action" onClick={() => downloadAnalysisReport(result)}>Download PDF report</button>
            </div>
          </div>

          <div className="grid gap-5 xl:grid-cols-[1.15fr_1.85fr]">
            <article className="dashboard-card score-overview">
              <div className="match-score">
                <svg viewBox="0 0 120 120" aria-label={`${result.score} percent match`}>
                  <circle cx="60" cy="60" r="49" className="score-ring-bg" />
                  <circle cx="60" cy="60" r="49" className="score-ring-value" strokeDasharray="308" strokeDashoffset={308 - (308 * result.score) / 100} />
                </svg>
                <div><strong>{result.score}%</strong><span>Match score</span></div>
              </div>
              <span className={`match-status ${result.status.toLowerCase().replace(" ", "-")}`}>{result.status}</span>
              <p className="score-caption">Compared with <b>{result.role}</b> requirements at the {result.level.toLowerCase()} level.</p>
              <div className="score-breakdown">
                <div><span>Skill coverage</span><b>{result.scoreBreakdown.skillCoverage}%</b></div>
                <div><span>Keyword relevance</span><b>{result.scoreBreakdown.keywordRelevance}%</b></div>
                <div><span>Evidence strength</span><b>{result.scoreBreakdown.evidence}%</b></div>
              </div>
            </article>

            <article className="dashboard-card candidate-information">
              <div className="card-heading"><div><h2>Candidate information</h2><p>Only information reliably found in the PDF is displayed.</p></div><span className="file-chip">{result.fileName}</span></div>
              <div className="candidate-info-grid">
                {[["Candidate name", result.candidate.name], ["Email address", result.candidate.email], ["Phone number", result.candidate.phone], ["Education", result.candidate.education.join("; ") || "Not found"]].map(([label, value]) => (
                  <div key={label}><span>{label}</span><p>{value}</p></div>
                ))}
              </div>
              <div className="candidate-detail-row"><span>Experience evidence</span><p>{result.candidate.experience.join(" · ") || "Not found"}</p></div>
              <div className="candidate-detail-row"><span>Projects & certifications</span><p>{[...result.candidate.projects, ...result.candidate.certifications].join(" · ") || "Not found"}</p></div>
            </article>
          </div>

          <div className="mt-5 grid gap-5 lg:grid-cols-3">
            <SkillsGroup type="matched" title="Matched skills" description="Required skills found in resume text" skills={result.matchedSkills} />
            <SkillsGroup type="missing" title="Missing skills" description="Required but not found in resume text" skills={result.missingSkills} />
            <SkillsGroup type="additional" title="Additional skills" description="Relevant skills beyond requirements" skills={result.additionalSkills} />
          </div>

          <article className="dashboard-card mt-5 improvement-card">
            <div className="card-heading"><div><h2>Resume improvement suggestions</h2><p>Practical recommendations based on the supplied resume and role requirements.</p></div></div>
            <div className="suggestions-grid">
              {result.suggestions.map((suggestion, index) => (
                <div key={suggestion}><span>{index + 1}</span><p>{suggestion}</p></div>
              ))}
            </div>
          </article>

          <div className="analysis-actions">
            <button type="button" className="secondary-action" onClick={resetAnalyzer}>Analyze another resume</button>
            <button type="button" className="secondary-action" onClick={onReturn}>Return to dashboard</button>
          </div>
        </section>
      )}

      {showSaved && (
        <div className="saved-overlay" role="dialog" aria-modal="true" aria-label="Saved analyses">
          <button type="button" className="saved-backdrop" onClick={() => setShowSaved(false)} aria-label="Close saved analyses" />
          <aside className="saved-panel">
            <div className="flex items-start justify-between">
              <div><h2>Saved analyses</h2><p>Stored securely in this browser.</p></div>
              <button type="button" className="panel-close" onClick={() => setShowSaved(false)}>×</button>
            </div>
            <div className="mt-6 space-y-3">
              {savedAnalyses.length ? savedAnalyses.map((saved) => (
                <article key={saved.id} className="saved-item">
                  <div className="flex items-center justify-between gap-3"><b>{saved.candidate.name}</b><span>{saved.score}%</span></div>
                  <p>{saved.role} · {saved.fileName}</p>
                  <time>{new Date(saved.createdAt).toLocaleString()}</time>
                  <div className="mt-3 flex gap-2">
                    <button type="button" onClick={() => { setResult(saved); setShowSaved(false); }}>Open</button>
                    <button type="button" className="delete" onClick={async () => { await deleteAnalysis(saved.id); setSavedAnalyses(await getSavedAnalyses()); }}>Delete</button>
                  </div>
                </article>
              )) : <div className="saved-empty"><UploadIcon /><h3>No saved analyses yet</h3><p>Completed analyses you save will appear here.</p></div>}
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
