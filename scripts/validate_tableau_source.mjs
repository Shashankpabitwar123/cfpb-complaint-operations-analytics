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
  ["Response Performance", "A1:I20"],
  ["Channel Mix", "A1:E15"],
  ["State Workload", "A1:H20"],
  ["Company Concentration", "A1:J20"],
  ["Quality Reconciliation", "A1:E10"],
];

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
