# AI Chatbot -- Sample User Prompts

A comprehensive guide of sample prompts you can try with the AI Chatbot. Each prompt includes the expected output format and a brief description of what to expect. Click any prompt in the Help Modal (the help icon next to the send button) to insert it directly into the chat input.

Output types:
- **table** -- sortable data table, often with hierarchical grouping
- **chart** -- interactive Apache ECharts visualization (bar, line, pie, etc.)
- **number** -- single metric with optional supporting context
- **mixed** -- combination of cards, tables, and charts
- **record** -- record creation or update confirmation
- **search** -- search results listing

---

## Sales / Selling

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show top 10 customers by revenue this year | table | Ranked list of customers with revenue amounts in company currency |
| Sales trend month by month for this fiscal year | chart | Line chart showing monthly revenue progression across the fiscal year |
| What is the total sales amount this quarter? | number | Single aggregate sales figure for the current fiscal quarter |
| Compare sales this month vs last month | table | Side-by-side comparison with absolute difference and percentage change |
| Show sales breakdown by territory | chart | Pie or donut chart showing revenue distribution across territories |
| Sales by item group for this year | chart | Bar chart with revenue broken down by item group |
| Who are our top 5 customers by order count? | table | Ranked list of customers sorted by number of sales orders placed |
| Show monthly sales trend for last 6 months | chart | Line chart with six data points showing recent revenue trajectory |

---

## Finance / Accounting

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show profit and loss summary for this fiscal year | table | Income, expense, and net profit/loss grouped by account hierarchy |
| What are our outstanding receivables? | table | Receivables aging buckets (0-30, 30-60, 60-90, 90+ days) with totals |
| Show expense breakdown by cost center | chart | Pie or bar chart of expenses distributed across cost centers |
| What is the current cash balance? | number | Aggregate balance across all cash and bank accounts |
| Show receivables aging report | table | Detailed aging with customer names, invoice references, and overdue amounts |
| What are our key financial ratios? | table | Current ratio, quick ratio, debt-to-equity, gross margin, net margin, and similar |
| Show payables aging summary | table | Supplier-wise payables grouped into aging buckets |
| Budget vs actual for this quarter | table | Comparison of budgeted amounts against actual expenses with variance |
| Show working capital analysis | table | Current assets, current liabilities, and net working capital breakdown |
| Give me a CFO dashboard overview | mixed | Summary cards (revenue, expenses, profit, cash) plus key charts and ratios |

---

## HR / HRMS

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| How many employees do we have? | number | Total active employee count |
| Show department-wise headcount | table | Department names with employee counts, sorted by headcount |
| List employees on leave today | table | Names, departments, and leave types for employees on leave today |
| Show attendance summary for this month | chart | Bar or stacked chart of present, absent, half-day, and on-leave counts |
| What is the total payroll cost this month? | number | Sum of gross or net salary for the current month's payroll |
| Show department-wise salary distribution | chart | Bar chart showing total salary expenditure per department |
| Employee turnover rate this year | number | Percentage of employees who left relative to average headcount |
| Show new hires vs exits for last 6 months | chart | Dual-bar or line chart comparing monthly joinings and separations |

---

## CRM

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show all open opportunities | table | List of opportunities with customer, amount, stage, and expected close date |
| How many new leads this month? | number | Count of leads created in the current month |
| Lead conversion rate this quarter | number | Percentage of leads converted to opportunities or customers this quarter |
| Show opportunity pipeline by stage | chart | Bar chart with opportunity count or value grouped by sales stage |
| Analyze leads by source | chart | Pie chart showing lead distribution by source (website, referral, etc.) |
| Show sales funnel from leads to orders | chart | Funnel visualization from leads to opportunities to quotations to orders |
| Opportunities grouped by sales stage | chart | Horizontal bar chart showing opportunity value at each pipeline stage |
| Show top opportunities by value | table | Ranked list of the highest-value open opportunities with details |

---

## Stock / Inventory

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show low stock items below reorder level | table | Items where current stock is below configured reorder level |
| What is the total stock value? | number | Aggregate valuation of all warehouse stock in company currency |
| Top 10 items by stock quantity | table | Items ranked by quantity on hand across all warehouses |
| Show stock movement for last 30 days | chart | Line or bar chart of stock receipts and issues over the past 30 days |
| Stock ageing report for main warehouse | table | Items grouped by age brackets showing how long stock has been held |
| Which items are running low? | table | Items approaching or below reorder level with current quantities |
| Show warehouse-wise stock summary | table | Stock quantities and values broken down by warehouse |
| Item-wise stock balance for all warehouses | table | Matrix of items vs. warehouses with quantities |

---

## Purchasing / Buying

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show pending purchase orders | table | Open purchase orders with supplier, amount, and expected delivery date |
| Top suppliers by purchase amount this year | table | Ranked list of suppliers by total purchase value |
| Total purchase amount this quarter | number | Aggregate purchase value for the current fiscal quarter |
| Purchase trends month by month | chart | Line chart showing monthly purchase amounts over time |
| Purchase breakdown by item group | chart | Pie or bar chart of purchase spend distributed across item groups |
| Supplier performance analysis | table | Suppliers with delivery timeliness, order count, and rejection rates |
| Show overdue purchase orders | table | Purchase orders past their expected delivery date |
| Compare purchase amounts: this quarter vs last quarter | table | Side-by-side quarterly comparison with variance |

