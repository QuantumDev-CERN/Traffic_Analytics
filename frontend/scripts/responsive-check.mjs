import { chromium } from "playwright";

const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "tablet-landscape", width: 1024, height: 768 },
  { name: "tablet-portrait", width: 768, height: 1024 },
  { name: "phone-large", width: 390, height: 844 },
  { name: "phone-small", width: 360, height: 800 }
];

const appUrl = process.env.FRONTEND_URL || "http://localhost:5173/";

function meaningfulConsoleMessages(messages) {
  return messages.filter(
    (line) =>
      !line.includes("Failed to load resource") &&
      !line.includes("OpenStreetMap") &&
      !line.includes("WebSocket is closed before the connection is established")
  );
}

async function checkViewport(browser, viewport) {
  const page = await browser.newPage({ viewport });
  const consoleMessages = [];
  page.on("console", (msg) => {
    if (["error", "warning"].includes(msg.type())) consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });

  await page.goto(appUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForSelector(".location-card", { timeout: 30000 });
  await page.waitForTimeout(1800);
  await page.getByTitle("Inject Connaught Place accident").click();
  await page.waitForTimeout(500);
  await page.getByTitle("Run route simulation").click();
  await page.waitForTimeout(500);
  await page.getByTitle("Run emergency corridor").click();
  await page.waitForTimeout(500);

  const metrics = await page.evaluate(() => {
    const checked = [
      ...document.querySelectorAll(
        ".topbar,.section,.map-shell,.route-panel,.location-card,.timeline-item,.alert,.status-strip,.hero-grid,.content-grid"
      )
    ];
    const offenders = checked
      .map((el) => {
        const rect = el.getBoundingClientRect();
        return {
          cls: typeof el.className === "string" ? el.className : el.tagName,
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          width: Math.round(rect.width),
          viewport: window.innerWidth
        };
      })
      .filter((item) => item.left < -2 || item.right > item.viewport + 2);
    const map = document.querySelector(".map")?.getBoundingClientRect();
    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      bodyScrollWidth: document.body.scrollWidth,
      map: map ? { width: Math.round(map.width), height: Math.round(map.height) } : null,
      cardCount: document.querySelectorAll(".location-card").length,
      alertCount: document.querySelectorAll(".alert").length,
      offenders: offenders.slice(0, 8)
    };
  });

  await page.close();

  const badConsole = meaningfulConsoleMessages(consoleMessages);
  const pass =
    metrics.scrollWidth <= metrics.clientWidth + 2 &&
    metrics.bodyScrollWidth <= metrics.clientWidth + 2 &&
    metrics.offenders.length === 0 &&
    metrics.map &&
    metrics.map.width > 250 &&
    metrics.map.height > 250 &&
    metrics.cardCount === 16 &&
    badConsole.length === 0;

  return { name: viewport.name, pass, badConsole, metrics };
}

const browser = await chromium.launch({ headless: true });
const results = [];
for (const viewport of viewports) {
  results.push(await checkViewport(browser, viewport));
}
await browser.close();

for (const result of results) {
  console.log(JSON.stringify(result, null, 2));
}

if (results.some((result) => !result.pass)) {
  process.exit(1);
}
