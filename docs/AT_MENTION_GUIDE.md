# AI Chatbot -- @Mention Guide

## Overview

The @mention system lets you scope your queries to specific companies, time periods, dimensions, and entities directly from the chat input. Instead of typing "show sales for Tara Technologies this quarter," you can use structured @mentions that autocomplete against your live ERPNext data, reducing typos and ensuring exact matches.

Type `@` in the chat input to see the available categories. Select a category, then pick a value from the sub-dropdown. The selected value is inserted into your message automatically.

---

## How to Use

1. **Type `@` in the chat input.** A dropdown appears with all available mention categories.

2. **Select a category** from the dropdown (or continue typing to filter categories). For example, typing `@com` filters to show "Company."

3. **Select a value** from the sub-dropdown. For `@company`, this shows all companies in your ERPNext instance. For `@period`, this shows preset date ranges.

4. **The selected value is inserted** into your message at the cursor position, followed by a space. Continue typing the rest of your prompt.

5. **Send your message.** The AI chatbot interprets the @mention values as context for your query.

**Keyboard shortcuts within the dropdown:**
- Arrow Up / Arrow Down -- navigate options
- Enter -- select the highlighted option
- Escape -- close the dropdown

---

## Available @Mentions

| Mention | Description | Example |
|---------|-------------|---------|
| `@company` | Scope the query to a specific company | `@company Tara Technologies` -- show sales this quarter |
| `@period` | Use a preset date range | `@period This Quarter` -- what are our total sales? |
| `@cost_center` | Filter by cost center | `@cost_center Main` -- show expenses |
| `@department` | Filter by department | `@department Engineering` -- employee headcount |
| `@warehouse` | Filter by warehouse | `@warehouse Stores` -- stock levels |
| `@customer` | Focus on a specific customer | `@customer ABC Corp` -- outstanding invoices |
| `@item` | Focus on a specific item | `@item Laptop Pro` -- stock movement |
| `@accounting_dimension` | Custom accounting dimensions | `@accounting_dimension Project Alpha` -- expenses |

---

## @period Presets

The `@period` mention provides pre-calculated date ranges based on your ERPNext fiscal year configuration. When you select a period, the exact date range (e.g., "2025-04-01 to 2025-06-30") is inserted into your message.

| Preset | Description |
|--------|-------------|
| This Week | Monday to Sunday of the current week |
| This Month | 1st to last day of the current month |
| Last Month | 1st to last day of the previous month |
| This Quarter | Current fiscal quarter (based on your fiscal year start month) |
| This FY | Full current fiscal year (e.g., April 1 to March 31) |
| Last FY | Full previous fiscal year |

Note: "This Quarter" and fiscal year presets rely on your ERPNext fiscal year configuration. If your fiscal year runs April to March, Q1 is April-June, Q2 is July-September, and so on. The presets calculate dates dynamically based on the current date.

---

## @company Details

When you select `@company`, the dropdown shows all companies in your ERPNext instance. Your default company appears first in the list.

- If you do not use an `@company` mention, the chatbot defaults to your user's default company (set in ERPNext User Defaults).
- Company matching is fuzzy: typing "Tara" in the search will match "Tara Technologies (Demo)."
- In a multi-company setup, use `@company` to switch context between parent and subsidiary companies.

---

## @cost_center, @department, @warehouse

These mentions are company-scoped. The dropdown values are filtered to show only records belonging to your current company context (your default company, or the company specified by a preceding `@company` mention).

- `@cost_center` -- shows cost centers configured in ERPNext for the selected company
- `@department` -- shows departments within the selected company
- `@warehouse` -- shows warehouses belonging to the selected company

---

## @customer and @item

These mentions search across all customers or items in your ERPNext instance (not scoped by company). They are useful for focusing a query on a specific party or product.

- `@customer` -- autocompletes against Customer names in ERPNext
- `@item` -- autocompletes against Item codes/names in ERPNext
- Both support partial name matching via the search filter

---

## @accounting_dimension

ERPNext allows configuring custom accounting dimensions (e.g., Project, Branch, Cost Center) beyond the standard ones. The `@accounting_dimension` mention provides a two-level drill-down:

1. First, select the dimension type (e.g., "Project," "Branch").
2. Then, select a specific value within that dimension (e.g., "Project Alpha," "Mumbai Branch").

Only dimensions that are enabled (not disabled) in ERPNext's Accounting Dimension configuration appear in the dropdown. Values are filtered by company where applicable.

---

## Combining @Mentions

You can use multiple @mentions in a single prompt to create highly targeted queries. Each @mention adds an additional filter or context layer.

**Examples:**

```
@company Tara Technologies @period This Quarter -- show sales by territory
```
Sales data scoped to Tara Technologies for the current fiscal quarter, broken down by territory.

```
@department Sales @period Last Month -- attendance summary
```
Attendance data for the Sales department during the previous month.

```
@warehouse Stores @item Laptop Pro -- stock movement
```
Stock movement history for the Laptop Pro item in the Stores warehouse.

```
@company Tara Technologies @cost_center Marketing -- show expenses this month
```
Expense breakdown for the Marketing cost center within Tara Technologies.

```
@customer ABC Corp @period This FY -- outstanding invoices
```
All outstanding invoices for customer ABC Corp during the current fiscal year.

---

## Session Context vs. @Mentions

In addition to @mentions (which apply to a single message), some session-level settings persist across your entire conversation:

| Feature | Scope | How to Set |
|---------|-------|------------|
| @mentions | Single message | Type `@` in chat input |
| Include subsidiaries | Entire session | Say "include subsidiaries" or "show consolidated data" |
| Target currency | Entire session | Say "show in USD" or "convert to EUR" |
| Response language | Entire session | Use the language selector in the chat header |

Session settings remain active until you explicitly reset them or start a new conversation.

---

## Notes

- @mentions autocomplete against your live ERPNext data. If a customer, item, or warehouse does not appear in the dropdown, verify that the record exists and is not disabled in ERPNext.
- Company mentions use fuzzy matching, so partial names work (e.g., "Tara" matches "Tara Technologies (Demo)").
- `@accounting_dimension` only shows dimensions that are configured and enabled in ERPNext Setup > Accounting Dimension.
- If no `@company` is specified in your message, the chatbot uses your default company (as configured in ERPNext User Defaults).
- `@period` values are calculated dynamically based on your ERPNext fiscal year settings and the current date. They are inserted as exact date ranges (e.g., "2025-04-01 to 2025-06-30") so the AI knows the precise boundaries.
- The dropdown shows up to 20 values per category for performance. Type to search if the value you need is not immediately visible.
- @mentions work alongside natural language. You can say `@company Tara Technologies what were our sales last week?` -- the @mention provides the company context while the rest of your message is interpreted naturally.
