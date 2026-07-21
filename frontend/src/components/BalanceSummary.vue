<template>
  <div class="balance">
    <p>Zůstatek: <strong>{{ balanceCzk }} CZK</strong></p>
    <p v-if="estimatedSats">≈ {{ estimatedSats }} sats</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ balanceCzk: number; estimatedSats?: number }>()
</script>
