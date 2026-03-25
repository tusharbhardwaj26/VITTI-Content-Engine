export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const requestedDate = searchParams.get('date'); // format: YYYY-MM-DD
  
  const logsDir = path.join(process.cwd(), 'logs');
  
  // Helper to find all unique dates in the logs folder
  const getAvailableDates = () => {
    try {
      if (!fs.existsSync(logsDir)) return [];
      const files = fs.readdirSync(logsDir).filter(f => f.endsWith('.json'));
      const dates = new Set();
      files.forEach(f => {
        const match = f.match(/^(\d{4}-\d{2}-\d{2})/);
        if (match) dates.add(match[1]);
      });
      return Array.from(dates).sort().reverse();
    } catch (e) {
      return [];
    }
  };

  const getLogForDate = (type, date) => {
    try {
      if (!fs.existsSync(logsDir)) return null;
      
      let fileName;
      if (date) {
        fileName = `${date}-${type}.json`;
      } else {
        // Find latest for this type
        const files = fs.readdirSync(logsDir)
                        .filter(f => f.endsWith(`-${type}.json`))
                        .sort()
                        .reverse();
        if (files.length === 0) return null;
        fileName = files[0];
      }

      const filePath = path.join(logsDir, fileName);
      if (!fs.existsSync(filePath)) return null;

      const data = fs.readFileSync(filePath, 'utf-8');
      const parsedArray = JSON.parse(data);
      if (Array.isArray(parsedArray) && parsedArray.length > 0) {
         return parsedArray[parsedArray.length - 1]; 
      }
    } catch (e) {
      console.error(`Error reading ${type} log:`, e);
    }
    return null;
  };

  const availableDates = getAvailableDates();
  const dateToFetch = requestedDate || (availableDates.length > 0 ? availableDates[0] : null);

  return NextResponse.json({
    ceo: getLogForDate('ceo', dateToFetch),
    ideas: getLogForDate('ideas', dateToFetch),
    posts: getLogForDate('posts', dateToFetch),
    availableDates,
    selectedDate: dateToFetch
  });
}
