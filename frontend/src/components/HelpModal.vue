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
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">Sample Prompts</h2>
          </div>
          <button
            @click="close"
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X :size="18" class="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-6 py-4 space-y-5">
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
                class="w-full text-left px-3 py-2.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors group flex items-center justify-between gap-3"
              >
                <span class="text-sm text-gray-700 dark:text-gray-300 group-hover:text-blue-700 dark:group-hover:text-blue-400">
                  {{ prompt.text }}
                </span>
                <span :class="typeBadgeClass(prompt.type)" class="text-[10px] font-medium px-1.5 py-0.5 rounded flex-shrink-0">
                  {{ prompt.type }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-400 dark:text-gray-500">
          Click a prompt to use it. Results depend on your ERPNext data and enabled tools.
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { HelpCircle, X, TrendingUp, DollarSign, Users, Target, Package, ShoppingCart } from 'lucide-vue-next'

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'select-prompt'])

const samplePrompts = [
  {
    category: 'Sales',
    icon: TrendingUp,
    prompts: [
      { text: 'Show top 10 customers by revenue this year', type: 'table' },
      { text: 'Sales trend month by month for this fiscal year', type: 'chart' },
      { text: 'What is the total sales amount this quarter?', type: 'number' },
      { text: 'Compare sales this month vs last month', type: 'table' },
    ],
  },
  {
    category: 'Finance',
    icon: DollarSign,
    prompts: [
      { text: 'Show profit and loss summary for this fiscal year', type: 'table' },
      { text: 'What are our outstanding receivables?', type: 'table' },
      { text: 'Show expense breakdown by cost center', type: 'chart' },
      { text: 'What is the current cash balance?', type: 'number' },
    ],
  },
  {
    category: 'HR',
    icon: Users,
    prompts: [
      { text: 'How many employees do we have?', type: 'number' },
      { text: 'Show department-wise headcount', type: 'table' },
      { text: 'List employees on leave today', type: 'table' },
      { text: 'Show attendance summary for this month', type: 'chart' },
    ],
  },
  {
    category: 'CRM',
    icon: Target,
    prompts: [
      { text: 'Show all open opportunities', type: 'table' },
      { text: 'How many new leads this month?', type: 'number' },
      { text: 'Lead conversion rate this quarter', type: 'number' },
      { text: 'Show opportunity pipeline by stage', type: 'chart' },
    ],
  },
  {
    category: 'Stock',
    icon: Package,
    prompts: [
      { text: 'Show low stock items below reorder level', type: 'table' },
      { text: 'What is the total stock value?', type: 'number' },
      { text: 'Top 10 items by stock quantity', type: 'table' },
      { text: 'Show stock movement for the last 30 days', type: 'chart' },
    ],
  },
  {
    category: 'Purchasing',
    icon: ShoppingCart,
    prompts: [
      { text: 'Show pending purchase orders', type: 'table' },
      { text: 'Top suppliers by purchase amount this year', type: 'table' },
      { text: 'What is the total purchase amount this quarter?', type: 'number' },
      { text: 'Purchase trends month by month', type: 'chart' },
    ],
  },
]

const typeBadgeClass = (type) => {
  const classes = {
    table: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400',
    chart: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400',
    number: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400',
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
