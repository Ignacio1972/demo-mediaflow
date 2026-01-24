/**
 * Detecta si el dispositivo es móvil real usando User-Agent
 * No depende del tamaño de viewport (no se afecta por DevTools)
 */
export function isMobileDevice(): boolean {
  if (typeof navigator === 'undefined') return false

  const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera || ''

  // Patrones comunes de dispositivos móviles
  const mobilePatterns = [
    /Android/i,
    /webOS/i,
    /iPhone/i,
    /iPad/i,
    /iPod/i,
    /BlackBerry/i,
    /Windows Phone/i,
    /Opera Mini/i,
    /IEMobile/i,
    /Mobile/i,
  ]

  return mobilePatterns.some(pattern => pattern.test(userAgent))
}
