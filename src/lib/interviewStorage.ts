import { apiRequest } from "./api";

export const INTERVIEWS_CHANGED_EVENT = "talentflow-interviews-changed";

export type InterviewStatus = "Scheduled" | "Completed" | "Rescheduled" | "Cancelled";
export type InterviewType = "Online" | "In-person" | "Phone";
export type InterviewHistory = {
  at: string;
  action: string;
  previousDate?: string;
  previousStartTime?: string;
  previousEndTime?: string;
};
export type Interview = {
  id: string;
  candidateId: string;
  candidateName: string;
  candidateEmail: string;
  candidatePhone: string;
  jobRoleId: string;
  jobRoleTitle: string;
  date: string;
  startTime: string;
  endTime: string;
  type: InterviewType;
  interviewerName: string;
  interviewerEmail: string;
  meetingLink: string;
  location: string;
  notes: string;
  preparation: string;
  feedback: string;
  status: InterviewStatus;
  history: InterviewHistory[];
  createdAt: string;
  updatedAt: string;
};

export async function getInterviews(): Promise<Interview[]> {
  const response = await apiRequest<{ data: Interview[] }>("/interviews?pageSize=100");
  return response.data;
}

export async function saveInterview(interview: Interview) {
  const isServerId = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(interview.id);
  await apiRequest(isServerId ? `/interviews/${interview.id}` : "/interviews", {
    method: isServerId ? "PUT" : "POST",
    body: JSON.stringify(interview),
  });
  window.dispatchEvent(new Event(INTERVIEWS_CHANGED_EVENT));
}
