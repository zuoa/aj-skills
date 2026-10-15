import { describe, expect, it } from 'vitest'
import { fitCanvas } from '../src/display/fit'

describe('full canvas resolution fitting', () => {
  it.each([
    [1280, 720, 2 / 3], [1366, 768, 768 / 1080], [1920, 1080, 1],
    [2560, 1440, 4 / 3], [3840, 2160, 2], [2560, 1080, 1],
    [1280, 1024, 2 / 3], [1024, 768, 1024 / 1920], [3440, 1440, 4 / 3],
  ])('preserves 16:9 and fits completely into %i × %i', (width, height, scale) => {
    const fit = fitCanvas(1920, 1080, width, height)
    expect(fit.scale).toBeCloseTo(scale)
    expect(fit.width / fit.height).toBeCloseTo(16 / 9)
    expect(fit.left).toBeGreaterThanOrEqual(0)
    expect(fit.top).toBeGreaterThanOrEqual(0)
    expect(fit.left + fit.width).toBeLessThanOrEqual(width + 1e-8)
    expect(fit.top + fit.height).toBeLessThanOrEqual(height + 1e-8)
    expect(fit.left).toBeCloseTo(width - fit.left - fit.width)
    expect(fit.top).toBeCloseTo(height - fit.top - fit.height)
  })
  it('uses configured canvas dimensions rather than a hardcoded aspect ratio', () => {
    expect(fitCanvas(2560, 1080, 1920, 1080)).toEqual({ scale: .75, width: 1920, height: 810, left: 0, top: 135 })
  })
  it.each([0, -1, Infinity, NaN])('rejects invalid dimensions: %s', value => {
    expect(() => fitCanvas(1920, 1080, value, 720)).toThrow(RangeError)
    expect(() => fitCanvas(value, 1080, 1920, 1080)).toThrow(RangeError)
  })
})
