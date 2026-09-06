<script setup>
const links = [
  { name: 'dashboard', label: 'Tableau de bord' },
  { name: 'transactions', label: 'Transactions' },
  { name: 'treasury', label: 'Trésorerie' },
  { name: 'payment-plans', label: 'Plans de paiement' },
  { name: 'budgets', label: 'Budgets' },
  { name: 'categories', label: 'Catégories' },
]

const upcoming = [
  { label: 'Gmail', hint: 'Phase 2' },
  { label: 'Assistant', hint: 'Phase 3' },
]
</script>

<template>
  <aside class="w-60 shrink-0 border-r border-slate-200 bg-white">
    <div class="px-5 py-4 text-lg font-semibold text-slate-800">CashFlow-Pilot</div>

    <nav class="flex flex-col gap-1 px-3">
      <RouterLink
        v-for="link in links"
        :key="link.name"
        :to="{ name: link.name }"
        class="rounded px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
        active-class="bg-slate-100 font-medium text-slate-900"
      >
        {{ link.label }}
      </RouterLink>

      <div class="mt-4 border-t border-slate-200 pt-3">
        <span
          v-for="item in upcoming"
          :key="item.label"
          class="flex cursor-not-allowed items-center justify-between rounded px-3 py-2 text-sm text-slate-300"
          :title="`Disponible en ${item.hint}`"
        >
          {{ item.label }}
          <span class="text-xs">{{ item.hint }}</span>
        </span>
      </div>
    </nav>
  </aside>
</template>
