// Clearly labeled temporary data. Replace via listingsService when FastAPI is available.
export const WORKFLOW_STATUSES = ['Draft', 'Processing', 'Review', 'Approved', 'Exported']

export const MOCK_LISTINGS = [
  { id: 'TC-1048', name: 'Handwoven Storage Basket', category: 'Home & Living', status: 'Review', createdAt: '2026-10-20', sku: 'HOM-BAS-048', price: 48, channels: ['Shopify'], completion: 82, description: 'Natural seagrass basket with reinforced handles, designed for shelves and entryways.' },
  { id: 'TC-1047', name: 'Linen Blend Overshirt', category: 'Apparel', status: 'Processing', createdAt: '2026-10-20', sku: 'APP-OVE-047', price: 76, channels: [], completion: 64, description: 'Relaxed linen-blend overshirt with corozo buttons and two utility pockets.' },
  { id: 'TC-1046', name: 'Ceramic Pour-Over Set', category: 'Kitchen', status: 'Approved', createdAt: '2026-10-18', sku: 'KIT-POU-046', price: 62, channels: ['Amazon', 'Shopify'], completion: 100, description: 'Two-piece glazed ceramic coffee dripper and carafe set.' },
  { id: 'TC-1045', name: 'Everyday Canvas Tote', category: 'Accessories', status: 'Exported', createdAt: '2026-10-17', sku: 'ACC-TOT-045', price: 34, channels: ['Etsy'], completion: 100, description: 'Heavyweight cotton canvas tote with internal pocket and reinforced shoulder straps.' },
  { id: 'TC-1044', name: 'Oak Desk Organizer', category: 'Office', status: 'Draft', createdAt: '2026-10-15', sku: 'OFF-ORG-044', price: 55, channels: [], completion: 38, description: 'Solid oak desktop tray for pens, notes, and everyday work tools.' },
  { id: 'TC-1043', name: 'Ribbed Glass Vase', category: 'Home & Living', status: 'Exported', createdAt: '2026-10-14', sku: 'HOM-VAS-043', price: 42, channels: ['Shopify'], completion: 100, description: 'Translucent ribbed glass vase with a softly tapered silhouette.' },
  { id: 'TC-1042', name: 'Wool Travel Pouch', category: 'Accessories', status: 'Approved', createdAt: '2026-10-12', sku: 'ACC-POU-042', price: 29, channels: [], completion: 100, description: 'Compact felted-wool organizer for cables and travel essentials.' },
  { id: 'TC-1041', name: 'Stoneware Serving Bowl', category: 'Kitchen', status: 'Review', createdAt: '2026-10-10', sku: 'KIT-BOW-041', price: 58, channels: [], completion: 91, description: 'Wide stoneware serving bowl finished in a warm speckled glaze.' },
  { id: 'TC-1040', name: 'Cotton Lounge Throw', category: 'Home & Living', status: 'Draft', createdAt: '2026-10-08', sku: 'HOM-THR-040', price: 68, channels: [], completion: 24, description: 'Soft woven cotton throw with hand-knotted fringe.' },
  { id: 'TC-1039', name: 'Walnut Phone Stand', category: 'Office', status: 'Processing', createdAt: '2026-10-06', sku: 'OFF-PHO-039', price: 36, channels: [], completion: 55, description: 'Angled solid-walnut stand with a cable pass-through.' },
]
