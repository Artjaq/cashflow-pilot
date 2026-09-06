<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title ?? '')
</script>

<template>
  <header class="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
    <h1 class="text-base font-semibold text-slate-800">{{ title }}</h1>
    <span class="text-sm text-slate-400">CHF</span>
  </header>
</template>
