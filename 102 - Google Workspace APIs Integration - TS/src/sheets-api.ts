/**
 * Google Sheets API Functions - Implementation from document lines 1697-2280
 *
 * This module implements all Sheets API functions from Section 4 of the guide.
 */
import { sheets_v4 } from 'googleapis';

// ==================== CREATE SPREADSHEETS (Section 4.1) ====================

/**
 * Create a new Google Spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheet(
  sheetsService: sheets_v4.Sheets,
  title: string
): Promise<sheets_v4.Schema$Spreadsheet> {
  const spreadsheet: sheets_v4.Schema$Spreadsheet = {
    properties: {
      title,
    },
  };

  const response = await sheetsService.spreadsheets.create({
    requestBody: spreadsheet,
    fields: 'spreadsheetId,spreadsheetUrl',
  });

  return response.data;
}

/**
 * Create a spreadsheet with multiple named sheets.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @param sheetNames - List of sheet names
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheetWithSheets(
  sheetsService: sheets_v4.Sheets,
  title: string,
  sheetNames: string[]
): Promise<sheets_v4.Schema$Spreadsheet> {
  const sheets: sheets_v4.Schema$Sheet[] = sheetNames.map(name => ({
    properties: { title: name },
  }));

  const spreadsheet: sheets_v4.Schema$Spreadsheet = {
    properties: { title },
    sheets,
  };

  const response = await sheetsService.spreadsheets.create({
    requestBody: spreadsheet,
    fields: 'spreadsheetId,spreadsheetUrl,sheets.properties',
  });

  return response.data;
}

/**
 * Create a spreadsheet and populate it with data.
 *
 * @param sheetsService - Sheets API service instance
 * @param title - Spreadsheet title
 * @param data - 2D array of values
 * @param sheetName - Name of the sheet
 * @returns Created spreadsheet metadata
 */
export async function createSpreadsheetWithData(
  sheetsService: sheets_v4.Sheets,
  title: string,
  data: any[][],
  sheetName: string = 'Sheet1'
): Promise<sheets_v4.Schema$Spreadsheet> {
  // Create the spreadsheet
  const spreadsheet = await createSpreadsheet(sheetsService, title);
  const spreadsheetId = spreadsheet.spreadsheetId!;

  // Write the data
  await writeValues(sheetsService, spreadsheetId, `${sheetName}!A1`, data);

  return spreadsheet;
}

// ==================== READ DATA (Section 4.2) ====================

/**
 * Get spreadsheet metadata.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @returns Spreadsheet metadata
 */
export async function getSpreadsheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string
): Promise<sheets_v4.Schema$Spreadsheet> {
  const response = await sheetsService.spreadsheets.get({
    spreadsheetId,
  });

  return response.data;
}

/**
 * Read values from a spreadsheet range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range (e.g., 'Sheet1!A1:D10')
 * @returns 2D array of values
 */
export async function readValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string
): Promise<any[][]> {
  const response = await sheetsService.spreadsheets.values.get({
    spreadsheetId,
    range: rangeName,
  });

  return response.data.values || [];
}

/**
 * Read all values from a sheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetName - Name of the sheet
 * @returns 2D array of all values
 */
export async function readAllValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetName: string = 'Sheet1'
): Promise<any[][]> {
  return readValues(sheetsService, spreadsheetId, sheetName);
}

/**
 * Read multiple ranges at once.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param ranges - List of A1 notation ranges
 * @returns Dictionary mapping ranges to values
 */
export async function readMultipleRanges(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  ranges: string[]
): Promise<Record<string, any[][]>> {
  const response = await sheetsService.spreadsheets.values.batchGet({
    spreadsheetId,
    ranges,
  });

  const result: Record<string, any[][]> = {};
  for (const vr of response.data.valueRanges || []) {
    if (vr.range) {
      result[vr.range] = vr.values || [];
    }
  }

  return result;
}

export interface SheetSummary {
  sheetId: number;
  title: string;
  rowCount: number;
  columnCount: number;
}

