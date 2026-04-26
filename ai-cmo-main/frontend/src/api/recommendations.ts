import ky from 'ky'
import type { Recommendation, RecommendationListItem } from '@/interfaces/recommendation'

const prefix = '/api/v1/recommendations'

export async function listRecommendations(companyId: number, page: number, pageSize: number) {
  const skip = page * pageSize
  return ky.get<{ total: number; items: RecommendationListItem[] }>(`${prefix}/${companyId}`, { searchParams: { skip, limit: pageSize } }).json()
}

export async function createRecommendation(companyId: number, data: { competitor_domain: string; prompt_ids: number[] }) {
  return ky.post<Recommendation>(`${prefix}/${companyId}`, { json: data }).json()
}

export async function getRecommendation(companyId: number, recId: number) {
  return ky.get<Recommendation>(`${prefix}/${companyId}/${recId}`).json()
}

export async function shareRecommendation(companyId: number, recId: number, data: { email: string; subject: string }) {
  await ky.post(`${prefix}/${companyId}/${recId}/share`, { json: data })
}
