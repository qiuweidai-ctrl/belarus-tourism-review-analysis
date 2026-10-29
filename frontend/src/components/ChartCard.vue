<template>
  <section class="chart-card card">
    <header class="chart-head">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="spacer"></div>
      <slot name="actions"></slot>
    </header>
    <BaseChart :option="option" :height="height" :loading="loading" :empty-text="emptyText" />
    <footer v-if="$slots.footer" class="chart-footer">
      <slot name="footer"></slot>
    </footer>
  </section>
</template>

<script setup>
import BaseChart from './BaseChart.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  option: { type: Object, required: true },
  height: { type: String, default: '300px' },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'No data to display' }
})
</script>

<style scoped>
.chart-card { padding: 1.1rem 1.15rem 1.15rem; }
.chart-head { display: flex; align-items: flex-start; gap: .75rem; margin-bottom: .85rem; }
.chart-head h3 { margin: 0; font-size: 1.02rem; }
.chart-head p { margin: .15rem 0 0; font-size: .8rem; color: var(--text-mute); }
.chart-footer { margin-top: .55rem; text-align: center; color: var(--text-soft); font-size: .8rem; }
</style>
