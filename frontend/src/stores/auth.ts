import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const role = ref<'parent' | 'child' | null>(null)

  function setAuth(t: string, r: 'parent' | 'child') {
    token.value = t
    role.value = r
  }

  function logout() {
    token.value = null
    role.value = null
  }

  return { token, role, setAuth, logout }
})
