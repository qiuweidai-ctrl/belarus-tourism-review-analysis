import api from './index.js'

// ── Auth ──
export const authAPI = {
  register(data) { return api.post('/auth/register', data) },
  login(data) { return api.post('/auth/login', data) },
  refresh() { return api.post('/auth/refresh') }
}

// ── Users ──
export const usersAPI = {
  me() { return api.get('/users/me') },
  updateMe(data) { return api.put('/users/me', data) },
  getProfile(userId) { return api.get(`/users/${userId}`) }
}

// ── Attractions ──
export const attractionsAPI = {
  list(params = {}) { return api.get('/attractions', { params }) },
  get(id) { return api.get(`/attractions/${id}`) },
  create(data) { return api.post('/attractions', data) },
  update(id, data) { return api.put(`/attractions/${id}`, data) },
  delete(id) { return api.delete(`/attractions/${id}`) },
  categories() { return api.get('/attractions/categories') },
  regions() { return api.get('/attractions/regions') }
}

// ── Reviews ──
export const reviewsAPI = {
  list(params = {}) { return api.get('/reviews', { params }) },
  create(data) { return api.post('/reviews', data) },
  delete(id) { return api.delete(`/reviews/${id}`) },
  voteHelpful(id) { return api.post(`/reviews/${id}/helpful`) },
  stats(attractionId) { return api.get(`/reviews/attraction/${attractionId}/stats`) }
}

// ── Wishlist ──
export const wishlistAPI = {
  list(params = {}) { return api.get('/wishlist', { params }) },
  toggle(data) { return api.post('/wishlist/toggle', data) },
  check(attractionId) { return api.get(`/wishlist/check/${attractionId}`) },
  remove(attractionId) { return api.delete(`/wishlist/${attractionId}`) }
}

// ── Recommendations ──
export const recommendationsAPI = {
  get(params = {}) { return api.get('/recommendations', { params }) },
  predictRating(data) { return api.post('/recommendations/predict-rating', data) }
}

// ── Articles ──
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

// ── Q&A ──
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

// ── Tags & Dimensions ──
export const tagsAPI = {
  list(params = {}) { return api.get('/tags', { params }) },
  create(data) { return api.post('/tags', data) },
  attractionTags(attractionId) { return api.get(`/tags/attraction/${attractionId}`) },
  setAttractionTags(attractionId, data) { return api.post(`/tags/attraction/${attractionId}`, data) },
  ratingDimensions(attractionId, params = {}) { return api.get(`/tags/dimensions/${attractionId}`, { params }) },
  setRatingDimensions(data) { return api.post('/tags/dimensions', data) },
  myRatingDimensions(params = {}) { return api.get('/tags/dimensions/my', { params }) }
}

// ── Admin ──
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
  verifyAttraction(id) { return api.post(`/admin/attractions/${id}/verify`) }
}
