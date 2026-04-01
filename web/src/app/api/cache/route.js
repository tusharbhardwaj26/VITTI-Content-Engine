import fs from 'fs';
import path from 'path';
import { NextResponse } from 'next/server';

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const requestedDate = searchParams.get('date');
  
  // Smart resolution for logs directory
  const getLogsPath = () => {
    const possiblePaths = [
      path.join(process.cwd(), 'logs'),          // If running from /web (Vercel default)
      path.join(process.cwd(), 'web', 'logs'),   // If running from repo root
    ];
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) return p;
    }
    return possiblePaths[0]; // fallback
  };

  const logsDir = getLogsPath();
  console.log('--- API: Reading logs from:', logsDir);
  console.log('--- API: Requested date:', requestedDate);
  const getAvailableDates = () => {
    try {
      if (!fs.existsSync(logsDir)) return [];
      const dates = new Set();
      
      // Root folder (new: logs stored directly in /logs)
      const rootFiles = fs.readdirSync(logsDir).filter(f => f.endsWith('.json'));
      rootFiles.forEach(f => {
        const match = f.match(/^(\d{4}-\d{2}-\d{2})/);
        if (match) dates.add(match[1]);
      });

      return Array.from(dates).sort().reverse();
    } catch (e) {
      console.error('Error getting dates:', e);
      return [];
    }
  };

  const getLogForDate = (type, date) => {
    try {
      if (!fs.existsSync(logsDir)) return null;
      
      // New: ideas logs live directly in /logs as YYYY-MM-DD.json
      if (type === 'ideas') {
        const fileName = date ? `${date}.json` : null;
        if (!fileName) return null;
        const filePath = path.join(logsDir, fileName);
        if (!fs.existsSync(filePath)) return null;
        try {
          const raw = fs.readFileSync(filePath, 'utf-8').trim();
          if (!raw) return null;
          const parsedArray = JSON.parse(raw);
          return Array.isArray(parsedArray) && parsedArray.length > 0
            ? parsedArray[parsedArray.length - 1]
            : null;
        } catch (parseErr) {
          console.error(`Failed to parse ideas log:`, parseErr.message);
          return null;
        }
      }
    } catch (e) {
      console.error(`Error reading ${type} log:`, e);
    }
    return null;
  };

  const availableDates = getAvailableDates();
  const dateToFetch = requestedDate || (availableDates.length > 0 ? availableDates[0] : null);

  return NextResponse.json({
    ideas: getLogForDate('ideas', dateToFetch),
    availableDates,
    selectedDate: dateToFetch
  });
}
