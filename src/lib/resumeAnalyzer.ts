export const ROLE_SKILLS: Record<string, string[]> = {
  "Data Analyst": ["SQL", "Excel", "Python", "Power BI", "Tableau", "Statistics", "Pandas"],
  "Data Scientist": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics", "Scikit-learn"],
  "Python Developer": ["Python", "Django", "Flask", "REST APIs", "Git", "SQL", "Testing"],
  "Machine Learning Engineer": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "MLOps", "Docker", "SQL"],
  "Software Developer": ["JavaScript", "TypeScript", "React", "Node.js", "Git", "REST APIs", "Testing"],
};

export const ROLE_DESCRIPTIONS: Record<string, string> = {
  "Data Analyst":
    "Analyze business data, build dashboards and reports, write SQL queries, and communicate actionable insights using statistical and visualization tools.",
  "Data Scientist":
    "Develop statistical and machine-learning solutions, prepare datasets, evaluate models, and communicate findings using Python and SQL.",
  "Python Developer":
    "Build reliable Python applications and APIs, work with databases, write automated tests, use version control, and maintain production-ready services.",
  "Machine Learning Engineer":
    "Build, evaluate, deploy, and monitor machine-learning systems using Python, modern ML frameworks, data pipelines, containers, and MLOps practices.",
  "Software Developer":
    "Design and build maintainable software applications, integrate APIs, collaborate through Git, test implementations, and work with modern web technologies.",
};

const SKILL_ALIASES: Record<string, string[]> = {
  "Power BI": ["power bi", "powerbi"],
  "Machine Learning": ["machine learning", "ml"],
  "Scikit-learn": ["scikit-learn", "sklearn"],
  "REST APIs": ["rest api", "restful api", "rest apis"],
  "Node.js": ["node.js", "nodejs"],
  "NumPy": ["numpy"],
  "Pandas": ["pandas"],
  "TensorFlow": ["tensorflow"],
  "PyTorch": ["pytorch"],
  "MLOps": ["mlops"],
};

export type CandidateInfo = {
  name: string;
  email: string;
  phone: string;
  education: string[];
  skills: string[];
  experience: string[];
  projects: string[];
  certifications: string[];
};

export type AnalysisResult = {
  id: string;
  candidateId?: string;
  jobRoleId?: string | null;
  createdAt: string;
  fileName: string;
  role: string;
  level: string;
  score: number;
  status: "Strong Match" | "Moderate Match" | "Low Match";
  recruitmentStatus?: "New" | "Shortlisted" | "Interview Scheduled" | "Rejected";
  matchedSkills: string[];
  missingSkills: string[];
  additionalSkills: string[];
  keywordMatches: string[];
  candidate: CandidateInfo;
  suggestions: string[];
  scoreBreakdown: {
    skillCoverage: number;
    keywordRelevance: number;
    evidence: number;
  };
};

