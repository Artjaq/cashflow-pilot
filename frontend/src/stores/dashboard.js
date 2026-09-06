import { defineStore } from 'pinia'
import { ref } from 'vue'

import client from '@/api/client'

// L'endpoint /dashboard est livré en Phase 1 — le store est posé, pas encore branché.
export const useDashboardStore = defineStore('dashboard', () => {
  const kpis = ref(null)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      const { data } = await client.get('/dashboard')
      kpis.value = data
    } finally {
      loading.value = false
    }
  }

  return { kpis, loading, fetch }
})
