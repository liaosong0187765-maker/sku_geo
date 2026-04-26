import ky from 'ky'
import type { MonitoredPrompt } from '@/interfaces/monitored_prompt'
import type { PromptMonitoringItem } from '@/interfaces/prompt_monitoring'
import type { MonitoredPromptRun } from '@/interfaces/monitored_prompt_run'

const prefix = '/api/v1/prompts'

export async function getPrompts(companyId: number) {
  return ky.get<MonitoredPrompt[]>(`${prefix}/${companyId}`).json()
}

export async function addPrompt(
  companyId: number,
  data: { prompt: string; prompt_type: string; target_country?: string }
) {
  return ky
    .post<MonitoredPrompt>(`${prefix}/${companyId}`, { json: data })
    .json()
}

export async function deletePrompt(companyId: number, promptId: number) {
  return ky.delete(`${prefix}/${companyId}/${promptId}`)
}

export async function getPromptMonitoring(
  companyId: number,
  page: number,
  pageSize: number
) {
  const skip = page * pageSize
  return ky
    .get<{ total: number; items: PromptMonitoringItem[] }>(
      `${prefix}/${companyId}/stats`,
      { searchParams: { skip, limit: pageSize } }
    )
    .json()
}

export async function deletePrompts(companyId: number, ids: number[]) {
  return ky.delete(`${prefix}/${companyId}/bulk`, { json: { ids } })
}

export async function setPromptsActive(
  companyId: number,
  ids: number[],
  isActive: boolean
) {
  return ky.patch(`${prefix}/${companyId}/activation`, {
    json: { ids, is_active: isActive },
  })
}

export async function getPrompt(companyId: number, promptId: number) {
  return ky.get<MonitoredPrompt>(`${prefix}/${companyId}/${promptId}`).json()
}

export async function updatePrompt(
  companyId: number,
  promptId: number,
  data: { prompt: string; refresh_interval_seconds: number }
) {
  return ky
    .patch<MonitoredPrompt>(`${prefix}/${companyId}/${promptId}`, { json: data })
    .json()
}

export async function getPromptRuns(
  companyId: number,
  promptId: number,
  page: number,
  pageSize: number
) {
  const skip = page * pageSize
  return ky
    .get<{ total: number; items: MonitoredPromptRun[] }>(
      `${prefix}/${companyId}/${promptId}/runs`,
      { searchParams: { skip, limit: pageSize } }
    )
    .json()
}

export async function getPromptRun(
  companyId: number,
  promptId: number,
  runId: number
) {
  return ky
    .get<MonitoredPromptRun>(
      `${prefix}/${companyId}/${promptId}/runs/${runId}`
    )
    .json()
}

export async function getPromptSuggestions(
  companyId: number,
  guidance: string
) {
  return ky
    .post<string[]>(`${prefix}/${companyId}/suggestions`, {
      json: { guidance },
      timeout: 120_000,
    })
    .json()
}

