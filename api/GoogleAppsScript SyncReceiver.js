/**
 * Multi-State Google Apps Script Webhook Receiver (States 689-704).
 * Routes incoming payloads to payload.spreadsheet_id via SpreadsheetApp.openById
 * rather than writing only to the container-bound active spreadsheet.
 */

const SECRET_SYNC_TOKEN = "LASTZ_STATE694_MIGRATION_SECURE_KEY";

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ status: "error", message: "No post data received" }, 400);
    }

    const payload = JSON.parse(e.postData.contents);
    if (payload.token !== SECRET_SYNC_TOKEN) {
      return jsonResponse({ status: "error", message: "Unauthorized: Invalid secret token" }, 403);
    }

    const stateId = payload.state_id || 694;
    const ss = payload.spreadsheet_id
      ? SpreadsheetApp.openById(payload.spreadsheet_id)
      : SpreadsheetApp.getActiveSpreadsheet();

    const alliances = payload.alliances || [];
    const timestampUtc = payload.timestamp || new Date().toISOString();
    if (alliances.length === 0) {
      return jsonResponse({ status: "error", message: "No alliances payload provided" }, 400);
    }

    for (let i = 0; i < alliances.length; i++) {
      updateAllianceSheet(ss, alliances[i], stateId);
    }
    updateOverviewSheet(ss, alliances, timestampUtc, stateId);

    return jsonResponse({
      status: "success",
      message: "State " + stateId + " Migration data updated successfully",
      state_id: stateId,
      spreadsheet_id: ss.getId(),
      updated_alliances: alliances.length,
      timestamp: timestampUtc
    }, 200);
  } catch (err) {
    return jsonResponse({ status: "error", message: err.toString(), stack: err.stack }, 500);
  }
}

function doGet(e) {
  return jsonResponse({
    status: "online",
    service: "Last Z Multi-State Migration Webhook (Grouping 689-704)",
    timestamp: new Date().toISOString()
  }, 200);
}

function updateAllianceSheet(ss, alliance, stateId) {
  const abbr = (alliance.abbr || "").replace(/[\[\]]/g, "").trim();
  const name = (alliance.name || "").replace(/[\[\]\:\/\?\*\\]/g, "").trim();
  const sheetTitle = (abbr + " - " + name).substring(0, 31).trim();

  let ws = ss.getSheetByName(sheetTitle);
  if (!ws) {
    const sheets = ss.getSheets();
    for (let s of sheets) {
      if (s.getName().startsWith(abbr + " -") || s.getName() === abbr) {
        ws = s;
        break;
      }
    }
  }
  if (!ws) return;

  const members = alliance.members || [];
  if (members.length === 0) return;

  members.sort((a, b) => (b.authoritative_migrate_power || 0) - (a.authoritative_migrate_power || 0));

  const rows = [];
  for (let idx = 0; idx < members.length; idx++) {
    const m = members[idx];
    const roleMap = { 1: "R1", 2: "R2", 3: "R3", 4: "R4", 5: "Leader (R5)" };
    const role = roleMap[m.rank] || ("R" + (m.rank || 1));
    rows.push([
      idx + 1,
      role,
      m.mainBuildingLevel || m.mainCityLv || 0,
      m.name || "Unknown",
      "'" + String(m.uid || ""),
      m.authoritative_migrate_power || 0,
      m.tier || "Unknown",
      m.passes_required || 0,
      m.total_power || m.power || 0,
      m.player_max_power || m.playerMaxPower || 0,
      m.building_power || m.buildingPower || 0,
      m.science_power || m.sciencePower || 0,
      m.hero_power || m.heroPower || 0,
      m.tank_power || m.tankPower || 0,
      m.army_power || m.armyPower || 0,
      "100% IN-GAME VERIFIED"
    ]);
  }

  ws.getRange(6, 1, rows.length, 16).setValues(rows);
  ws.getRange("A1").setValue("[" + abbr + "] " + name + " (State " + stateId + ")");

  const dist = alliance.tier_distribution || {};
  const cElite = dist["Elite (Che4)"] || 0;
  const cAdv = dist["Advanced (Che3)"] || 0;
  const cMid = dist["Intermediate (Che2)"] || 0;
  const cReg = dist["Regular (Che1)"] || 0;

  ws.getRange("A3").setValue("Total Members: " + members.length);
  ws.getRange("D3").setValue("Total Passes: " + formatNumber(alliance.total_passes_required) + " Passes (Members: " + members.length + ")");
  ws.getRange("J3").setValue("Tier Breakdown: Elite (>100M): " + cElite + " | Advanced (40-100M): " + cAdv + " | Intermediate (20-40M): " + cMid + " | Regular (<=20M): " + cReg);
}