export interface SpreadsheetSummary {
  title: string | null | undefined;
  spreadsheetId: string;
  url: string | null | undefined;
  sheets: SheetSummary[];
}

/**
 * Get a summary of the spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @returns Dictionary with spreadsheet summary
 */
export async function getSheetSummary(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string
): Promise<SpreadsheetSummary> {
  const spreadsheet = await getSpreadsheet(sheetsService, spreadsheetId);

  const summary: SpreadsheetSummary = {
    title: spreadsheet.properties?.title,
    spreadsheetId,
    url: spreadsheet.spreadsheetUrl,
    sheets: [],
  };

  for (const sheet of spreadsheet.sheets || []) {
    const props = sheet.properties;
    const gridProps = props?.gridProperties;

    summary.sheets.push({
      sheetId: props?.sheetId || 0,
      title: props?.title || '',
      rowCount: gridProps?.rowCount || 0,
      columnCount: gridProps?.columnCount || 0,
    });
  }

  return summary;
}

// ==================== UPDATE DATA (Section 4.3) ====================

/**
 * Write values to a spreadsheet range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range
 * @param values - 2D array of values
 * @returns Update result
 */
export async function writeValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string,
  values: any[][]
): Promise<sheets_v4.Schema$UpdateValuesResponse> {
  const response = await sheetsService.spreadsheets.values.update({
    spreadsheetId,
    range: rangeName,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values },
  });

  return response.data;
}

/**
 * Append values after the last row of data.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range (determines columns)
 * @param values - 2D array of values to append
 * @returns Append result
 */
export async function appendValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string,
  values: any[][]
): Promise<sheets_v4.Schema$AppendValuesResponse> {
  const response = await sheetsService.spreadsheets.values.append({
    spreadsheetId,
    range: rangeName,
    valueInputOption: 'USER_ENTERED',
    insertDataOption: 'INSERT_ROWS',
    requestBody: { values },
  });

  return response.data;
}

/**
 * Clear values from a range.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param rangeName - A1 notation range
 */
export async function clearValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  rangeName: string
): Promise<void> {
  await sheetsService.spreadsheets.values.clear({
    spreadsheetId,
    range: rangeName,
  });
}

/**
 * Update multiple ranges at once.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param data - Dictionary mapping ranges to values
 * @returns Update result
 */
export async function updateMultipleRanges(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  data: Record<string, any[][]>
): Promise<sheets_v4.Schema$BatchUpdateValuesResponse> {
  const valueRanges: sheets_v4.Schema$ValueRange[] = Object.entries(data).map(
    ([range, values]) => ({ range, values })
  );

  const response = await sheetsService.spreadsheets.values.batchUpdate({
    spreadsheetId,
    requestBody: {
      valueInputOption: 'USER_ENTERED',
      data: valueRanges,
    },
  });

  return response.data;
}

/**
 * Add a new sheet to a spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetName - Name for the new sheet
 * @returns New sheet properties
 */
export async function addSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetName: string
): Promise<sheets_v4.Schema$SheetProperties> {
  const requests: sheets_v4.Schema$Request[] = [
    {
      addSheet: {
        properties: {
          title: sheetName,
        },
      },
    },
  ];

  const response = await sheetsService.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });

  return response.data.replies![0].addSheet!.properties!;
}

/**
 * Delete a sheet from a spreadsheet.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param sheetId - ID of the sheet to delete
 */
export async function deleteSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  sheetId: number
): Promise<void> {
  const requests: sheets_v4.Schema$Request[] = [
    {
      deleteSheet: {
        sheetId,
      },
    },
  ];

  await sheetsService.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });
}

// ==================== SEARCH AND QUERY DATA (Section 4.4) ====================

export interface CellMatch {
  cell: string;
  row: number;
  column: number;
  value: any;
}

/**
 * Find cells containing specific text.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param searchText - Text to search for
 * @param sheetName - Sheet to search
 * @returns List of matches with cell references
 */
