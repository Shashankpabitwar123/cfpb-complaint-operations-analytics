import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const summaryDir = path.join(root, "data", "processed", "summary");
const exportDir = path.join(root, "data", "exports", "tableau");
const outputPath = path.join(root, "tableau", "CFPB_Tableau_Source.xlsx");

const legacySources = [
  ["Monthly Volume", "monthly_volume.csv"],
  ["Product Summary", "product_summary.csv"],
  ["Issue Summary", "issue_summary.csv"],
  ["Response Performance", "response_performance.csv"],
  ["Channel Mix", "channel_mix.csv"],
  ["State Summary", "state_summary.csv"],
];

const snowflakeMartSources = [
  ["Monthly Operations", "mart_monthly_operations.csv"],
  ["Product Workload", "mart_product_workload.csv"],
  ["Issue Workload", "mart_issue_workload.csv"],
  ["Response Performance", "mart_response_performance.csv"],
  ["Channel Mix", "mart_channel_mix.csv"],
  ["State Workload", "mart_state_workload.csv"],
  ["Company Concentration", "mart_company_concentration.csv"],
  ["Quality Reconciliation", "mart_data_quality_reconciliation.csv"],
];

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];
    if (char === '"' && quoted && next === '"') {
      field += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === ',' && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && next === '\n') i += 1;
      row.push(field);
      if (row.length > 1 || row[0] !== "") rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.map((r, rowIndex) => r.map((value) => {
    if (rowIndex === 0 || value === "") return value;
    return /^-?\d+(\.\d+)?$/.test(value) ? Number(value) : value;
  }));
}

function columnName(index) {
  let n = index;
  let name = "";
  while (n > 0) {
    const remainder = (n - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

const workbook = Workbook.create();
console.log("created workbook");
const readme = workbook.worksheets.add("Read Me");
console.log("added readme");
const hasSnowflakeMarts = (await Promise.all(
  snowflakeMartSources.map(([, filename]) => fileExists(path.join(exportDir, filename))),
)).every(Boolean);
const sources = hasSnowflakeMarts ? snowflakeMartSources : legacySources;
const sourceDirectory = hasSnowflakeMarts ? exportDir : summaryDir;
const sourceMode = hasSnowflakeMarts
  ? "Snowflake dbt mart extract snapshot"
  : "Legacy local-summary fallback — run the Snowflake/dbt pipeline before final Tableau publication";

readme.getRange("A1:B1").merge();
readme.getRange("A1").values = [["CFPB Complaint Operations Analytics — Tableau Source"]];
readme.getRange("A3:B9").values = [
  ["Analysis period", "2023-01-01 to 2025-12-31"],
  ["Record grain", "One published CFPB complaint per Complaint ID"],
  ["Scope", "9,363,711 validated complaint records"],
  ["Privacy", "Consumer complaint narratives are excluded"],
  ["Source", "CFPB Consumer Complaint Database"],
  ["Data mode", sourceMode],
  ["Use", "Connect Tableau to these aggregate sheets. Tableau Public uses this extract snapshot, not a live Snowflake connection."],
];
readme.getRange("A11:B13").values = [["Important note", "The two credit-reporting product labels are kept separate because source taxonomy labels differ. Do not combine them without a documented mapping."], [null, null], ["Dashboard build", "Use the Tableau build specification in docs/tableau_build_spec.md. Keep a single dashboard with documented global filters and actions."]];
readme.getRange("A1:B1").format = { fill: "#0B3A61", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
readme.getRange("A1:B1").format.rowHeight = 30;
readme.getRange("A3:A9").format = { fill: "#E8F1F8", font: { bold: true, color: "#0B3A61" } };
readme.getRange("A3:B9").format.borders = { preset: "outside", style: "thin", color: "#B8C7D1" };
readme.getRange("A11:B11").format = { fill: "#FFF4D6", font: { bold: true, color: "#6B4E00" }, wrapText: true };
readme.getRange("A13:B13").format = { fill: "#E8F1F8", wrapText: true };
readme.getRange("A:A").format.columnWidth = 23;
readme.getRange("B:B").format.columnWidth = 62;
readme.showGridLines = false;
console.log("formatted readme");

for (const [sheetName, filename] of sources) {
  console.log(`importing ${sheetName}`);
  const csvText = await fs.readFile(path.join(sourceDirectory, filename), "utf8");
  const rows = parseCsv(csvText);
  const sheet = workbook.worksheets.add(sheetName);
  sheet.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;
  const used = sheet.getUsedRange();
  const lastColumn = columnName(rows[0].length);
  sheet.getRange(`A1:${lastColumn}1`).format = { fill: "#0B3A61", font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
  used.format.autofitColumns();
  used.format.autofitRows();
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}

await fs.mkdir(path.dirname(outputPath), { recursive: true });
console.log("exporting workbook");
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
