import ky from 'ky'

const prefix = '/api/v1/companies'

export async function getCrawlStatus(companyId: number) {
  return ky.get<{ status: string }>(`${prefix}/${companyId}/crawl-status`).json()
}

