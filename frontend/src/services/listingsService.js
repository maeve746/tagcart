import { MOCK_LISTINGS } from '../data/mockListings'

const LISTINGS_KEY = 'tagcart.mock.listings.v2'
const HISTORY_KEY = 'tagcart.mock.history.v2'
const EVENT_NAME = 'tagcart:listings-changed'
const wait = (ms = 250) => new Promise((resolve) => setTimeout(resolve, ms))

/**
 * @typedef {'Draft'|'Processing'|'Review'|'Approved'|'Exported'} ListingStatus
 * @typedef {{name:string,value:string,confidence:number,evidence:string}} ExtractedAttribute
 * @typedef {{id:string,name:string,category:string,status:ListingStatus,createdAt:string,sku:string,price:number,
 * channels:string[],completion:number,description:string,caption:string,hashtags:string[],image?:string,
 * analysis:{category:string,confidence:number,attributes:ExtractedAttribute[],warnings:string[],summary:string},
 * content:{title:string,bullets:string[],description:string,keywords:string[]},approvedAt?:string,
 * versions:Array<{id:string,createdAt:string,reason:string,status:ListingStatus,snapshot:object}>}} Listing
 *
 * LOCAL MOCK REPOSITORY — persistence and analysis are simulated. Replace this module with
 * HTTP calls to FastAPI; components only depend on this public API.
 */

function inferMaterial(name) {
  const text = name.toLowerCase()
  if (text.includes('linen')) return 'Linen blend'
  if (text.includes('ceramic') || text.includes('stoneware')) return 'Ceramic'
  if (text.includes('oak')) return 'Solid oak'
  if (text.includes('walnut')) return 'Walnut wood'
  if (text.includes('wool')) return 'Wool'
  if (text.includes('canvas') || text.includes('cotton')) return 'Cotton'
  if (text.includes('glass')) return 'Glass'
  return 'Natural fiber'
}

function normalize(listing) {
  const attributes = listing.analysis?.attributes?.length ? listing.analysis.attributes : [
    { name: 'Material', value: inferMaterial(listing.name), confidence: 91, evidence: `Visible texture and wording in “${listing.name}”.` },
    { name: 'Color', value: 'Natural', confidence: 84, evidence: 'Dominant neutral tone in the supplied product image.' },
    { name: 'Style', value: 'Contemporary', confidence: 79, evidence: 'Clean form and minimal decorative treatment.' },
  ]
  const bullets = listing.content?.bullets?.length ? listing.content.bullets : [
    `Thoughtfully made ${listing.category.toLowerCase()} essential`,
    'Designed for reliable everyday use',
    'Clean, versatile finish complements modern spaces',
    'Easy to care for and simple to style',
  ]
  return {
    caption: listing.caption || listing.description,
    hashtags: listing.hashtags || ['handmade', 'modernliving', listing.category.toLowerCase().replaceAll(' ', '')],
    analysis: { category: listing.analysis?.category || listing.category, confidence: listing.analysis?.confidence || 88, attributes, warnings: listing.analysis?.warnings || (listing.completion < 70 ? ['Dimensions could not be confirmed from the image.', 'Add a specific material before approval.'] : []), summary: listing.analysis?.summary || 'Simulated analysis based on the uploaded image and seller caption.' },
    content: { title: listing.content?.title || listing.name, bullets, description: listing.content?.description || listing.description, keywords: listing.content?.keywords || [listing.category.toLowerCase(), 'quality', 'everyday', 'modern'] },
    versions: listing.versions || [],
    ...listing,
  }
}

function readListings() {
  try { const saved = JSON.parse(localStorage.getItem(LISTINGS_KEY)); if (Array.isArray(saved)) return saved.map(normalize) } catch { /* fall through */ }
  const seeded = MOCK_LISTINGS.map((item) => { const listing = normalize(item); listing.versions = [snapshot(listing, 'Imported sample')]; return listing })
  localStorage.setItem(LISTINGS_KEY, JSON.stringify(seeded))
  return seeded
}

function writeListings(listings) { localStorage.setItem(LISTINGS_KEY, JSON.stringify(listings)); window.dispatchEvent(new Event(EVENT_NAME)) }
function readHistory() {
  try { const value = JSON.parse(localStorage.getItem(HISTORY_KEY)); if (Array.isArray(value)) return value } catch { /* fall through */ }
  const seed = MOCK_LISTINGS.slice(0, 7).map((item, index) => ({ id: `EV-SEED-${index}`, listingId: item.id, listingName: item.name, action: index < 2 ? 'Exported listing' : 'Status updated', detail: index < 2 ? 'Export package prepared' : `Moved to ${item.status}`, status: item.status, createdAt: `${item.createdAt}T10:30:00.000Z` }))
  localStorage.setItem(HISTORY_KEY, JSON.stringify(seed)); return seed
}
function recordEvent(listing, action, detail) { const history = readHistory(); history.unshift({ id: `EV-${Date.now()}`, listingId: listing.id, listingName: listing.name, action, detail, status: listing.status, createdAt: new Date().toISOString() }); localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 100))) }
function snapshot(listing, reason) { return { id: `v${(listing.versions?.length || 0) + 1}`, createdAt: new Date().toISOString(), reason, status: listing.status, snapshot: { name: listing.name, category: listing.category, analysis: listing.analysis, content: listing.content } } }

