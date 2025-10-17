# PDF Catalogue to Supabase Importer

## Overview
This tool extracts product data and images from a catalogue PDF and loads the records into a Supabase table while uploading images to a storage bucket.

## Setup
- **Create virtual environment**
```
python -m venv .venv
.venv\Scripts\activate
```
- **Install dependencies**
```
pip install -r requirements.txt
```
- **Environment variables** (create `.env`):
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SUPABASE_PRODUCTS_TABLE=products
SUPABASE_IMAGES_BUCKET=product_images
DEFAULT_CURRENCY=
CHECKPOINT_PATH=checkpoints/last_page.json
```

## Usage
- **Run import**
```
python -m pdf_catalog_importer.cli --pdf "c:/Users/S2029790/OneDrive - SARS/Pictures/PDFEX/2026 Topmark Catalogue _0108.pdf"
```
- Optional flags:
  - `--env path/to/.env`
  - `--start-page 5`
  - `--end-page 25`
  - `--resume`
  - `--log-level DEBUG`

## Output
- Product rows saved in Supabase table `products`.
- Images stored in bucket `product_images` under `product_code/filename`.
- Checkpoint file written to help resume long imports.

## Notes
- Parser heuristics are tuned for the catalogue layout shown. Review `pdf_catalog_importer/pdf_parser.py` to adjust extraction rules if future catalogues differ.
- Prices are left `NULL` when not provided, per current requirement.

## Web storefront
- **Install dependencies**
```
cd web
npm install
```
- **Environment variables**: create `web/.env.local`
```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```
- **Run dev server**
```
npm run dev -- --host
```
- **Build for production**
```
npm run build
npm run preview
```
