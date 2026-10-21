# TagCart seller dashboard

Responsive React, Vite and Tailwind frontend implementing the TagCart seller listing workflow.

## Run

```bash
npm install
npm run dev
```

Demo sign-in accepts any valid-looking email and a password of at least six characters. This is explicitly simulated authentication; credentials are stored only in browser `localStorage`.

## Implemented workflow

1. Upload and validate a product image, caption and hashtags.
2. Run clearly labelled simulated analysis and edit category/attributes.
3. Edit listing title, bullets, description and keywords.
4. Review warnings and save regenerated copy variants.
5. Approve as the seller before JSON, CSV or Excel export is enabled.
6. Review listing activity and read-only version snapshots.

## API integration seam

`src/services/listingsService.js` documents the listing record shape with JSDoc and owns all mock persistence and simulated AI actions. `authService.js` owns simulated sessions, and `exportService.js` owns client-side downloads. Replace these method bodies with FastAPI calls without changing page components. MongoDB should eventually store listings, analysis evidence and immutable versions.