function normalize(value: string) {
  return value.toLowerCase().replace(/[^\w+#.]+/g, " ").replace(/\s+/g, " ").trim();
}

function includesSkill(text: string, skill: string) {
  const aliases = SKILL_ALIASES[skill] ?? [skill.toLowerCase()];
  const normalized = normalize(text);
  return aliases.some((alias) => {
    const escaped = normalize(alias).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`(^|\\s)${escaped}(?=\\s|$)`, "i").test(normalized);
  });
}

export function inferTargetRole(text: string) {
  const ranked = Object.entries(ROLE_SKILLS)
    .map(([role, requiredSkills]) => {
      const detectedSkills = requiredSkills.filter((skill) => includesSkill(text, skill));
      return {
        role,
        detectedSkills,
        missingSkills: requiredSkills.filter((skill) => !detectedSkills.includes(skill)),
        confidence: Math.round((detectedSkills.length / requiredSkills.length) * 100),
      };
    })
    .sort(
      (a, b) =>
        b.detectedSkills.length - a.detectedSkills.length ||
        b.confidence - a.confidence,
    );

  return ranked[0]?.detectedSkills.length ? ranked[0] : null;
}

function unique(values: string[]) {
  return [...new Set(values.map((item) => item.trim()).filter(Boolean))];
}

function sectionLines(text: string, headings: string[]) {
  const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const start = lines.findIndex((line) => headings.some((heading) => normalize(line).includes(heading)));
  if (start < 0) return [];
  const result: string[] = [];
  for (let index = start + 1; index < Math.min(lines.length, start + 9); index += 1) {
    const line = lines[index];
    if (/^(education|experience|projects?|certifications?|skills|summary|objective)$/i.test(line)) break;
    result.push(line);
  }
  return result.slice(0, 5);
}

function extractCandidate(text: string, knownSkills: string[]): CandidateInfo {
  const rawLines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const email = text.match(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i)?.[0] ?? "Not found";
  const phone = text.match(/(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}/)?.[0] ?? "Not found";
  const possibleName =
    rawLines
      .slice(0, 5)
      .find((line) => {
        const words = line.split(/\s+/);
        return (
          words.length >= 2 &&
          words.length <= 4 &&
          line.length < 50 &&
          words.every((word) => /^[A-Z][A-Za-z'.-]+$/.test(word)) &&
          !/\b(resume|curriculum|vitae|profile|summary)\b/i.test(line)
        );
      }) ?? "";
  const name =
    possibleName.length > 2 &&
    possibleName.length < 50 &&
    !possibleName.includes("@") &&
    !/\d/.test(possibleName)
      ? possibleName
      : "Not found";

  const educationMatches = unique(
    text.match(/[^.!?]*(?:bachelor|master|b\.?sc|m\.?sc|university|college|degree)[^.!?]*/gi) ?? [],
  ).slice(0, 4);
  const certifications = unique(
    text.match(/[^.!?]*(?:certified|certification|certificate)[^.!?]*/gi) ?? [],
  ).slice(0, 4);

  return {
    name,
    email,
    phone,
    education: educationMatches,
    skills: knownSkills.filter((skill) => includesSkill(text, skill)),
    experience: sectionLines(text, ["experience", "employment", "work history"]),
    projects: sectionLines(text, ["projects", "project experience"]),
    certifications,
  };
}

function importantKeywords(description: string) {
  const stopWords = new Set([
    "and", "the", "with", "for", "that", "this", "from", "your", "you", "our", "are", "will",
    "have", "has", "role", "work", "team", "years", "using", "into", "who", "but", "not", "job",
  ]);
  const words = normalize(description).split(" ").filter((word) => word.length > 4 && !stopWords.has(word));
  const counts = words.reduce<Record<string, number>>((accumulator, word) => {
    accumulator[word] = (accumulator[word] ?? 0) + 1;
    return accumulator;
  }, {});
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([word]) => word);
}

export function analyzeResume(input: {
  text: string;
  fileName: string;
  role: string;
  level: string;
  jobDescription: string;
  customSkills: string[];
}): AnalysisResult {
  const requiredSkills = unique([...(ROLE_SKILLS[input.role] ?? []), ...input.customSkills]);
  const allKnownSkills = unique([...Object.values(ROLE_SKILLS).flat(), ...requiredSkills]);
  const matchedSkills = requiredSkills.filter((skill) => includesSkill(input.text, skill));
  const missingSkills = requiredSkills.filter((skill) => !includesSkill(input.text, skill));
  const additionalSkills = allKnownSkills.filter(
    (skill) => !requiredSkills.includes(skill) && includesSkill(input.text, skill),
  );

  const keywords = importantKeywords(input.jobDescription);
  const normalizedResume = normalize(input.text);
  const keywordMatches = keywords.filter((keyword) => normalizedResume.includes(keyword));
  const skillCoverage = requiredSkills.length ? matchedSkills.length / requiredSkills.length : 0;
  const keywordRelevance = keywords.length ? keywordMatches.length / keywords.length : skillCoverage;
  const hasExperience = /\b(experience|employment|worked|developed|managed|built|implemented)\b/i.test(input.text);
  const hasProjects = /\b(project|portfolio|case study|github)\b/i.test(input.text);
  const evidence = (hasExperience ? 0.6 : 0) + (hasProjects ? 0.4 : 0);
  const score = Math.round(skillCoverage * 60 + keywordRelevance * 25 + evidence * 15);
  const status = score >= 75 ? "Strong Match" : score >= 50 ? "Moderate Match" : "Low Match";
  const candidate = extractCandidate(input.text, allKnownSkills);

  const suggestions: string[] = [];
  if (missingSkills.length) {
    suggestions.push(`Address relevant skill gaps where truthful: ${missingSkills.slice(0, 4).join(", ")}.`);
  }
  if (keywords.length > keywordMatches.length) {
    const missingKeywords = keywords.filter((keyword) => !keywordMatches.includes(keyword)).slice(0, 4);
    suggestions.push(`Consider naturally reflecting applicable job-language such as ${missingKeywords.join(", ")}.`);
  }
  if (!hasProjects) {
    suggestions.push("Add a focused projects section with outcomes, tools used, and your specific contribution.");
  }
  if (!hasExperience) {
    suggestions.push("Make experience evidence easier to find with clear role headings and achievement-focused bullet points.");
  }
  if (input.text.length < 700) {
    suggestions.push("The resume appears brief; add measurable impact where it improves clarity without adding filler.");
  }
  suggestions.push("Use a simple single-column structure and standard section headings to support reliable parsing.");

  const signature = `${input.fileName}-${input.role}-${score}-${matchedSkills.join("-")}`;
  let hash = 0;
  for (let index = 0; index < signature.length; index += 1) hash = (hash * 31 + signature.charCodeAt(index)) | 0;

  return {
    id: `analysis-${Math.abs(hash)}`,
    createdAt: new Date().toISOString(),
    fileName: input.fileName,
    role: input.role,
    level: input.level,
    score,
    status,
    matchedSkills,
    missingSkills,
    additionalSkills,
    keywordMatches,
    candidate,
    suggestions,
    scoreBreakdown: {
      skillCoverage: Math.round(skillCoverage * 100),
      keywordRelevance: Math.round(keywordRelevance * 100),
      evidence: Math.round(evidence * 100),
    },
  };
}
