<template>
  <div class="flex justify-start">
    <div class="max-w-3xl rounded-2xl px-6 py-4 shadow-sm bg-white border border-gray-200">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-semibold text-blue-600 flex-shrink-0">
          AI
        </div>
        <div class="flex items-center gap-2">
          <div class="flex gap-1">
            <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
          <span class="text-gray-600 text-sm">AI is thinking...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No imports needed - pure CSS animation
</script>
