// 保留行程备注，景点展示信息用最新目录。
export const refreshItineraryDays = (days, catalog) => {
  const current = new Map(catalog.map((attraction) => [String(attraction.id), attraction]))
  return days.map((day) => {
    const items = []
    const unavailableItems = []
    for (const stop of [...(day.items || []), ...(day.unavailableItems || [])]) {
      const attraction = current.get(String(stop.attraction?.id))
      if (attraction) items.push({ ...stop, attraction })
      else unavailableItems.push(stop)
    }
    return { ...day, items, unavailableItems }
  })
}
