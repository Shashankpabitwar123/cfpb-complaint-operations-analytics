import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const workbookPath = path.join(root, "tableau", "CFPB_Tableau_Source.xlsx");
const previewDirectory = path.join("/private/tmp", "cfpb-tableau-source-previews");
const previewSheets = [
  ["Read Me", "A1:B13"],
  ["Monthly Operations", "A1:L20"],
  ["Product Workload", "A1:H20"],
  ["Issue Workload", "A1:F20"],
  ["Response Performance by Product", "A1:I20"],
  ["Channel Mix", "A1:E15"],
  ["State Workload", "A1:H20"],
  ["Company Concentration", "A1:J20"],
  ["Quality Reconciliation", "A1:E10"],
  ["Monthly Volume", "A1:C20"],
  ["Product Summary", "A1:C20"],
  ["State Summary", "A1:B20"],
  ["Response Performance", "A1:G10"],
];

const adapterExpectations = {
  "Monthly Volume": ["month_start", "year", "complaint_count"],
  "Product Summary": ["product", "complaint_count", "share_pct"],
  "State Summary": ["state", "complaint_count"],
  "Response Performance": [
    "year",
    "complaint_count",
    "known_public_response_count",
    "response_coverage_pct",
    "timely_yes_count",
    "timely_known_count",
    "timely_response_rate_pct",
  ],
};

const input = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const inspection = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 4,
  tableMaxCols: 6,
  tableMaxCellChars: 70,
});
console.log(inspection.ndjson);

for (const [sheetName, expectedHeaders] of Object.entries(adapterExpectations)) {
  const headerRange = `A1:${String.fromCharCode(64 + expectedHeaders.length)}1`;
  const actualHeaders = workbook.worksheets.getItem(sheetName).getRange(headerRange).values[0];
  if (JSON.stringify(actualHeaders) !== JSON.stringify(expectedHeaders)) {
    throw new Error(`${sheetName} adapter schema mismatch: ${JSON.stringify(actualHeaders)}`);
  }
  console.log(`PASS adapter schema: ${sheetName}`);
}

await fs.mkdir(previewDirectory, { recursive: true });
for (const [sheetName, range] of previewSheets) {
  const preview = await workbook.render({
    sheetName,
    range,
    scale: 1,
    format: "png",
  });
  const previewPath = path.join(previewDirectory, `${sheetName.replaceAll(" ", "_")}.png`);
  await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
  console.log(`Rendered preview: ${previewPath}`);
}
