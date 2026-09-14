import api from './api'
import { Fee, FeeCreate, FeeDashboardStats, Payment, PaymentCreate, PaginatedResponse, PaginationParams } from '../types'

export const feesApi = {
  getFees: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Fee>>('/fees', { params }),

  getFee: (id: number) =>
    api.get<Fee>(`/fees/${id}`),

  createFee: (data: FeeCreate) =>
    api.post<Fee>('/fees', data),

  updateFee: (id: number, data: Partial<Fee>) =>
    api.put<Fee>(`/fees/${id}`, data),

  deleteFee: (id: number) =>
    api.delete(`/fees/${id}`),

  getDashboardStats: () =>
    api.get<FeeDashboardStats>('/fees/dashboard'),

  createPayment: (feeId: number, data: PaymentCreate) =>
    api.post<Payment>(`/fees/${feeId}/payments`, data),

  getPayments: (feeId: number) =>
    api.get<Payment[]>(`/fees/${feeId}/payments`),

  getMyFees: () =>
    api.get<Fee[]>('/fees/me/fees'),
}
