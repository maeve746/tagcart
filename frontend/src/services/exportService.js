function download(name, content, type) { const url = URL.createObjectURL(new Blob([content], { type })); const anchor = document.createElement('a'); anchor.href = url; anchor.download = name; anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 500) }
function rows(listing) { return [['ID', listing.id], ['Title', listing.content.title], ['Category', listing.category], ['SKU', listing.sku], ['Price', listing.price], ['Bullets', listing.content.bullets.join(' | ')], ['Description', listing.content.description], ['Keywords', listing.content.keywords.join(', ')]] }
export const exportService = {
  download(listing, format) {
    if (!listing.approvedAt && listing.status !== 'Approved' && listing.status !== 'Exported') throw new Error('Seller approval is required before export.')
    if (format === 'json') download(`${listing.id}.json`, JSON.stringify(listing, null, 2), 'application/json')
    if (format === 'csv') download(`${listing.id}.csv`, rows(listing).map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\n'), 'text/csv')
    if (format === 'excel') { const table = `<table>${rows(listing).map((row) => `<tr><td>${escapeHtml(row[0])}</td><td>${escapeHtml(String(row[1]))}</td></tr>`).join('')}</table>`; download(`${listing.id}.xls`, table, 'application/vnd.ms-excel') }
  },
}
function escapeHtml(value) { return value.replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char])) }
