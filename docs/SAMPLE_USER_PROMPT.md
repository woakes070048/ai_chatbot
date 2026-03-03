# AI Chatbot — Sample User Prompts

Sample prompts to help users get started with the AI Chatbot. These are shown in the **Help Modal** (click the help icon next to the send button).

Each prompt includes the expected output format: **table**, **chart**, or **number**.

---

## Sales

| Prompt | Output |
|--------|--------|
| Show top 10 customers by revenue this year | table |
| Sales trend month by month for this fiscal year | chart |
| What is the total sales amount this quarter? | number |
| Compare sales this month vs last month | table |

## Finance

| Prompt | Output |
|--------|--------|
| Show profit and loss summary for this fiscal year | table |
| What are our outstanding receivables? | table |
| Show expense breakdown by cost center | chart |
| What is the current cash balance? | number |

## HR

| Prompt | Output |
|--------|--------|
| How many employees do we have? | number |
| Show department-wise headcount | table |
| List employees on leave today | table |
| Show attendance summary for this month | chart |

## CRM

| Prompt | Output |
|--------|--------|
| Show all open opportunities | table |
| How many new leads this month? | number |
| Lead conversion rate this quarter | number |
| Show opportunity pipeline by stage | chart |

## Stock

| Prompt | Output |
|--------|--------|
| Show low stock items below reorder level | table |
| What is the total stock value? | number |
| Top 10 items by stock quantity | table |
| Show stock movement for the last 30 days | chart |

## Purchasing

| Prompt | Output |
|--------|--------|
| Show pending purchase orders | table |
| Top suppliers by purchase amount this year | table |
| What is the total purchase amount this quarter? | number |
| Purchase trends month by month | chart |

---

## Tips

- Use **@mentions** to scope your query: `@company`, `@period`, `@cost_center`, `@department`, `@warehouse`, `@customer`, `@item`.
- Prompts that return **chart** output render interactive ECharts visualizations.
- Prompts that return **table** output show sortable data tables with optional hierarchical grouping.
- Prompts that return **number** output give a single metric with optional context.
- Results depend on your ERPNext data, enabled tools, and user permissions.
