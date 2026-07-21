<template>
  <div class="sync-status">
    <span>Poslední sync: {{ lastSync ? new Date(lastSync).toLocaleString('cs-CZ') : 'nikdy' }}</span>
    <button @click="$emit('trigger-sync')">Spustit sync</button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ lastSync?: string }>()
defineEmits(['trigger-sync'])
</script>
