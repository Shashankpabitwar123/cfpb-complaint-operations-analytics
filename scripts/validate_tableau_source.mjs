import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const workbookPath = path.join(root, "tableau", "CFPB_Tableau_Source.xlsx");
const previewPath = path.join("/private/tmp", "cfpb-tableau-readme-preview.png");

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

const preview = await workbook.render({
  sheetName: "Read Me",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
console.log(`Rendered preview: ${previewPath}`);
