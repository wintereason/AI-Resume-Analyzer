import { apiRequest } from "./api";
import type { AnalysisResult } from "./resumeAnalyzer";
import type { Interview } from "./interviewStorage";
import type { JobRole } from "./jobRoleStorage";

const MIGRATION_KEY = "talentflow-supabase-migration-v1";
const DATABASE_NAME = "talentflow-recruitment";
const DATABASE_VERSION = 3;

function legacyCandidateKey(item: AnalysisResult) {
  if (item.candidate.email !== "Not found") return item.candidate.email.toLowerCase();
  if (item.candidate.phone !== "Not found") return item.candidate.phone.replace(/\D/g, "");
  return `${item.fileName}:${item.candidate.name}`;
}

async function readStore<T>(storeName: string): Promise<T[]> {
  return new Promise((resolve) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => undefined;
    request.onerror = () => resolve([]);
    request.onsuccess = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(storeName)) {
        database.close();
        resolve([]);
        return;
      }
      const read = database.transaction(storeName, "readonly").objectStore(storeName).getAll();
      read.onsuccess = () => {
        resolve(read.result as T[]);
        database.close();
      };
      read.onerror = () => {
        resolve([]);
        database.close();
      };
    };
  });
}

export async function migrateIndexedDbToSupabase() {
  if (localStorage.getItem(MIGRATION_KEY)) return { migrated: false, roles: 0, analyses: 0, interviews: 0 };

  const [legacyRoles, legacyAnalyses, legacyInterviews] = await Promise.all([
    readStore<JobRole>("job-roles"),
    readStore<AnalysisResult>("resume-analyses"),
    readStore<Interview>("interviews"),
  ]);

  const currentRoles = await apiRequest<{ data: JobRole[] }>("/job-roles?pageSize=100");
  const rolesByTitle = new Map(currentRoles.data.map((role) => [role.title.toLowerCase(), role]));
  let migratedRoles = 0;

  for (const role of legacyRoles) {
    if (rolesByTitle.has(role.title.toLowerCase())) continue;
    const response = await apiRequest<{ data: JobRole }>("/job-roles", {
      method: "POST",
      body: JSON.stringify(role),
    });
    rolesByTitle.set(response.data.title.toLowerCase(), response.data);
    migratedRoles += 1;
  }

  let migratedAnalyses = 0;
  for (const analysis of legacyAnalyses) {
    const role = rolesByTitle.get(analysis.role.toLowerCase());
    await apiRequest("/analyses", {
      method: "POST",
      body: JSON.stringify({ ...analysis, jobRoleId: role?.id ?? null }),
    });
    migratedAnalyses += 1;
  }

  const serverAnalyses = await apiRequest<{ data: AnalysisResult[] }>("/analyses?pageSize=100");
  const candidateIds = new Map(
    serverAnalyses.data
      .filter((analysis) => analysis.candidateId)
      .map((analysis) => [legacyCandidateKey(analysis), analysis.candidateId as string]),
  );
  let migratedInterviews = 0;

  for (const interview of legacyInterviews) {
    const candidateId =
      candidateIds.get(interview.candidateId) ??
      serverAnalyses.data.find(
        (analysis) =>
          analysis.candidate.email !== "Not found" &&
          analysis.candidate.email.toLowerCase() === interview.candidateEmail.toLowerCase(),
      )?.candidateId;
    if (!candidateId) continue;
    const role = rolesByTitle.get(interview.jobRoleTitle.toLowerCase());
    await apiRequest("/interviews", {
      method: "POST",
      body: JSON.stringify({
        ...interview,
        candidateId,
        jobRoleId: role?.id ?? null,
      }),
    });
    migratedInterviews += 1;
  }

  localStorage.setItem(
    MIGRATION_KEY,
    JSON.stringify({
      completedAt: new Date().toISOString(),
      roles: migratedRoles,
      analyses: migratedAnalyses,
      interviews: migratedInterviews,
    }),
  );
  window.dispatchEvent(new Event("talentflow-job-roles-changed"));
  window.dispatchEvent(new Event("talentflow-analyses-changed"));
  window.dispatchEvent(new Event("talentflow-interviews-changed"));
  return {
    migrated: true,
    roles: migratedRoles,
    analyses: migratedAnalyses,
    interviews: migratedInterviews,
  };
}
