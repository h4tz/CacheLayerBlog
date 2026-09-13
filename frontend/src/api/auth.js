import client from './client'

export const authApi = {
  register: (rail, data) =>
    client.post(`/v1/${rail}/auth/register`, data),

  login: (rail, data) =>
    client.post(`/v1/${rail}/auth/login`, data),

  me: (rail) =>
    client.get(`/v1/${rail}/auth/me`),
}
