import api from './api'
import { LoginRequest, LoginResponse, User } from '../types'

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data),

  logout: () =>
    api.post('/auth/logout'),

  getMe: () =>
    api.get<User>('/auth/me'),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),

  refreshToken: (refresh_token: string) =>
    api.post<{ access_token: string }>('/auth/refresh', { refresh_token }),
}