async function update(id, changes, action = 'Listing updated') {
  await wait(); const listings = readListings(); const index = listings.findIndex((item) => item.id === id)
  if (index < 0) throw new Error('Listing not found')
  const next = normalize({ ...listings[index], ...changes }); next.versions = [...(next.versions || []), snapshot(next, action)]; listings[index] = next
  writeListings(listings); recordEvent(next, action, `${next.name} saved as ${next.status}`); return structuredClone(next)
}

export const listingsService = {
  subscribe(callback) { window.addEventListener(EVENT_NAME, callback); return () => window.removeEventListener(EVENT_NAME, callback) },
  async getAll() { await wait(360); return structuredClone(readListings()) },
  async getById(id) { await wait(220); const listing = readListings().find((item) => item.id === id); if (!listing) throw new Error('Listing not found'); return structuredClone(listing) },
  async create(input) {
    await wait(420); const id = `TC-${Math.floor(1100 + Math.random() * 8000)}`
    const listing = normalize({ id, name: input.name || 'Untitled product', category: 'Uncategorized', status: 'Draft', createdAt: new Date().toISOString().slice(0, 10), sku: input.sku || `SKU-${id.slice(3)}`, price: Number(input.price) || 0, channels: [], completion: 35, description: input.caption, caption: input.caption, hashtags: input.hashtags, image: input.image, analysis: { category: '', confidence: 0, attributes: [], warnings: [], summary: '' }, content: { title: input.name, bullets: [], description: input.caption, keywords: input.hashtags } })
    listing.versions = [snapshot(listing, 'Draft created')]; writeListings([listing, ...readListings()]); recordEvent(listing, 'Draft created', 'Product image and seller context saved'); return structuredClone(listing)
  },
  update,
  // SIMULATED AI: deterministic mock result; no image or text is sent to an AI service.
  async runSimulatedAnalysis(id) {
    await wait(1100); const listing = await this.getById(id); const category = listing.category === 'Uncategorized' ? 'Home & Living' : listing.category
    return update(id, { status: 'Review', category, completion: 82, analysis: { category, confidence: 89, summary: 'Simulated analysis inferred likely merchandising details from the seller-provided image and caption.', attributes: [
      { name: 'Material', value: 'Natural woven fiber', confidence: 92, evidence: 'Visible interlaced texture in the uploaded image.' },
      { name: 'Color', value: 'Warm natural', confidence: 95, evidence: 'Dominant tan and beige pixels across the product surface.' },
      { name: 'Shape', value: 'Rectangular', confidence: 86, evidence: 'Outer silhouette has four defined corners.' },
      { name: 'Use case', value: 'Home organization', confidence: 78, evidence: 'Open-top container form suggests storage use.' },
    ], warnings: ['Exact dimensions are missing.', 'Confirm care instructions before approval.'] }, content: { title: listing.name, bullets: ['Handwoven natural-fiber construction', 'Structured handles make carrying simple', 'Versatile storage for shelves or entryways', 'Warm neutral finish complements modern interiors'], description: listing.caption || listing.description, keywords: [...new Set([...listing.hashtags, 'woven storage', 'home organization'])] } }, 'Simulated analysis completed')
  },
  // SIMULATED AI regeneration: cycles controlled copy variants locally.
  async regenerate(id) { const listing = await this.getById(id); const count = listing.versions?.filter((item) => item.reason.includes('regenerated')).length || 0; const prefixes = ['Artisan', 'Everyday', 'Modern']; return update(id, { content: { ...listing.content, title: `${prefixes[count % prefixes.length]} ${listing.name}`, bullets: listing.content.bullets.map((bullet, index) => index === 0 ? `${bullet} with a refined, seller-ready finish` : bullet) } }, 'Listing copy regenerated (simulated)') },
  async approve(id, content) { const listing = await this.getById(id); return update(id, { status: 'Approved', completion: 100, approvedAt: new Date().toISOString(), content: content || listing.content }, 'Seller approved listing') },
  async markExported(id, format) { const listing = await this.getById(id); if (!listing.approvedAt && listing.status !== 'Approved' && listing.status !== 'Exported') throw new Error('Seller approval is required before export.'); return update(id, { status: 'Exported', completion: 100 }, `Exported ${format.toUpperCase()}`) },
  async getHistory() { await wait(280); return structuredClone(readHistory()) },
  async getVersions(id) { const listing = await this.getById(id); return structuredClone(listing.versions || []) },
  resetMockData() { localStorage.removeItem(LISTINGS_KEY); localStorage.removeItem(HISTORY_KEY); window.dispatchEvent(new Event(EVENT_NAME)) },
}
