export interface CanvasFit { scale: number; left: number; top: number; width: number; height: number }

export function fitCanvas(canvasWidth: number, canvasHeight: number, viewportWidth: number, viewportHeight: number): CanvasFit {
  if (![canvasWidth, canvasHeight, viewportWidth, viewportHeight].every(value => Number.isFinite(value) && value > 0)) {
    throw new RangeError('Canvas and viewport dimensions must be finite positive numbers')
  }
  const scale = Math.min(viewportWidth / canvasWidth, viewportHeight / canvasHeight)
  const width = canvasWidth * scale, height = canvasHeight * scale
  return { scale, width, height, left: (viewportWidth - width) / 2, top: (viewportHeight - height) / 2 }
}
