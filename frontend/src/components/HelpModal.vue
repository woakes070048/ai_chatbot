<!-- Copyright (c) 2026, Sanjay Kumar and contributors -->
<!-- For license information, please see license.txt -->
<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center"
      @keydown.escape="close"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/40 dark:bg-black/60"
        @click="close"
      ></div>

      <!-- Modal -->
      <div
        class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col mx-4 border border-gray-200 dark:border-gray-700"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <HelpCircle :size="20" class="text-blue-600 dark:text-blue-400" />
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">Help & Reference</h2>
          </div>
          <button
            @click="close"
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X :size="18" class="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-gray-200 dark:border-gray-700 px-6">
          <button
            @click="activeTab = 'prompts'"
            :class="[
              'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px',
              activeTab === 'prompts'
                ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            ]"
          >
            <span class="flex items-center gap-1.5">
              <MessageSquare :size="14" />
              Sample Prompts
            </span>
          </button>
          <button
            @click="activeTab = 'mentions'"
            :class="[
              'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px',
              activeTab === 'mentions'
                ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            ]"
          >
            <span class="flex items-center gap-1.5">
              <AtSign :size="14" />
              @Mention Reference
            </span>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <!-- Sample Prompts Tab -->
          <div v-if="activeTab === 'prompts'" class="space-y-5">
            <div v-for="category in samplePrompts" :key="category.category">
              <div class="flex items-center gap-2 mb-2">
                <component :is="category.icon" :size="16" class="text-gray-500 dark:text-gray-400" />
                <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                  {{ category.category }}
                </h3>
              </div>
              <div class="space-y-1.5">
                <button
                  v-for="prompt in category.prompts"
                  :key="prompt.text"
                  @click="selectPrompt(prompt.text)"
                  class="w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors group"
                >
                  <div class="flex items-center justify-between gap-3">
                    <span class="text-sm text-gray-700 dark:text-gray-300 group-hover:text-blue-700 dark:group-hover:text-blue-400">
                      {{ prompt.text }}
                    </span>
                    <span :class="typeBadgeClass(prompt.type)" class="text-[10px] font-medium px-1.5 py-0.5 rounded flex-shrink-0">
                      {{ prompt.type }}
                    </span>
                  </div>
                  <p v-if="prompt.expected" class="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 leading-tight">
                    {{ prompt.expected }}
                  </p>
                </button>
              </div>
            </div>
          </div>

          <!-- @Mention Reference Tab -->
          <div v-if="activeTab === 'mentions'" class="space-y-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Type <kbd class="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-600 font-mono">@</kbd>
              in the chat input to filter by context. Mentions help the AI scope queries to specific companies, date ranges, or dimensions.
            </p>
            <div class="space-y-3">
              <div
                v-for="mention in mentionReference"
                :key="mention.mention"
                class="rounded-lg border border-gray-200 dark:border-gray-700 p-3"
              >
                <div class="flex items-start gap-3">
                  <code class="text-sm font-mono font-semibold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded flex-shrink-0">
                    {{ mention.mention }}
                  </code>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-gray-700 dark:text-gray-300">{{ mention.description }}</p>
                    <button
                      @click="selectPrompt(mention.example)"
                      class="mt-1.5 text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer italic"
                      :title="'Use this example'"
                    >
                      e.g. "{{ mention.example }}"
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-400 dark:text-gray-500">
          <template v-if="activeTab === 'prompts'">
            Click a prompt to use it. Results depend on your ERPNext data and enabled tools.
          </template>
          <template v-else>
            Click an example to populate the input. Mention values are loaded from your ERPNext site.
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import {
  HelpCircle, X, TrendingUp, DollarSign, Users, Target,
  Package, ShoppingCart, MessageSquare, AtSign, Settings,
} from 'lucide-vue-next'

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'select-prompt'])

const activeTab = ref('prompts')

