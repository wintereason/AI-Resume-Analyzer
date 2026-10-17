import type { AnalysisResult } from "./resumeAnalyzer";
import { apiRequest } from "./api";

export const ANALYSES_CHANGED_EVENT = "talentflow-analyses-changed";

export async function getSavedAnalyses(): Promise<AnalysisResult[]> {
  const response = await apiRequest<{ data: AnalysisResult[] }>("/analyses?pageSize=100");
  return response.data;
}

export async function saveAnalysis(result: AnalysisResult) {
  await apiRequest("/analyses", { method: "POST", body: JSON.stringify(result) });
  window.dispatchEvent(new Event(ANALYSES_CHANGED_EVENT));
  return true;
}

export async function deleteAnalysis(id: string) {
  await apiRequest(`/analyses/${encodeURIComponent(id)}`, { method: "DELETE" });
  window.dispatchEvent(new Event(ANALYSES_CHANGED_EVENT));
}

export async function updateRecruitmentStatus(
  id: string,
  recruitmentStatus: NonNullable<AnalysisResult["recruitmentStatus"]>,
) {
  const response = await apiRequest<{ data: AnalysisResult }>(
    `/analyses/${encodeURIComponent(id)}/recruitment-status`,
    { method: "PATCH", body: JSON.stringify({ recruitmentStatus }) },
  );
  window.dispatchEvent(new Event(ANALYSES_CHANGED_EVENT));
  return response.data;
}
