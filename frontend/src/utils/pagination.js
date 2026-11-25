// 收藏等完整列表需要把后面的分页也读完。
export const loadAllPages = async (fetchPage, field, params = {}) => {
  const items = []
  let page = 1
  while (true) {
    const response = await fetchPage({ ...params, page, per_page: 200 })
    const data = response.data
    const batch = data?.[field]
    if (!Array.isArray(batch)) throw new Error(`Missing paginated field: ${field}`)
    items.push(...batch)
    const pages = Number(data.pages)
    if (batch.length === 0 || (Number.isFinite(pages) && page >= pages) || items.length >= Number(data.total)) {
      return items
    }
    if (!Number.isFinite(pages)) throw new Error('Missing pagination metadata')
    page += 1
  }
}
