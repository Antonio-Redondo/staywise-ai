export function realtorAffiliate(url: string, realtorId?: string) {
  if (!realtorId) return url
  const sep = url.includes("?") ? "&" : "?"
  return `${url}${sep}ref=${realtorId}`
}

export function apartmentsAffiliate(url: string, apartmentsId?: string) {
  if (!apartmentsId) return url
  const sep = url.includes("?") ? "&" : "?"
  return `${url}${sep}cm_mmc=affiliate-${apartmentsId}`
}

export type AffiliateNetwork = 'realtor' | 'apartments' | undefined

export function getAffiliateNetwork(sourceUrl: string, source: string): AffiliateNetwork {
  const normalized = `${sourceUrl} ${source}`.toLowerCase()
  if (normalized.includes('realtor')) return 'realtor'
  if (normalized.includes('apartments')) return 'apartments'
  return undefined
}

export function getAffiliateUrl(sourceUrl: string, network: AffiliateNetwork) {
  if (network === 'realtor') {
    return realtorAffiliate(sourceUrl, process.env.NEXT_PUBLIC_REALTOR_AFFILIATE_ID)
  }
  if (network === 'apartments') {
    return apartmentsAffiliate(sourceUrl, process.env.NEXT_PUBLIC_APARTMENTS_AFFILIATE_ID)
  }
  return sourceUrl
}
