<template>
  <div class="login">
    <h1>Bakaláři Rewards</h1>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Uživatelské jméno" />
      <input v-model="password" type="password" placeholder="Heslo / PIN" />
      <button type="submit">Přihlásit</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

async function handleLogin() {
  try {
    const r = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    auth.setAuth(r.data.access_token, r.data.role)
    axios.defaults.headers.common['Authorization'] = `Bearer ${r.data.access_token}`
    router.push(r.data.role === 'parent' ? '/parent/dashboard' : '/child/dashboard')
  } catch {
    error.value = 'Nesprávné přihlašovací údaje'
  }
}
</script>
