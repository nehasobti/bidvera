import fs from 'fs'
import path from 'path'
import pg from 'pg'
import { GoogleGenAI } from '@google/genai'

const cacheFilePath = path.resolve('src/lib/translations-cache.json')
let cache = {}
if (fs.existsSync(cacheFilePath)) {
  try {
    cache = JSON.parse(fs.readFileSync(cacheFilePath, 'utf8'))
  } catch (e) {
    cache = {}
  }
}

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY })

const REGIONAL_LANGS = [
  { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
]

function extractLexicalText(lexicalNode) {
  if (!lexicalNode) return []
  if (typeof lexicalNode === 'string') return [lexicalNode]
  const texts = []
  function walk(node) {
    if (!node) return
    if (node.text && typeof node.text === 'string' && node.text.trim()) {
      texts.push(node.text.trim())
    }
    if (Array.isArray(node.children)) {
      node.children.forEach(walk)
    }
  }
  if (lexicalNode.root) {
    walk(lexicalNode.root)
  } else {
    walk(lexicalNode)
  }
  return texts
}

async function run() {
  const client = new pg.Client({
    connectionString: process.env.DATABASE_URI,
    ssl: { rejectUnauthorized: false },
  })
  await client.connect()

  const postsRes = await client.query("SELECT id, slug FROM scam_posts WHERE status = 'published';")
  const publishedPosts = postsRes.rows

  console.log(`Found ${publishedPosts.length} published scam posts.`)

  for (const post of publishedPosts) {
    const localesRes = await client.query(
      "SELECT * FROM scam_posts_locales WHERE _parent_id = $1 AND _locale = 'hi';",
      [post.id]
    )
    if (localesRes.rows.length === 0) continue
    const hiData = localesRes.rows[0]

    const redFlagsRes = await client.query(
      "SELECT flag FROM scam_posts_red_flags WHERE _parent_id = $1 AND _locale = 'hi' ORDER BY _order ASC;",
      [post.id]
    )
    const redFlags = redFlagsRes.rows.map((r) => r.flag).filter(Boolean)
    const howItWorks = extractLexicalText(hiData.how_it_works)
    const whatToDo = extractLexicalText(hiData.what_to_do)

    for (const lang of REGIONAL_LANGS) {
      const cacheKey = `${post.slug}_${lang.code}`
      if (cache[cacheKey] && cache[cacheKey].title && cache[cacheKey].summary) {
        console.log(`[Cache Hit] ${cacheKey}`)
        continue
      }

      console.log(`[Translating] ${cacheKey} via Gemini 3.8 Flash...`)

      const prompt = `You are an expert Indian cyber safety translator.
Translate the following cyber scam alert into ${lang.name}.
Ensure the translation sounds completely natural, authoritative, and easy for ordinary citizens, elders, and youth in India to understand.

Preserve crucial technical, institutional, and legal terms:
- "1930", "cybercrime.gov.in"
- "UPI", "UPI PIN", "QR code", "APK", "AnyDesk"
- "WhatsApp", "Telegram", "Skype", "X (Twitter)"
- "CBI", "ED", "Digital Arrest", "FIR", "PIB Fact Check", "MEA", "mea.gov.in"

Original Alert Details:
Title: ${hiData.title}
Summary: ${hiData.summary}
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
        const res = await ai.models.generateContent({
          model: 'gemini-3.8-flash',
          contents: prompt,
          config: {
            temperature: 0.2,
            responseMimeType: 'application/json',
          },
        })

        const text = res.text?.trim()
        if (text) {
          const parsed = JSON.parse(text)
          if (parsed.title && parsed.summary) {
            cache[cacheKey] = {
              title: parsed.title,
              summary: parsed.summary,
              howItWorks: parsed.howItWorks || howItWorks,
              redFlags: parsed.redFlags || redFlags,
              whatToDo: parsed.whatToDo || whatToDo,
            }
            fs.writeFileSync(cacheFilePath, JSON.stringify(cache, null, 2), 'utf8')
            console.log(`[Saved] ${cacheKey}`)
          }
        }
      } catch (err) {
        console.error(`[Error] Failed to translate ${cacheKey}:`, err.message)
      }

      // Small delay between calls to be gentle on API limits
      await new Promise((resolve) => setTimeout(resolve, 600))
    }
  }

  await client.end()
  console.log('Finished generating translations cache.')
}

run().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
