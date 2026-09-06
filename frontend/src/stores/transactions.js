import { defineStore } from 'pinia'
import { ref } from 'vue'

import client from '@/api/client'

export const useTransactionsStore = defineStore('transactions', () => {
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchAll(params = {}) {
    loading.value = true
    try {
      const { data } = await client.get('/transactions', { params })
      items.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await client.post('/transactions', payload)
    return data
  }

  async function update(id, payload) {
    const { data } = await client.put(`/transactions/${id}`, payload)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) items.value[index] = data
    return data
  }

  async function settle(id) {
    const { data } = await client.patch(`/transactions/${id}/settle`)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) items.value[index] = data
    return data
  }

  async function remove(id) {
    await client.delete(`/transactions/${id}`)
    items.value = items.value.filter((item) => item.id !== id)
  }

  return { items, total, loading, fetchAll, create, update, settle, remove }
})
