import fs from 'fs'
import path from 'path'
import { SAMPLE_SCAMS } from '../src/lib/sampleScams'
import { GoogleGenAI } from '@google/genai'

const cacheFilePath = path.resolve('src/lib/translations-cache.json')
let cache: Record<string, any> = {}
if (fs.existsSync(cacheFilePath)) {
  try {
    cache = JSON.parse(fs.readFileSync(cacheFilePath, 'utf8'))
  } catch (e) {
    cache = {}
  }
}

const apiKey = process.env.GEMINI_API_KEY
if (!apiKey) {
  console.error('GEMINI_API_KEY is not set')
  process.exit(1)
}

const ai = new GoogleGenAI({ apiKey })

const REGIONAL_LANGS = [
  { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
]

async function run() {
  console.log(`Loaded ${SAMPLE_SCAMS.length} sample scams.`)

  for (const scam of SAMPLE_SCAMS) {
    const titles = scam.title as Record<string, string>
    const summaries = scam.summary as Record<string, string>
    const howItWorks = (scam.howItWorks as Record<string, string[]>).hi || (scam.howItWorks as Record<string, string[]>).en || []
    const redFlags = (scam.redFlags as Record<string, string[]>).hi || (scam.redFlags as Record<string, string[]>).en || []
    const whatToDo = (scam.whatToDo as Record<string, string[]>).hi || (scam.whatToDo as Record<string, string[]>).en || []

    for (const lang of REGIONAL_LANGS) {
      const cacheKey = `${scam.slug}_${lang.code}`

      // Check if already in cache
      if (cache[cacheKey] && cache[cacheKey].title && cache[cacheKey].summary) {
        continue
      }

      // Check if sampleScam already has this language natively
      if (titles[lang.code] && summaries[lang.code]) {
        const nativeHow = (scam.howItWorks as Record<string, string[]>)[lang.code] || howItWorks
        const nativeRed = (scam.redFlags as Record<string, string[]>)[lang.code] || redFlags
        const nativeWhat = (scam.whatToDo as Record<string, string[]>)[lang.code] || whatToDo

        cache[cacheKey] = {
          title: titles[lang.code],
          summary: summaries[lang.code],
          howItWorks: nativeHow,
          redFlags: nativeRed,
          whatToDo: nativeWhat,
        }
        fs.writeFileSync(cacheFilePath, JSON.stringify(cache, null, 2), 'utf8')
        console.log(`[Synced from sample] ${cacheKey}`)
        continue
      }

      console.log(`[Translating via Gemini] ${cacheKey} into ${lang.name}...`)

      const prompt = `You are a specialist Indian cyber safety translator.
Translate the following cyber scam alert into ${lang.name}.
Ensure the translation sounds completely natural, authoritative, and easy for ordinary citizens, elders, and youth in India to understand.

Preserve crucial technical, institutional, and legal terms:
- "1930" (helpline number)
- "cybercrime.gov.in"
- "UPI", "UPI PIN", "QR code", "APK", "AnyDesk", "QuickSupport"
- "WhatsApp", "Skype", "Telegram", "X (Twitter)"
- "CBI", "ED", "Digital Arrest", "FIR", "PIB Fact Check", "MEA", "mea.gov.in"
- "RBI Zero Liability", "BNSS", "Chakshu"

Original Alert Details:
Title: ${titles.hi || titles.en}
Summary: ${summaries.hi || summaries.en}
How it works:
${howItWorks.map((s, i) => `${i + 1}. ${s}`).join('\n')}
Red flags:
${redFlags.map((r, i) => `${i + 1}. ${r}`).join('\n')}
What to do:
${whatToDo.map((w, i) => `${i + 1}. ${w}`).join('\n')}

Respond STRICTLY with valid JSON in this exact structure (no markdown fences, no explanation):
{
  "title": "translated title in ${lang.name}",
  "summary": "translated summary in ${lang.name}",
  "howItWorks": ["step 1", "step 2", "step 3"],
  "redFlags": ["flag 1", "flag 2", "flag 3"],
  "whatToDo": ["step 1", "step 2", "step 3"]
}`

      try {
        const response = await ai.models.generateContent({
          model: 'gemini-3.8-flash',
          contents: prompt,
          config: {
            temperature: 0.2,
            responseMimeType: 'application/json',
          },
        })

        const text = response.text?.trim()
        if (text) {
          const parsed = JSON.parse(text)
          if (parsed && parsed.title && parsed.summary) {
            cache[cacheKey] = {
              title: parsed.title,
              summary: parsed.summary,
              howItWorks: Array.isArray(parsed.howItWorks) && parsed.howItWorks.length > 0 ? parsed.howItWorks : howItWorks,
              redFlags: Array.isArray(parsed.redFlags) && parsed.redFlags.length > 0 ? parsed.redFlags : redFlags,
              whatToDo: Array.isArray(parsed.whatToDo) && parsed.whatToDo.length > 0 ? parsed.whatToDo : whatToDo,
            }
            fs.writeFileSync(cacheFilePath, JSON.stringify(cache, null, 2), 'utf8')
            console.log(`[Cached] ${cacheKey}`)
          }
        }
      } catch (err: any) {
        console.warn(`[Translate Error] ${cacheKey}:`, err.message)
      }

      await new Promise((r) => setTimeout(r, 400))
    }
  }

  console.log('Finished caching translations.')
}

run().catch(console.error)
