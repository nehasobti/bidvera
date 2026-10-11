import sharp from 'sharp'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="50%" stop-color="#1e1b4b" />
      <stop offset="100%" stop-color="#090d16" />
    </linearGradient>
    <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fbbf24" />
      <stop offset="60%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#d97706" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#f59e0b" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)" />
  <rect width="504" height="504" x="4" y="4" rx="108" fill="none" stroke="#38bdf8" stroke-opacity="0.25" stroke-width="4" />

  <!-- Shield -->
  <g filter="url(#glow)">
    <path d="M256 64 L392 120 C392 260 256 392 256 428 C256 392 120 260 120 120 Z"
          fill="url(#shieldGrad)" />
    <path d="M256 80 L376 130 C376 252 256 370 256 404 C256 370 136 252 136 130 Z"
          fill="none" stroke="#fef3c7" stroke-width="4" stroke-opacity="0.6" />
  </g>

  <!-- Alert / Exclamation Symbol -->
  <g fill="#0f172a">
    <path d="M236 160 H276 L270 290 H242 Z" />
    <circle cx="256" cy="336" r="20" />
  </g>
</svg>`

const publicDir = path.resolve(__dirname, '../public')
fs.writeFileSync(path.join(publicDir, 'icon.svg'), svg)

async function run() {
  await sharp(Buffer.from(svg)).resize(192, 192).png().toFile(path.join(publicDir, 'icon-192.png'))
  await sharp(Buffer.from(svg)).resize(512, 512).png().toFile(path.join(publicDir, 'icon-512.png'))
  await sharp(Buffer.from(svg)).resize(180, 180).png().toFile(path.join(publicDir, 'apple-touch-icon.png'))
  console.log('Icons generated successfully in public/')
}

run().catch(console.error)
