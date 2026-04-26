import ky from 'ky'
import type { Company } from '@/interfaces/company'

const prefix = '/api/v1/companies'

export async function getCompetitors(companyId: number) {
  return ky.get<Company[]>(`${prefix}/${companyId}/competitors`).json()
}

export async function addCompetitor(
  companyId: number,
  data: { name: string; website?: string }
) {
  return ky
    .post<Company>(`${prefix}/${companyId}/competitors`, { json: data })
    .json()
}

export async function deleteCompetitor(companyId: number, competitorId: number) {
  return ky.delete(`${prefix}/${companyId}/competitors/${competitorId}`)
}

