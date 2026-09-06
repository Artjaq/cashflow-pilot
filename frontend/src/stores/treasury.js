import { defineStore } from 'pinia'
import { ref } from 'vue'

import client from '@/api/client'

// L'endpoint /treasury est livré en Phase 1 — le store est posé, pas encore branché.
export const useTreasuryStore = defineStore('treasury', () => {
  const months = ref([])
  const loading = ref(false)

  async function fetchRange(from, to) {
    loading.value = true
    try {
      const { data } = await client.get('/treasury', { params: { from, to } })
      months.value = data
    } finally {
      loading.value = false
    }
  }

  return { months, loading, fetchRange }
})
