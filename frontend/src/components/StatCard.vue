<template>
  <div class="stat-card card card-hover">
    <span class="stat-icon" :style="{ background: tint, color: color }" aria-hidden="true">{{ icon }}</span>
    <div class="stat-body">
      <span class="stat-value" :style="{ color: color }">{{ formatted }}</span>
      <span class="stat-label">{{ label }}</span>
      <span v-if="hint" class="stat-hint">{{ hint }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  icon: { type: String, default: '📈' },
  color: { type: String, default: 'var(--brand-600)' },
  suffix: { type: String, default: '' },
  decimals: { type: Number, default: null },
  hint: { type: String, default: '' }
})

const formatted = computed(() => {
  const v = props.value
  if (typeof v !== 'number') return String(v ?? '') + props.suffix
  const d = props.decimals != null ? props.decimals : (Number.isInteger(v) ? 0 : 1)
  const n = d === 0 ? v.toLocaleString('en-US') : v.toFixed(d)
  return n + props.suffix
})

const tint = computed(() => {
  const map = {
    'var(--brand-600)': 'var(--brand-50)',
    'var(--accent-600)': 'var(--warning-soft)',
    'var(--danger)': 'var(--danger-soft)',
    'var(--info)': 'var(--info-soft)',
    'var(--success)': 'var(--success-soft)'
  }
  return map[props.color] || 'var(--surface-2)'
})
</script>

<style scoped>
.stat-card {
  display: flex; align-items: center; gap: .9rem;
  padding: 1.05rem 1.15rem;
}
.stat-icon {
  width: 46px; height: 46px; flex-shrink: 0;
  border-radius: 13px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
}
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-value { font-size: 1.55rem; font-weight: 800; line-height: 1.15; letter-spacing: -.02em; }
.stat-label { font-size: .82rem; color: var(--text-soft); font-weight: 500; }
.stat-hint { font-size: .72rem; color: var(--text-mute); margin-top: .1rem; }
</style>