function updateOverviewSheet(ss, alliances, timestampUtc, stateId) {
  let ws = ss.getSheetByName("State " + stateId + " Overview");
  if (!ws) {
    ws = ss.getSheets()[0];
  }
  if (!ws) return;

  ws.getRange("A1").setValue("State " + stateId + " Top 10 Alliances - Grouping 689-704");
  const dateStr = Utilities.formatDate(new Date(), "UTC", "yyyy-MM-dd HH:mm:ss") + " UTC";
  ws.getRange("A2").setValue("Official In-Game Verified Migration Scores | Group 200162 | Synced: " + dateStr);

  alliances.sort((a, b) => a.rank - b.rank);

  let totalStatePower = 0;
  let totalStateMembers = 0;
  let totalStatePasses = 0;
  let totalElite = 0;
  let totalAdv = 0;
  let totalMid = 0;
  let totalReg = 0;

  const tableRows = [];
  for (let i = 0; i < alliances.length; i++) {
    const a = alliances[i];
    const m = a.members || [];
    const dist = a.tier_distribution || {};

    const e = dist["Elite (Che4)"] || 0;
    const adv = dist["Advanced (Che3)"] || 0;
    const mid = dist["Intermediate (Che2)"] || 0;
    const reg = dist["Regular (Che1)"] || 0;

    totalStatePower += a.total_fightpower || 0;
    totalStateMembers += m.length;
    totalStatePasses += a.total_passes_required || 0;
    totalElite += e;
    totalAdv += adv;
    totalMid += mid;
    totalReg += reg;

    const topScorer = m[0] || {};
    const topStr = (topScorer.name || "N/A") + " (" + formatNumber(topScorer.authoritative_migrate_power || 0) + ")";
    const avgPasses = m.length > 0 ? Number((a.total_passes_required / m.length).toFixed(1)) : 0;

    tableRows.push([
      a.rank,
      "[" + a.abbr + "]",
      a.name,
      a.leader,
      a.total_fightpower,
      m.length,
      a.total_passes_required,
      avgPasses,
      e,
      adv,
      mid,
      reg,
      topStr
    ]);
  }

  if (tableRows.length > 0) {
    ws.getRange(9, 1, tableRows.length, 13).setValues(tableRows);
  }

  const totRow = 9 + tableRows.length;
  const avgStatePasses = totalStateMembers > 0 ? Number((totalStatePasses / totalStateMembers).toFixed(1)) : 0;
  ws.getRange(totRow, 5).setValue(totalStatePower);
  ws.getRange(totRow, 6).setValue(totalStateMembers);
  ws.getRange(totRow, 7).setValue(totalStatePasses);
  ws.getRange(totRow, 8).setValue(avgStatePasses);
  ws.getRange(totRow, 9).setValue(totalElite);
  ws.getRange(totRow, 10).setValue(totalAdv);
  ws.getRange(totRow, 11).setValue(totalMid);
  ws.getRange(totRow, 12).setValue(totalReg);

  ws.getRange("B5").setValue(alliances.length + " Alliances");
  ws.getRange("D5").setValue(formatNumber(totalStateMembers) + " Players");
  ws.getRange("F5").setValue(formatNumber(totalStatePasses) + " Passes");
  ws.getRange("H5").setValue(formatNumber(totalAdv + totalElite) + " Players");
  ws.getRange("J5").setValue(avgStatePasses.toFixed(1) + " Passes");
  ws.getRange("L5").setValue((totalStatePower / 1e9).toFixed(2) + " Billion");
}

function formatNumber(num) {
  if (!num) return "0";
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function jsonResponse(data, statusCode) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
