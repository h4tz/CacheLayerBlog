import client from './client'

export const productsApi = {
  list: (rail, params = {}) =>
    client.get(`/v1/${rail}/products/`, { params }),

  get: (rail, sku) =>
    client.get(`/v1/${rail}/products/${sku}/`),

  create: (rail, data) =>
    client.post(`/v1/${rail}/products/`, data),

  updateStock: (rail, sku, stock) =>
    client.patch(`/v1/${rail}/products/${sku}/stock/`, { stock }),
}
