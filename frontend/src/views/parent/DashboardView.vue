<template>
  <div>
    <h2>Rodičovský panel</h2>
    <p v-if="store.loading">Načítám...</p>
    <pre v-else>{{ store.data }}</pre>
    <!-- TODO: GradeTable, BalanceSummary, SyncStatus komponenty -->
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useDashboardStore } from '../../stores/dashboard'
const store = useDashboardStore()
onMounted(() => store.fetchParentDashboard())
</script>
