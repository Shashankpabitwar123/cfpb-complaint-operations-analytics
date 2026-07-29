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
  ["Response Performance by Product", "mart_response_performance.csv"],
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
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return new Date(`${value}T00:00:00Z`);
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

function writeDataSheet(workbook, sheetName, rows) {
  const sheet = workbook.worksheets.add(sheetName);
  sheet.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;
  const used = sheet.getUsedRange();
  const lastColumn = columnName(rows[0].length);
  sheet.getRange(`A1:${lastColumn}1`).format = {
    fill: "#0B3A61",
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    wrapText: true,
  };
  for (let columnIndex = 0; columnIndex < rows[0].length; columnIndex += 1) {
    const header = String(rows[0][columnIndex]);
    const dataRange = sheet.getRangeByIndexes(1, columnIndex, Math.max(rows.length - 1, 1), 1);
    if (header.endsWith("_date") || header.endsWith("_start")) {
      dataRange.format.numberFormat = "yyyy-mm-dd";
    } else if (header.includes("_rate") || header.includes("_share") || header.includes("_pct")) {
      dataRange.format.numberFormat = "0.0%";
    } else if (header.includes("volume") || header.includes("count") || header.includes("change") || header.includes("difference")) {
      dataRange.format.numberFormat = "#,##0";
    }
  }
  used.format.autofitColumns();
  used.format.autofitRows();
  if (sheetName === "Response Performance") {
    // The retained Tableau view displays percent points (for example, 99.6), not decimal percentages.
    sheet.getRange(`D2:D${rows.length}`).format.numberFormat = "0.0";
    sheet.getRange(`G2:G${rows.length}`).format.numberFormat = "0.0";
    sheet.getRange("A:G").format.columnWidth = 24;
    sheet.getRange("A1:G1").format.rowHeight = 30;
  }
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  return sheet;
}

function recordsFromRows(rows) {
  const [headers, ...data] = rows;
  return data.map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index]])));
}

