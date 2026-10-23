<template>
  <div class="empty-state">
    <span class="emoji" aria-hidden="true">{{ icon }}</span>
    <p class="empty-title">{{ title }}</p>
    <p v-if="hint" class="empty-hint">{{ hint }}</p>
    <slot></slot>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '🗂️' },
  title: { type: String, default: 'Nothing here yet' },
  hint: { type: String, default: '' }
})
</script>

<style scoped>
.empty-state .empty-title { margin: .2rem 0 .3rem; font-weight: 600; color: var(--text-soft); }
.empty-state .empty-hint { margin: 0; font-size: .85rem; max-width: 44ch; margin-inline: auto; }
</style>