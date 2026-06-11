import { describe, it, expect, vi, beforeEach } from 'vitest'

// --- API helper tests ---

describe('API Helper: getPlatformRate', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('should fetch a single platform rate by name', async () => {
    const mockRate = {
      platform: 'Kredivo',
      avg_rate: 2.5,
      common_type: 'monthly',
      sample_count: 42,
      confidence: 0.85,
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockRate),
    } as Response)

    // Dynamic import to pick up mocked fetch
    const { getPlatformRate } = await import('@/lib/api')
    const result = await getPlatformRate('Kredivo')

    expect(result).toEqual(mockRate)
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/platforms/rates/suggest?platform=Kredivo',
      expect.any(Object)
    )
  })

  it('should return null on fetch failure', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

    const { getPlatformRate } = await import('@/lib/api')
    const result = await getPlatformRate('Kredivo')
    expect(result).toBeNull()
  })

  it('should encode platform names with special characters', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(null),
    } as Response)

    const { getPlatformRate } = await import('@/lib/api')
    await getPlatformRate('Shopee PayLater')

    const url = (global.fetch as any).mock.calls[0][0]
    expect(url).toContain('platform=Shopee%20PayLater')
  })
})

describe('API Helper: getAllPlatformRates', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('should fetch all platform rates', async () => {
    const mockRates = [
      { platform: 'Kredivo', avg_rate: 2.5, common_type: 'monthly', sample_count: 42, confidence: 0.85 },
      { platform: 'Akulaku', avg_rate: 3.0, common_type: 'monthly', sample_count: 30, confidence: 0.75 },
    ]

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockRates),
    } as Response)

    const { getAllPlatformRates } = await import('@/lib/api')
    const result = await getAllPlatformRates()

    expect(result).toEqual(mockRates)
    expect(result).toHaveLength(2)
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/platforms/rates',
      expect.any(Object)
    )
  })

  it('should return empty array when no rates exist', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    } as Response)

    const { getAllPlatformRates } = await import('@/lib/api')
    const result = await getAllPlatformRates()
    expect(result).toEqual([])
  })
})

// --- Formatting/parsing helper tests ---

describe('Utility: cn (className merge)', () => {
  it('should merge class names', async () => {
    const { cn } = await import('@/lib/utils')
    const result = cn('px-4', 'py-2', 'bg-red-500')
    expect(result).toContain('px-4')
    expect(result).toContain('py-2')
  })

  it('should handle conditional classes', async () => {
    const { cn } = await import('@/lib/utils')
    const result = cn('base', false && 'hidden', true && 'visible')
    expect(result).toContain('base')
    expect(result).not.toContain('hidden')
    expect(result).toContain('visible')
  })
})

describe('Platform constants', () => {
  it('should export the PLATFORMS array', async () => {
    const { PLATFORMS } = await import('@/lib/platforms')
    expect(Array.isArray(PLATFORMS)).toBe(true)
    expect(PLATFORMS.length).toBeGreaterThan(10)
    expect(PLATFORMS).toContain('Kredivo')
    expect(PLATFORMS).toContain('Shopee PayLater')
    expect(PLATFORMS).toContain('Lainnya')
  })

  it('should export the CATEGORIES array with correct shape', async () => {
    const { CATEGORIES } = await import('@/lib/platforms')
    expect(Array.isArray(CATEGORIES)).toBe(true)
    CATEGORIES.forEach((cat) => {
      expect(cat).toHaveProperty('value')
      expect(cat).toHaveProperty('label')
    })
    expect(CATEGORIES.find((c) => c.value === 'paylater')?.label).toBe('Paylater')
  })
})