---

## Document Processing (IDP)

Upload a document (invoice, PO, quotation) using the attachment button, then use these prompts.

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Extract data from this invoice | table | Structured extraction of header fields and line items for review |
| Create a purchase invoice from the extracted data | record | ERPNext Purchase Invoice created after user confirmation |
| Extract and create a sales invoice from this document | table + record | Extraction displayed for review, then record created on confirmation |
| Compare this uploaded PO with Sales Order SO-00123 | table | Field-by-field comparison highlighting discrepancies |
| What does this document contain? | table | Extracted fields, party name, amounts, line items, and dates |
| Process this receipt and create a purchase receipt | table + record | Extraction from receipt image, then Purchase Receipt creation |

Notes on IDP:
- Supported file types: PDF, images (PNG, JPG, TIFF), Excel, Word, CSV
- Documents can be in any language; extracted values are translated to English by default
- The chatbot always presents extracted data for your review before creating any record
- If items or parties do not exist in ERPNext, the chatbot will ask whether to create them

---

## Predictive Analytics

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Forecast sales revenue for next 3 months | chart | Line chart with predicted revenue, confidence intervals, and trend direction |
| Predict demand for [Item Name] for next quarter | chart | Item-level demand forecast with upper and lower bounds |
| Cash flow projection for next 3 months | chart | Projected cash inflows and outflows with net position |
| Detect any anomalies in our recent transactions | table | Flagged transactions with unusually large amounts or atypical patterns |
| Revenue forecast by territory for next quarter | chart | Territory-wise revenue predictions with confidence bands |
| Show anomalies in purchase transactions | table | Unusual purchase amounts, new suppliers with large first orders |

Notes on Predictive Analytics:
- Forecasts use statistical methods (exponential smoothing, linear regression) on historical data
- At least 6 months of historical data is recommended for reliable forecasts
- Confidence intervals widen further into the future, reflecting increasing uncertainty
- Anomaly detection flags statistical outliers, not necessarily errors

---

## Multi-Company

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Show consolidated sales across all companies | table | Aggregated sales from parent and all subsidiary companies |
| @company Tara Technologies show sales this quarter | table | Sales data scoped to the specified company only |
| Include subsidiaries in the sales report | mixed | Toggles subsidiary inclusion for all subsequent queries in the session |
| Show revenue breakdown by subsidiary | table | Revenue figures for each child company under the parent |
| @company Tara Technologies @period This Quarter show P&L | table | Profit and loss scoped to a specific company and time period |
| Compare sales across companies this fiscal year | table | Company-wise sales comparison with totals |

---

## General / Operations

These prompts require write operations to be enabled in Chatbot Settings.

| Prompt | Output | Expected Result |
|--------|--------|-----------------|
| Create a new customer "ABC Corp" | record | Customer record created after confirmation of details |
| Search for item "Laptop" | search | Matching items displayed with codes, names, and stock status |
| Update status of SO-00123 to Closed | record | Sales Order status updated after confirmation |
| Create a sales order for customer ABC Corp | record | Guided sales order creation with item and quantity prompts |
| Show details of Purchase Order PO-00456 | table | Full details of the specified purchase order |
| What ERPNext tools are available? | table | List of enabled tool categories and their capabilities |

---

## Tips

**Use @mentions to scope queries.** Type `@` in the chat input to see available categories: `@company`, `@period`, `@cost_center`, `@department`, `@warehouse`, `@customer`, `@item`, `@accounting_dimension`. These let you target specific companies, date ranges, or entities without typing full names. See the [AT_MENTION_GUIDE.md](AT_MENTION_GUIDE.md) for full details.

**Charts are interactive.** Prompts that return chart output render as interactive Apache ECharts visualizations. You can hover for tooltips, zoom, and pan. Charts are also included when you export a conversation to PDF.

**Results depend on your data and permissions.** The chatbot queries live ERPNext data. If a module is not installed (e.g., HRMS) or tools are disabled in Chatbot Settings, related prompts will not return results. Your user role permissions also apply -- you only see data you are authorized to access.

**Ask follow-up questions.** You can drill down into any result. For example, after seeing top customers, ask "Show sales details for the top customer" or "Break this down by item group."

**Upload documents for IDP processing.** Click the paperclip icon (or drag and drop) to attach invoices, purchase orders, receipts, or other documents. The chatbot extracts structured data using AI vision and maps it to ERPNext fields.

**Use voice input.** Click the microphone icon to dictate your prompt. The chatbot auto-sends after detecting 2 seconds of silence. Voice input works for any prompt type.

**Export conversations.** Use the download icon on any assistant message to export it as a PDF. You can also export the entire conversation from the chat header menu.

**Set your preferred language.** Use the language selector in the chat header to receive responses in Hindi, Spanish, French, German, and other supported languages.

**Combine @mentions for precision.** Use multiple @mentions in a single prompt for highly targeted queries: `@company Tara Technologies @period This Quarter -- show sales by territory`.
