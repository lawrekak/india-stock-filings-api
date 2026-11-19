/**
 * Google Apps Script: append new BSE announcements to the active sheet.
 * 1. Extensions → Apps Script, paste this file.
 * 2. Project Settings → Script properties: APIFY_TOKEN = your token.
 * 3. Triggers → add time-driven trigger for fetchAnnouncements (every hour).
 */
function fetchAnnouncements() {
  const token = PropertiesService.getScriptProperties().getProperty('APIFY_TOKEN');
  const url = 'https://api.apify.com/v2/acts/guiltless_baluster~india-corporate-announcements/run-sync-get-dataset-items?token=' + token;
  const input = { exchanges: ['BSE'], daysBack: 1, onlyNew: true, stateKey: 'google-sheet',
                  excludeKeywords: ['trading window', 'newspaper publication'] };
  const res = UrlFetchApp.fetch(url, { method: 'post', contentType: 'application/json', payload: JSON.stringify(input), muteHttpExceptions: true });
  const items = JSON.parse(res.getContentText());
  const sheet = SpreadsheetApp.getActiveSheet();
  if (sheet.getLastRow() === 0) sheet.appendRow(['Time (IST)', 'Company', 'Scrip', 'Category', 'Sub-category', 'Headline', 'PDF']);
  items.forEach(a => sheet.appendRow([a.announcedAt, a.companyName, a.bseScripCode, a.category, a.subCategory, a.headline, a.attachmentUrl]));
}
