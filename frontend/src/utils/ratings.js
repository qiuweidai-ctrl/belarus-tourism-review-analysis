export const externalRating = (item) => item?.primary_external_rating || null

export const externalScore = (item) => {
  const rating = externalRating(item)
  if (!rating || !Number(rating.scale)) return null
  return Number(rating.normalized_score ?? (Number(rating.score) / Number(rating.scale) * 5))
}

export const externalReviewCount = (item) => Number(externalRating(item)?.review_count || 0)
// 已保存的评论数和平台累计评价数是两回事。
export const storedReviewCount = (item) => Number(item?.stored_review_count || 0)
export const externalProvider = (item) => externalRating(item)?.provider || 'External source'
export const externalCountLabel = (item) => (
  externalRating(item)?.count_kind === 'rating_votes' || externalRating(item)?.provider === 'Yandex Maps'
) ? 'ratings' : 'reviews'
export const externalSourceUrl = (item) => externalRating(item)?.source_url || ''

export const formatScoreNumber = (value) => {
  if (value == null || value === '') return 'Unavailable'
  const score = Number(value)
  if (!Number.isFinite(score)) return 'Unavailable'
  return Number.isInteger(score) ? score.toFixed(1) : String(score)
}

export const formatExternalScore = (item) => formatScoreNumber(externalRating(item)?.score)

export const formatExternalRating = (item) => externalRating(item)
  ? `${formatExternalScore(item)} / ${Number(externalRating(item).scale)}`
  : 'Unavailable'
