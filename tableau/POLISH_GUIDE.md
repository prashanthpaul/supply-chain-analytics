# Tableau Polish Guide — Supply Chain Dashboard
Step-by-step. Follow top to bottom. ~15 minutes total.

---

## STEP 1 — Open the file

1. Open **Tableau Desktop** (double-click the app)
2. Click **File → Open**
3. Navigate to: `supply-chain-analytics/tableau/`
4. Select `supply_chain.twb` → click **Open**

---

## STEP 2 — Connect to Snowflake

A password prompt will appear for each data source (5 times).

Each time, type exactly:
```
Prashanthpaul@12
```
Click **Sign In** → repeat until all 5 connect.

> ✅ You'll see sheets appear at the bottom of the screen when connected.

---

## STEP 3 — Set the workbook font (do this FIRST)

1. Click **Format** in the top menu bar
2. Click **Workbook...**
3. A panel opens on the left side
4. Under **Worksheet** → click the font dropdown → type `Georgia` → select it
5. Set size to `11`
6. Under **Dashboard** → same thing: `Georgia`, size `11`
7. Click anywhere to close the panel

---

## STEP 4 — Polish each worksheet (repeat for all 7 sheets)

Click each sheet tab at the bottom one by one.

### 4A — "Revenue Trend" sheet

1. **Remove gridlines:**
   - Click **Format → Lines**
   - Set **Grid Lines** → None (click the dotted line icon, pick the blank option)
   - Set **Zero Lines** → None

2. **Format the Y-axis:**
   - Right-click the left axis (the numbers) → **Format...**
   - Under **Numbers** → choose **Currency (Custom)**
   - Decimal places: `0`
   - Prefix: `$`
   - Click the X to close

3. **Add a title:**
   - Double-click the sheet name tab at the bottom → rename to `Monthly Revenue & Profit`

4. **Color the area:**
   - In the **Marks** card on the left → click the **Color** box
   - Click **Edit Colors...**
   - Pick the amber swatch `#f0a500`
   - Set **Opacity** to `70%`
   - Click OK

---

### 4B — "Top Products" sheet

1. Remove gridlines (same as above: Format → Lines → Grid Lines → None)

2. **Sort bars:**
   - Click the **Revenue** axis label → click the **sort descending** icon (↓) that appears

3. **Format the X-axis as currency:**
   - Right-click X-axis → Format → Numbers → Currency → `$` prefix, 0 decimals

4. Rename tab: `Top 10 Products by Revenue`

---

### 4C — "Supplier On-Time Rate" sheet

1. Remove gridlines

2. **Add reference line at 92%:**
   - Right-click on the X-axis → **Add Reference Line**
   - Value: `92`
   - Label: **Custom** → type: `Target: 92%`
   - Line: dashed, color `#2e2820`
   - Click OK

3. **Format X-axis as percentage:**
   - Right-click X-axis → Format → Numbers → **Percentage** → 1 decimal place

4. Rename tab: `Supplier On-Time Rate`

---

### 4D — "Regional Revenue" sheet

1. Remove gridlines

2. Format Y-axis as currency (`$`, 0 decimals)

3. **Show data labels:**
   - In the Marks card → click **Label** checkbox → check **Show mark labels**
   - Set font color to `#c4b8aa`, size `10`

4. Rename tab: `Revenue by Region`

---

### 4E — "Carrier Performance" sheet

1. Remove gridlines

2. **Add reference line at 92% on Y-axis:**
   - Right-click Y-axis → Add Reference Line → Value: `92`
   - Label: `Target: 92%`, dashed, color `#2e2820`

3. **Format Y-axis as percentage**, X-axis as currency

4. Rename tab: `Carrier Performance`

---

### 4F — "Margin by Category" sheet

1. Remove gridlines

2. **Format X-axis as percentage** (1 decimal)

3. Rename tab: `Margin % by Category`

---

### 4G — "Revenue vs Margin" sheet

1. Remove gridlines

2. Format X-axis as currency, Y-axis as percentage

3. Rename tab: `Revenue vs Margin`

---

## STEP 5 — Polish the Dashboard

Click the **"Supply Chain Executive Dashboard"** tab at the bottom.

### 5A — Background
- Click **Format → Shading**
- Set **Dashboard** → color `#111010` (type it in the hex box)

### 5B — Header text
- Double-click the top text banner
- Change text to:
  ```
  SUPPLY CHAIN ANALYTICS   ·   Executive Dashboard   ·   Jan 2022 – Dec 2024
  ```
- Font: `Georgia Bold`, size `16`, color `#f0a500`
- Background: `#1a1612`
- Click outside to close

### 5C — Add sheet titles
- For each chart zone: click the little arrow (▼) in the top-right corner of the zone
- Click **Title** → check **Show Title**
- The title comes from the sheet name you set in Step 4

### 5D — Remove borders between zones (optional cleaner look)
- Click **Format → Borders**
- Set **Row Divider** and **Column Divider** → None

### 5E — Add padding inside each chart
- Click any chart zone to select it
- In the bottom-left **Layout** panel → set all **Outer Padding** to `8`

---

## STEP 6 — Save

1. Click **File → Save**
   - This saves as `.twb` (keeps the XML format, good for GitHub)

2. To also export as a **packaged workbook** (shares data too):
   - Click **File → Export Packaged Workbook**
   - Save as `supply_chain_packaged.twbx`
   - This file can be sent to anyone with Tableau Reader (free)

---

## STEP 7 — Take a screenshot for your portfolio

1. On the Dashboard tab → click **File → Print to PDF** (or take a screenshot)
2. Save it as `dashboard_preview.png`
3. Add it to your portfolio project detail page (`projects/supply-chain.html`)

---

## Quick reference — exact colors

| Element | Hex |
|---------|-----|
| Background | `#111010` |
| Panel/card | `#1a1612` |
| Border | `#2e2820` |
| Primary (amber) | `#f0a500` |
| Positive (teal) | `#2ec4a9` |
| Negative (red) | `#e05c4b` |
| Text primary | `#f0e6d3` |
| Text muted | `#7a6e62` |

---

## Quick reference — exact number formats

| Measure | Format to use |
|---------|--------------|
| Revenue, Cost | Currency → `$` prefix, 0 decimals |
| Margin %, On-Time % | Percentage, 1 decimal |
| Orders, Units | Number (standard), 0 decimals |
| Avg Delay Days | Number, 1 decimal, suffix ` days` |
