import client from './client'

export const ordersApi = {
  list: (rail, params = {}) =>
    client.get(`/v1/${rail}/orders/`, { params }),

  get: (rail, orderId) =>
    client.get(`/v1/${rail}/orders/${orderId}/`),

  create: (rail, data) =>
    client.post(`/v1/${rail}/orders/`, data),

  updateStatus: (rail, orderId, status) =>
    client.patch(`/v1/${rail}/orders/${orderId}/status/`, { status }),
}