const samplePrompts = [
  {
    category: 'Sales',
    icon: TrendingUp,
    prompts: [
      { text: 'What is the total sales this month?', type: 'number', expected: 'Revenue figure with currency, date range, company name' },
      { text: 'Show top 10 customers by revenue this year', type: 'table', expected: 'Ranked customer list with revenue amounts' },
      { text: 'Sales trend month by month for this fiscal year', type: 'chart', expected: 'ECharts line chart with monthly revenue trend' },
      { text: 'Compare sales this month vs last month', type: 'table', expected: 'Side-by-side comparison with variance' },
      { text: 'Break down sales by territory', type: 'chart', expected: 'ECharts pie chart with territory-wise revenue' },
      { text: 'Show sales by product category', type: 'chart', expected: 'ECharts bar chart by item group' },
      { text: 'Which products are most profitable?', type: 'chart', expected: 'Items with revenue, cost, margin %, and ECharts chart' },
      { text: 'Show profitability breakdown by territory', type: 'chart', expected: 'ECharts pie chart with territory margin data' },
      { text: 'Show sales for @company Acme Corp in @period Last Quarter', type: 'table', expected: 'Filtered sales data for the specified company and period' },
    ],
  },
  {
    category: 'Finance',
    icon: DollarSign,
    prompts: [
      { text: 'Give me a financial overview', type: 'chart', expected: 'Revenue, COGS, gross profit, net profit, cash position, AR/AP with bar chart' },
      { text: 'Show me the CFO dashboard', type: 'table', expected: 'Financial highlights, KPIs, cash flow, aging summaries, budget variance' },
      { text: 'Show profit and loss summary for this fiscal year', type: 'table', expected: 'Revenue, expenses, net profit for fiscal year' },
      { text: 'What are the current liquidity ratios?', type: 'number', expected: 'Current ratio, quick ratio with component breakdown' },
      { text: 'Show me profitability ratios for this fiscal year', type: 'number', expected: 'Gross margin %, net margin %, ROA %' },
      { text: 'What are the efficiency ratios?', type: 'number', expected: 'Inventory turnover, DSO, DPO with component breakdown' },
      { text: 'Show accounts receivable aging', type: 'chart', expected: 'Aging buckets (0-30, 31-60, 61-90, 90+) with ECharts bar chart' },
      { text: 'Who are the top 10 debtors?', type: 'chart', expected: 'Customers with outstanding amounts and ECharts horizontal bar' },
      { text: 'Show accounts payable aging', type: 'chart', expected: 'Supplier aging buckets with ECharts bar chart' },
      { text: 'What is our working capital position?', type: 'number', expected: 'Receivables, inventory, payables, net working capital' },
      { text: 'What is the cash conversion cycle?', type: 'number', expected: 'DSO, DIO, DPO, and CCC = DSO + DIO - DPO' },
      { text: 'Show budget vs actual for this fiscal year', type: 'chart', expected: 'Accounts with budget, actual, variance and multi-series bar chart' },
      { text: 'Show monthly budget variance', type: 'chart', expected: 'Monthly breakdown with ECharts multi-series line chart' },
      { text: 'Generate a cash flow statement', type: 'table', expected: 'Operating/financing activities with inflow, outflow, net' },
      { text: 'Show cash flow trend for the last 12 months', type: 'chart', expected: 'ECharts multi-series line chart (inflow, outflow, net)' },
      { text: 'What are the current bank balances?', type: 'number', expected: 'Bank/cash accounts with individual and total balances' },
      { text: 'Show month-over-month comparison for the last 3 months', type: 'chart', expected: 'Revenue, expenses, net profit with MoM variance and line chart' },
      { text: 'Show expense breakdown by @cost_center', type: 'chart', expected: 'Expenses filtered by cost center' },
      { text: 'Show consolidated revenue including subsidiaries', type: 'number', expected: 'Aggregated revenue from parent + all child companies' },
      { text: 'Show CFO dashboard with subsidiary data', type: 'table', expected: 'KPIs, cash flow, aging consolidated across all group companies' },
      { text: 'Show receivable aging across all group companies', type: 'chart', expected: 'Outstanding invoices from parent + subsidiaries with aging buckets' },
      { text: 'Show financial ratios for the group', type: 'number', expected: 'Liquidity, profitability, efficiency ratios from consolidated data' },
    ],
  },
  {
    category: 'HR',
    icon: Users,
    prompts: [
      { text: 'How many active employees do we have?', type: 'chart', expected: 'Total count with department-wise breakdown and pie chart' },
      { text: 'Show employee distribution by department', type: 'chart', expected: 'Pie chart with department segments' },
      { text: 'Show attendance summary for this month', type: 'chart', expected: 'Present, Absent, On Leave, Half Day, WFH with bar chart' },
      { text: 'What is the leave balance for an employee?', type: 'table', expected: 'Leave type breakdown: allocated, consumed, balance' },
      { text: 'Show payroll summary for this month', type: 'chart', expected: 'Gross pay, deductions, net pay with bar chart' },
      { text: 'Show department-wise salary distribution', type: 'chart', expected: 'Departments with gross/net pay and pie chart' },
      { text: 'Show employee turnover for this year', type: 'chart', expected: 'Hires, exits, turnover rate % with multi-series bar chart' },
      { text: 'Show headcount by @department', type: 'table', expected: 'Filtered count for the specified department' },
    ],
  },
  {
    category: 'CRM',
    icon: Target,
    prompts: [
      { text: 'Show me lead statistics', type: 'chart', expected: 'Total leads, status breakdown with pie chart' },
      { text: 'Show opportunity pipeline', type: 'chart', expected: 'Opportunities with amounts by sales stage, bar chart' },
      { text: 'What is our lead conversion rate?', type: 'number', expected: 'Total leads, converted count, conversion rate %' },
      { text: 'Which lead sources are performing best?', type: 'chart', expected: 'Sources ranked by lead count with pie chart' },
      { text: 'Show the sales funnel', type: 'chart', expected: 'Leads > Opportunities > Quotations > Orders with conversion rates' },
      { text: 'Show opportunities by sales stage', type: 'chart', expected: 'Stages with count and total value, bar chart' },
      { text: 'Show all open opportunities', type: 'table', expected: 'Filtered opportunities with status Open' },
      { text: 'List recent activities for @customer', type: 'table', expected: 'Activity log for the specified customer' },
    ],
  },
  {
    category: 'Stock',
    icon: Package,
    prompts: [
      { text: 'What is the total stock value?', type: 'number', expected: 'Aggregate stock valuation across warehouses' },
      { text: 'Show low stock items below reorder level', type: 'table', expected: 'Items below reorder point with quantities' },
      { text: 'Top 10 items by stock quantity', type: 'table', expected: 'Ranked items with warehouse and quantity' },
      { text: 'Show stock movement for the last 30 days', type: 'chart', expected: 'In/out movements with ECharts multi-series bar chart' },
      { text: 'Show stock ageing report', type: 'chart', expected: 'Items with age in days, aging buckets with bar chart' },
      { text: 'Show stock balance for @item in @warehouse', type: 'table', expected: 'Filtered stock balance for specific item and warehouse' },
    ],
  },
  {
    category: 'Operations',
    icon: Settings,
    prompts: [
      { text: 'Show pending purchase orders', type: 'table', expected: 'Open POs with supplier, amount, date' },
      { text: 'Top suppliers by purchase amount this year', type: 'table', expected: 'Ranked suppliers with purchase totals' },
      { text: 'Show the purchase trend for the last 12 months', type: 'chart', expected: 'ECharts line chart with monthly purchase amounts' },
      { text: 'Break down purchases by item group', type: 'chart', expected: 'ECharts bar chart by item group' },
      { text: 'What is the total purchase amount this quarter?', type: 'number', expected: 'Aggregate purchase value for the quarter' },
      { text: 'Show consolidated revenue', type: 'number', expected: 'Aggregated revenue across subsidiary companies' },
      { text: 'Search for customers matching "Acme"', type: 'table', expected: 'Matching customer records' },
    ],
  },
]

