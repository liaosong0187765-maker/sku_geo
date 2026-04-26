import type {
  Company, CompanyConfig
} from '@/interfaces/company'
import ky from 'ky'
import type { MonitoredPrompt } from '@/interfaces/monitored_prompt'

const prefix = '/api/v1/companies'

export async function createCompany(data: Omit<Company, 'id' | 'account_id' | 'created_at' | 'updated_at'>) {
  return ky.post<Company>(`${prefix}/`, {
    json: data,
  }).json()
}
  
export async function getCompanies() {
  return ky.get<Company[]>(`${prefix}/`).json()
}

export async function getCompanyById(id: number) {
  return ky.get<Company>(`${prefix}/${id}`).json()
}

export async function updateCompany(id: number, data: CompanyConfig) {
  return ky.put<Company>(`${prefix}/${id}`, {
    json: data,
  }).json()
}

export async function deleteCompany(id: number) {
  return ky.delete(`${prefix}/${id}`)
}

export async function createPromptSuggestions(companyId: number) {
  return ky.post<MonitoredPrompt[]>(`${prefix}/${companyId}/suggestions/prompts`, {timeout: 120_000})
}

export async function createCompetitorSuggestions(companyId: number) {
  return ky.post<MonitoredPrompt[]>(`${prefix}/${companyId}/suggestions/competitors`, {timeout: 120_000})
}

export async function recrawlCompany(companyId: number) {
  return ky.post(`${prefix}/${companyId}/recrawl`)
}