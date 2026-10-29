import api from './index.js'
export const authAPI = {
  register(data) { return api.post('/auth/register', data) },
  login(data) { return api.post('/auth/login', data) },
  refresh() { return api.post('/auth/refresh') },
  logout() { return api.post('/auth/logout') },
  events(params = {}) { return api.get('/auth/events', { params }) }
}
export const usersAPI = {
  me() { return api.get('/users/me') },
  updateMe(data) { return api.put('/users/me', data) },
  uploadAvatar(file) {
    const fd = new FormData()
    fd.append('avatar', file)
    return api.post('/users/me/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getProfile(userId) { return api.get(`/users/${userId}`) }
}
export const attractionsAPI = {
  list(params = {}) { return api.get('/attractions', { params }) },
  get(id) { return api.get(`/attractions/${id}`) },
  create(data) { return api.post('/attractions', data) },
  update(id, data) { return api.put(`/attractions/${id}`, data) },
  delete(id) { return api.delete(`/attractions/${id}`) },
  uploadImage(id, file) {
    const fd = new FormData()
    fd.append('image', file)
    return api.post(`/attractions/${id}/image`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  categories() { return api.get('/attractions/categories') },
  regions() { return api.get('/attractions/regions') }
}
export const reviewsAPI = {
  list(params = {}) { return api.get('/reviews', { params }) },
  create(data) { return api.post('/reviews', data) },
  delete(id) { return api.delete(`/reviews/${id}`) },
  voteHelpful(id) { return api.post(`/reviews/${id}/helpful`) },
  stats(attractionId) { return api.get(`/reviews/attraction/${attractionId}/stats`) }
}
export const wishlistAPI = {
  list(params = {}) { return api.get('/wishlist', { params }) },
  toggle(data) { return api.post('/wishlist/toggle', data) },
  check(attractionId) { return api.get(`/wishlist/check/${attractionId}`) },
  remove(attractionId) { return api.delete(`/wishlist/${attractionId}`) }
}
export const recommendationsAPI = {
  get(params = {}) { return api.get('/recommendations', { params }) },
  predictRating(data) { return api.post('/recommendations/predict-rating', data) }
}
export const articlesAPI = {
  list(params = {}) { return api.get('/articles', { params }) },
  get(id) { return api.get(`/articles/${id}`) },
  create(data) { return api.post('/articles', data) },
  update(id, data) { return api.put(`/articles/${id}`, data) },
  delete(id) { return api.delete(`/articles/${id}`) },
  like(id) { return api.post(`/articles/${id}/like`) },
  comments(id, params = {}) { return api.get(`/articles/${id}/comments`, { params }) },
  addComment(id, data) { return api.post(`/articles/${id}/comments`, data) }
}
export const qaAPI = {
  listQuestions(params = {}) { return api.get('/qa/questions', { params }) },
  getQuestion(id) { return api.get(`/qa/questions/${id}`) },
  createQuestion(data) { return api.post('/qa/questions', data) },
  upvoteQuestion(id) { return api.post(`/qa/questions/${id}/upvote`) },
  answers(questionId, params = {}) { return api.get(`/qa/questions/${questionId}/answers`, { params }) },
  createAnswer(questionId, data) { return api.post(`/qa/questions/${questionId}/answers`, data) },
  upvoteAnswer(id) { return api.post(`/qa/answers/${id}/upvote`) },
  acceptAnswer(id) { return api.post(`/qa/answers/${id}/accept`) }
}
export const tagsAPI = {
  list(params = {}) { return api.get('/tags', { params }) },
  create(data) { return api.post('/tags', data) },
  attractionTags(attractionId) { return api.get(`/tags/attraction/${attractionId}`) },
  setAttractionTags(attractionId, data) { return api.post(`/tags/attraction/${attractionId}`, data) },
  ratingDimensions(attractionId, params = {}) { return api.get(`/tags/dimensions/${attractionId}`, { params }) },
  setRatingDimensions(data) { return api.post('/tags/dimensions', data) },
  myRatingDimensions(params = {}) { return api.get('/tags/dimensions/my', { params }) }
}
export const adminAPI = {
  stats() { return api.get('/admin/stats') },
  users(params = {}) { return api.get('/admin/users', { params }) },
  updateUser(id, data) { return api.put(`/admin/users/${id}`, data) },
  banUser(id) { return api.post(`/admin/users/${id}/ban`) },
  unbanUser(id) { return api.post(`/admin/users/${id}/unban`) },
  reviews(params = {}) { return api.get('/admin/reviews', { params }) },
  hideReview(id) { return api.post(`/admin/reviews/${id}/hide`) },
  approveReview(id) { return api.post(`/admin/reviews/${id}/approve`) },
  attractions(params = {}) { return api.get('/admin/attractions', { params }) },
  toggleFeature(id) { return api.post(`/admin/attractions/${id}/feature`) },
  loginEvents(params = {}) { return api.get('/admin/login-events', { params }) }
}
export const analyticsAPI = {
  overview() { return api.get('/analytics/overview') },
  ratingDistribution() { return api.get('/analytics/rating-distribution') },
  regionDistribution() { return api.get('/analytics/region-distribution') },
  priceAnalysis() { return api.get('/analytics/price-analysis') },
  reviewTrend() { return api.get('/analytics/review-trend') },
  sentimentBreakdown() { return api.get('/analytics/sentiment-breakdown') },
  topAttractions(params = {}) { return api.get('/analytics/top-attractions', { params }) },
  keywords(params = {}) { return api.get('/analytics/keywords', { params }) },
  exportCsv(dataset) { return api.get(`/analytics/export/${dataset}.csv`, { responseType: 'blob' }) }
}
export const algoAPI = {
  getSimilarAttractions(attractionId, params = {}) {
    return api.get(`/algo/similar/${attractionId}`, { params })
  },
  getPersonalRecommendations(params = {}) {
    return api.get('/algo/recommendations/personal', { params })
  },
  getMyCluster() { return api.get('/algo/clustering/my') },
  getClusterDistribution() { return api.get('/algo/clustering/distribution') },
  getClusterUsers(clusterId, params = {}) {
    return api.get(`/algo/clustering/${clusterId}/users`, { params })
  },
  explainCluster(clusterId) {
    return api.get(`/algo/clustering/${clusterId}/explain`)
  },
  retrainClustering() { return api.post('/algo/clustering/retrain') },
  getReviewQuality(reviewId) {
    return api.get(`/algo/quality/${reviewId}`)
  },
  batchCalculateQuality(data = {}) {
    return api.post('/algo/quality/batch', data)
  },
  getTopQualityReviews(attractionId, params = {}) {
    return api.get(`/algo/quality/attraction/${attractionId}/top`, { params })
  },
  getTrending(params = {}) { return api.get('/algo/trending', { params }) },
  getTrendingByCategory(category, params = {}) {
    return api.get('/algo/trending/categories', { params: { category, ...params } })
  },
  getWeeklyTrend(attractionId, params = {}) {
    return api.get(`/algo/trending/${attractionId}/weekly`, { params })
  },
  getCategorizedTrending(params = {}) {
    return api.get('/algo/trending/categorize', { params })
  },
  recalculateTrending() { return api.post('/algo/trending/recalculate') },
  checkDuplicate(data) { return api.post('/algo/duplicate/check', data) },
  findDuplicatePairs(params = {}) {
    return api.get('/algo/duplicate/pairs', { params })
  },
  getUserReviewPattern(userId) {
    return api.get(`/algo/duplicate/user-pattern/${userId}`)
  },
  rebuildDuplicateIndex() { return api.post('/algo/duplicate/rebuild-index') },
  getAttractionSummary(attractionId) {
    return api.get(`/algo/summary/${attractionId}`)
  }
}
