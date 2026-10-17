import { jsPDF } from "jspdf";
import type { AnalysisResult } from "./resumeAnalyzer";

export function downloadAnalysisReport(result: AnalysisResult) {
  const pdf = new jsPDF({ unit: "pt", format: "a4" });
  const margin = 48;
  let y = 54;

  const line = (text: string, size = 10, bold = false, gap = 17) => {
    pdf.setFont("helvetica", bold ? "bold" : "normal");
    pdf.setFontSize(size);
    const lines = pdf.splitTextToSize(text, 500);
    pdf.text(lines, margin, y);
    y += lines.length * gap;
    if (y > 780) {
      pdf.addPage();
      y = 54;
    }
  };

  pdf.setTextColor(20, 157, 140);
  line("TALENTFLOW AI", 11, true, 18);
  pdf.setTextColor(31, 36, 33);
  line("Resume Analysis Report", 22, true, 27);
  line(`Estimated Resume-to-Job Match: ${result.score}% — ${result.status}`, 13, true, 23);
  line(`Target role: ${result.role} | Experience level: ${result.level}`);
  line(`Resume: ${result.fileName} | Generated: ${new Date(result.createdAt).toLocaleString()}`);

  y += 8;
  line("Candidate Information", 14, true, 22);
  line(`Name: ${result.candidate.name}`);
  line(`Email: ${result.candidate.email}`);
  line(`Phone: ${result.candidate.phone}`);
  line(`Education: ${result.candidate.education.join("; ") || "Not found"}`);

  y += 8;
  line("Skills Analysis", 14, true, 22);
  line(`Matched skills: ${result.matchedSkills.join(", ") || "None identified"}`);
  line(`Missing skills: ${result.missingSkills.join(", ") || "None identified"}`);
  line(`Additional skills: ${result.additionalSkills.join(", ") || "None identified"}`);

  y += 8;
  line("Scoring Method", 14, true, 22);
  line(
    `Required-skill coverage (60%): ${result.scoreBreakdown.skillCoverage}% | Job-description keywords (25%): ${result.scoreBreakdown.keywordRelevance}% | Experience/project evidence (15%): ${result.scoreBreakdown.evidence}%`,
  );

  y += 8;
  line("Improvement Suggestions", 14, true, 22);
  result.suggestions.forEach((suggestion, index) => line(`${index + 1}. ${suggestion}`));

  y += 8;
  pdf.setTextColor(105, 110, 107);
  line(
    "This is an estimated match produced from the supplied resume and requirements. It is not an official ATS score and does not guarantee selection.",
    8,
  );

  pdf.save(`${result.candidate.name === "Not found" ? "candidate" : result.candidate.name.replace(/\s+/g, "-").toLowerCase()}-analysis.pdf`);
}
