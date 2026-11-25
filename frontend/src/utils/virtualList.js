// 地图侧栏只渲染当前可见的几行。
export const virtualWindow = (items, scrollTop, rowHeight = 112, size = 16, overscan = 3) => {
  const start = Math.max(0, Math.min(Math.floor(Math.max(0, scrollTop) / rowHeight) - overscan, Math.max(0, items.length - size)))
  const end = Math.min(items.length, start + size)
  return { start, end, items: items.slice(start, end) }
}
