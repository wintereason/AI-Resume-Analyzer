import * as pdfjs from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

pdfjs.GlobalWorkerOptions.workerSrc = pdfWorker;

export const MAX_PDF_SIZE = 10 * 1024 * 1024;

export async function extractPdfText(file: File) {
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    throw new Error("Only PDF files are supported.");
  }
  if (!file.size) throw new Error("This PDF is empty.");
  if (file.size > MAX_PDF_SIZE) throw new Error("The PDF exceeds the 10 MB size limit.");

  try {
    const data = new Uint8Array(await file.arrayBuffer());
    const document = await pdfjs.getDocument({ data }).promise;
    const pages: string[] = [];
    for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
      const page = await document.getPage(pageNumber);
      const content = await page.getTextContent();
      pages.push(
        content.items
          .map((item) => ("str" in item ? `${item.str}${item.hasEOL ? "\n" : " "}` : ""))
          .join(""),
      );
    }
    const text = pages.join("\n").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
    if (text.length < 40) {
      throw new Error("No readable text was found. The PDF may be scanned or image-only.");
    }
    return text;
  } catch (error) {
    if (error instanceof Error && error.message.includes("readable text")) throw error;
    throw new Error("This PDF could not be read. It may be damaged, encrypted, or malformed.");
  }
}
