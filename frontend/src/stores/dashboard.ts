import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref<any>(null)
  const loading = ref(false)

  async function fetchParentDashboard() {
    loading.value = true
    try {
      const r = await axios.get('/api/parent/dashboard')
      data.value = r.data
    } finally {
      loading.value = false
    }
  }

  return { data, loading, fetchParentDashboard }
})