export async function findInSheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  searchText: string,
  sheetName: string = 'Sheet1'
): Promise<CellMatch[]> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  const matches: CellMatch[] = [];
  const searchLower = searchText.toLowerCase();

  for (let rowIdx = 0; rowIdx < values.length; rowIdx++) {
    const row = values[rowIdx];
    for (let colIdx = 0; colIdx < row.length; colIdx++) {
      const cell = row[colIdx];
      if (String(cell).toLowerCase().includes(searchLower)) {
        const colLetter = colIdx < 26
          ? String.fromCharCode('A'.charCodeAt(0) + colIdx)
          : String.fromCharCode('A'.charCodeAt(0) + Math.floor(colIdx / 26) - 1) +
            String.fromCharCode('A'.charCodeAt(0) + (colIdx % 26));

        matches.push({
          cell: `${colLetter}${rowIdx + 1}`,
          row: rowIdx + 1,
          column: colIdx + 1,
          value: cell,
        });
      }
    }
  }

  return matches;
}

/**
 * Query sheet data with column filters.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param columnFilters - Dict of {column_index: filter_value}
 * @param sheetName - Sheet to query
 * @returns Filtered rows
 */
export async function querySheet(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  columnFilters: Record<number, string>,
  sheetName: string = 'Sheet1'
): Promise<Record<string, any>[]> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  if (values.length === 0) {
    return [];
  }

  const headers = values[0] || [];
  const results: Record<string, any>[] = [];

  for (const row of values.slice(1)) {  // Skip header row
    let match = true;
    for (const [colIdx, filterValue] of Object.entries(columnFilters)) {
      const idx = parseInt(colIdx);
      if (idx >= row.length) {
        match = false;
        break;
      }
      if (!String(row[idx]).toLowerCase().includes(filterValue.toLowerCase())) {
        match = false;
        break;
      }
    }

    if (match) {
      const rowObj: Record<string, any> = {};
      headers.forEach((header, i) => {
        rowObj[header] = row[i];
      });
      results.push(rowObj);
    }
  }

  return results;
}

/**
 * Get all values from a specific column.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param column - Column letter (e.g., 'A') or index (0-based)
 * @param sheetName - Sheet name
 * @returns List of column values
 */
export async function getColumnValues(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  column: string | number,
  sheetName: string = 'Sheet1'
): Promise<any[]> {
  let colLetter: string;
  if (typeof column === 'number') {
    colLetter = String.fromCharCode('A'.charCodeAt(0) + column);
  } else {
    colLetter = column;
  }

  const rangeName = `${sheetName}!${colLetter}:${colLetter}`;
  const values = await readValues(sheetsService, spreadsheetId, rangeName);

  return values.map(row => row[0] || '');
}

/**
 * Find a row by a value in a specific column.
 *
 * @param sheetsService - Sheets API service instance
 * @param spreadsheetId - ID of the spreadsheet
 * @param column - Column to search
 * @param value - Value to find
 * @param sheetName - Sheet name
 * @returns Row data as dictionary (with headers) or null
 */
export async function findRowByValue(
  sheetsService: sheets_v4.Sheets,
  spreadsheetId: string,
  column: string | number,
  value: any,
  sheetName: string = 'Sheet1'
): Promise<Record<string, any> | null> {
  const values = await readAllValues(sheetsService, spreadsheetId, sheetName);

  if (values.length < 2) {
    return null;
  }

  const headers = values[0];

  let colIdx: number;
  if (typeof column === 'string') {
    colIdx = column.toUpperCase().charCodeAt(0) - 'A'.charCodeAt(0);
  } else {
    colIdx = column;
  }

  for (const row of values.slice(1)) {
    if (colIdx < row.length && String(row[colIdx]) === String(value)) {
      const rowObj: Record<string, any> = {};
      headers.forEach((header, i) => {
        rowObj[header] = row[i];
      });
      return rowObj;
    }
  }

  return null;
}
