import { defineStore } from 'pinia'
import { ref } from 'vue'

import client from '@/api/client'

export const useCategoriesStore = defineStore('categories', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await client.get('/categories')
      items.value = data
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await client.post('/categories', payload)
    items.value.push(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await client.put(`/categories/${id}`, payload)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) items.value[index] = data
    return data
  }

  async function remove(id) {
    await client.delete(`/categories/${id}`)
    items.value = items.value.filter((item) => item.id !== id)
  }

  return { items, loading, fetchAll, create, update, remove }
})
