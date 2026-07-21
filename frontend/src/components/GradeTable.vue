<template>
  <table>
    <thead><tr><th>Předmět</th><th>Známka</th><th>Datum</th><th>Odměna (CZK)</th></tr></thead>
    <tbody>
      <tr v-for="m in marks" :key="m.id">
        <td>{{ m.subject }}</td>
        <td>{{ m.mark_text }}</td>
        <td>{{ new Date(m.mark_date).toLocaleDateString('cs-CZ') }}</td>
        <td>{{ m.reward_czk }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
defineProps<{ marks: any[] }>()
</script>