const mentionReference = [
  {
    mention: '@company',
    description: 'Select a specific company to scope your query. Useful in multi-company setups.',
    example: 'Show total revenue for @company Acme Corp',
  },
  {
    mention: '@period',
    description: 'Date range presets — This Week, This Month, Last Month, This Quarter, Last Quarter, This Fiscal Year, Last Fiscal Year, or YTD.',
    example: 'Show sales trend in @period Last Quarter',
  },
  {
    mention: '@cost_center',
    description: 'Filter results by a specific cost center.',
    example: 'Show expenses for @cost_center Main - AC',
  },
  {
    mention: '@department',
    description: 'Filter by department for HR or expense queries.',
    example: 'Show headcount in @department Engineering',
  },
  {
    mention: '@warehouse',
    description: 'Filter stock queries by warehouse location.',
    example: 'Show stock balance in @warehouse Stores - AC',
  },
  {
    mention: '@customer',
    description: 'Reference a specific customer in sales or CRM queries.',
    example: 'Show all invoices for @customer John Doe',
  },
  {
    mention: '@item',
    description: 'Reference a specific item in stock or sales queries.',
    example: 'What is the stock level for @item Widget A?',
  },
  {
    mention: '@accounting_dimension',
    description: 'Custom accounting dimensions configured in your ERPNext site (e.g., Branch, Project).',
    example: 'Show revenue by @accounting_dimension Branch',
  },
]

const typeBadgeClass = (type) => {
  const classes = {
    table: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400',
    chart: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400',
    number: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400',
    text: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-400',
  }
  return classes[type] || 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
}

const selectPrompt = (text) => {
  emit('select-prompt', text)
  close()
}

const close = () => {
  emit('update:modelValue', false)
}
</script>
