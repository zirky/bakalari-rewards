<template>
  <div class="payout-card">
    <p>{{ payout.amount_czk }} CZK / {{ payout.amount_sats }} sats</p>
    <span :class="'status-' + payout.status">{{ payout.status }}</span>
    <button v-if="payout.status === 'pending' && canApprove" @click="$emit('approve', payout.id)">
      Schválit
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ payout: any; canApprove?: boolean }>()
defineEmits(['approve'])
</script>
