import { apiRequest } from "./api";

export const JOB_ROLES_CHANGED_EVENT = "talentflow-job-roles-changed";

export type JobRoleStatus = "Active" | "Draft" | "Closed";
export type EmploymentType = "Full-time" | "Part-time" | "Internship" | "Contract";
export type WorkMode = "Remote" | "Hybrid" | "On-site";

export type JobRole = {
  id: string;
  title: string;
  department: string;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  level: "Fresher" | "Entry Level" | "Intermediate" | "Experienced";
  minExperience: number;
  maxExperience?: number;
  education: string;
  employmentType: EmploymentType;
  location: string;
  workMode: WorkMode;
  salary: string;
  status: JobRoleStatus;
  createdAt: string;
  updatedAt: string;
};

export async function getJobRoles(): Promise<JobRole[]> {
  const response = await apiRequest<{ data: JobRole[] }>("/job-roles?pageSize=100");
  return response.data;
}

export async function saveJobRole(role: JobRole) {
  const isServerId = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(role.id);
  await apiRequest(isServerId ? `/job-roles/${role.id}` : "/job-roles", {
    method: isServerId ? "PUT" : "POST",
    body: JSON.stringify(role),
  });
  window.dispatchEvent(new Event(JOB_ROLES_CHANGED_EVENT));
}

export async function deleteJobRole(id: string) {
  await apiRequest(`/job-roles/${id}`, { method: "DELETE" });
  window.dispatchEvent(new Event(JOB_ROLES_CHANGED_EVENT));
}
