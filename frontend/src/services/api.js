import axios from 'axios'

const BASE = '/api'

const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
})

// ── Shops ─────────────────────────────────────────────────────────────────────
export const shopApi = {
  list:        ()             => api.get('/shops/'),
  get:         (id)          => api.get(`/shops/${id}`),
  create:      (data)        => api.post('/shops/', data),
  update:      (id, data)    => api.put(`/shops/${id}`, data),
  delete:      (id)          => api.delete(`/shops/${id}`),
  types:       ()            => api.get('/shops/types'),
  template:    (type)        => api.get(`/shops/types/${type}/template`),
}

// ── Products ──────────────────────────────────────────────────────────────────
export const productApi = {
  list:        (shopId, opts={}) => api.get('/products/', { params: { shop_id: shopId, ...opts } }),
  get:         (id)              => api.get(`/products/${id}`),
  create:      (data)            => api.post('/products/', data),
  update:      (id, data)        => api.put(`/products/${id}`, data),
  delete:      (id)              => api.delete(`/products/${id}`),
  lowStock:    (shopId)          => api.get('/products/low-stock', { params: { shop_id: shopId } }),
  adjustStock: (id, adj)         => api.post(`/products/${id}/adjust-stock?adjustment=${adj}`),
}

// ── Orders ────────────────────────────────────────────────────────────────────
export const orderApi = {
  list:        (shopId, opts={}) => api.get('/orders/', { params: { shop_id: shopId, ...opts } }),
  get:         (id)              => api.get(`/orders/${id}`),
  create:      (data)            => api.post('/orders/', data),
  updateStatus:(id, status)      => api.put(`/orders/${id}/status`, { status }),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  dashboard:   (shopId)         => api.get('/analytics/dashboard', { params: { shop_id: shopId } }),
  salesChart:  (shopId, days=7) => api.get('/analytics/sales-chart', { params: { shop_id: shopId, days } }),
  topProducts: (shopId)         => api.get('/analytics/top-products', { params: { shop_id: shopId } }),
  channels:    (shopId)         => api.get('/analytics/channel-breakdown', { params: { shop_id: shopId } }),
}

// ── WhatsApp ──────────────────────────────────────────────────────────────────
export const waApi = {
  simulate:    (data)           => api.post('/whatsapp/simulate', data),
  parseOrder:  (shopId, msg)    => api.post('/whatsapp/parse-order', null, { params: { shop_id: shopId, message: msg } }),
  send:        (data)           => api.post('/whatsapp/send', data),
}

export default api