function numberOrZero(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function monthLabel(value) {
  if (value instanceof Date) return value.toISOString().slice(0, 7);
  return String(value).slice(0, 7);
}

const stateNames = {
  AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California", CO: "Colorado",
  CT: "Connecticut", DE: "Delaware", DC: "District of Columbia", FL: "Florida", GA: "Georgia",
  HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky",
  LA: "Louisiana", ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota",
  MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada", NH: "New Hampshire",
  NJ: "New Jersey", NM: "New Mexico", NY: "New York", NC: "North Carolina", ND: "North Dakota",
  OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina",
  SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia",
  WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming", PR: "Puerto Rico",
  GU: "Guam", VI: "U.S. Virgin Islands", AS: "American Samoa", MP: "Northern Mariana Islands",
};

function buildLegacyAdapters(martRowsByFile) {
  const monthly = recordsFromRows(martRowsByFile.get("mart_monthly_operations.csv"));
  const product = recordsFromRows(martRowsByFile.get("mart_product_workload.csv"));
  const state = recordsFromRows(martRowsByFile.get("mart_state_workload.csv"));
  const response = recordsFromRows(martRowsByFile.get("mart_response_performance.csv"));

  const monthlyRows = [["month_start", "year", "complaint_count"], ...monthly
    .map((row) => [monthLabel(row.month_start), numberOrZero(row.received_year), numberOrZero(row.complaint_volume)])
    .sort((left, right) => left[0].localeCompare(right[0]))];

  const productTotals = new Map();
  for (const row of product) {
    const key = String(row.product);
    productTotals.set(key, (productTotals.get(key) ?? 0) + numberOrZero(row.complaint_volume));
  }
  const allProductVolume = [...productTotals.values()].reduce((sum, value) => sum + value, 0);
  const productRows = [["product", "complaint_count", "share_pct"], ...[...productTotals.entries()]
    .sort((left, right) => right[1] - left[1])
    .map(([name, volume]) => [name, volume, allProductVolume ? volume / allProductVolume : null])];

  const stateTotals = new Map();
  for (const row of state) {
    const code = String(row.state_code ?? "").trim().toUpperCase();
    const name = stateNames[code] ?? (code || "Unknown");
    stateTotals.set(name, (stateTotals.get(name) ?? 0) + numberOrZero(row.complaint_volume));
  }
  const stateRows = [["state", "complaint_count"], ...[...stateTotals.entries()]
    .sort((left, right) => right[1] - left[1])
    .map(([name, volume]) => [name, volume])];

  const responseTotals = new Map();
  for (const row of response) {
    const year = numberOrZero(row.received_year);
    const current = responseTotals.get(year) ?? {
      complaintCount: 0,
      knownResponseCount: 0,
      timelyYesCount: 0,
      timelyKnownCount: 0,
    };
    current.complaintCount += numberOrZero(row.complaint_volume);
    current.knownResponseCount += numberOrZero(row.company_response_count);
    current.timelyYesCount += numberOrZero(row.timely_response_count);
    current.timelyKnownCount += numberOrZero(row.timely_response_denominator);
    responseTotals.set(year, current);
  }
  const responseRows = [[
    "year",
    "complaint_count",
    "known_public_response_count",
    "response_coverage_pct",
    "timely_yes_count",
    "timely_known_count",
    "timely_response_rate_pct",
  ], ...[...responseTotals.entries()]
    .sort((left, right) => left[0] - right[0])
    .map(([year, totals]) => [
      year,
      totals.complaintCount,
      totals.knownResponseCount,
      totals.complaintCount ? (totals.knownResponseCount / totals.complaintCount) * 100 : null,
      totals.timelyYesCount,
      totals.timelyKnownCount,
      totals.timelyKnownCount ? (totals.timelyYesCount / totals.timelyKnownCount) * 100 : null,
    ])];

  return [
    ["Monthly Volume", monthlyRows],
    ["Product Summary", productRows],
    ["State Summary", stateRows],
    ["Response Performance", responseRows],
  ];
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
readme.getRange("A3:B10").values = [
  ["Analysis period", "2023-01-01 to 2025-12-31"],
  ["Record grain", "One published CFPB complaint per Complaint ID"],
  ["Scope", "9,363,711 validated complaint records"],
  ["Privacy", "Consumer complaint narratives are excluded"],
  ["Source", "CFPB Consumer Complaint Database"],
  ["Data mode", sourceMode],
  ["Use", "Connect Tableau to these aggregate sheets. Tableau Public uses this extract snapshot, not a live Snowflake connection."],
  ["Compatibility", hasSnowflakeMarts ? "Legacy-named adapter sheets preserve the original dashboard's four connections; Snowflake dbt mart sheets remain the source of truth." : "Not applicable in legacy fallback mode."],
];
readme.getRange("A11:B13").values = [["Important note", "The two credit-reporting product labels are kept separate because source taxonomy labels differ. Do not combine them without a documented mapping."], [null, null], ["Dashboard build", "Use the Tableau build specification in docs/tableau_build_spec.md. Keep a single dashboard with documented global filters and actions."]];
readme.getRange("A1:B1").format = { fill: "#0B3A61", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
readme.getRange("A1:B1").format.rowHeight = 30;
readme.getRange("A3:A10").format = { fill: "#E8F1F8", font: { bold: true, color: "#0B3A61" } };
readme.getRange("A3:B10").format.borders = { preset: "outside", style: "thin", color: "#B8C7D1" };
readme.getRange("A11:B11").format = { fill: "#FFF4D6", font: { bold: true, color: "#6B4E00" }, wrapText: true };
readme.getRange("A13:B13").format = { fill: "#E8F1F8", wrapText: true };
readme.getRange("A:A").format.columnWidth = 23;
readme.getRange("B:B").format.columnWidth = 62;
readme.showGridLines = false;
console.log("formatted readme");

const sourceRowsByFile = new Map();
for (const [sheetName, filename] of sources) {
  console.log(`importing ${sheetName}`);
  const csvText = await fs.readFile(path.join(sourceDirectory, filename), "utf8");
  const rows = parseCsv(csvText);
  sourceRowsByFile.set(filename, rows);
  writeDataSheet(workbook, sheetName, rows);
}

if (hasSnowflakeMarts) {
  for (const [sheetName, rows] of buildLegacyAdapters(sourceRowsByFile)) {
    console.log(`adding compatibility adapter ${sheetName}`);
    writeDataSheet(workbook, sheetName, rows);
  }
}

await fs.mkdir(path.dirname(outputPath), { recursive: true });
console.log("exporting workbook");
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
