import { MOCK_LISTINGS } from '../data/mockListings'

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// FastAPI integration seam: replace these implementations with fetch('/api/listings').
export const listingsService = {
  async getAll() {
    await wait(420)
    return structuredClone(MOCK_LISTINGS)
  },
  async getById(id) {
    await wait(260)
    const listing = MOCK_LISTINGS.find((item) => item.id === id)
    if (!listing) throw new Error('Listing not found')
    return structuredClone(listing)
  },
}
