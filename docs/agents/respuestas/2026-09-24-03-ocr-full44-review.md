# Final 44-page OCR review

## Result

The full 44-page comparison is complete. PaddleOCR PP-OCRv5 mobile Latin was the preferred engine for the substantive legal text on **44/44 pages**. It preserved resolution identifiers, article references, dates, names, quantities and paragraph order better than either Tesseract run.

This is a comparative QA verdict, not permission to overwrite production OCR.

## Measured run

The same 300 dpi grayscale pages were sent to all engines:

| Engine | Pages | Characters | Runtime | Gate |
|---|---:|---:|---:|---:|
| Tesseract fast PSM 3 | 44 | 68,808 | 341.18 s | 44/44 |
| Tesseract best PSM 3 | 44 | 69,303 | 341.01 s | 44/44 |
| PaddleOCR PP-OCRv5 mobile Latin CPU | 44 | 69,565 | 1,658.26 s | 44/44 |

Paddle is about **4.86x slower** on this document. The quality gain is not cosmetic: Tesseract repeatedly changes legal numerals and terms, including 94/74, 64/44, 39/32, 30/20, GOTO 65/SOTO 5, and tarijeños/torieños.

## Page review

- **Pages 1-4:** Paddle preserves the preamble and identifiers; Tesseract has severe header noise and substitutions such as `pario` and `torieños`. Page 2's date remains a visual-confirmation item.
- **Pages 5-10:** Paddle preserves R.A. 164-169, Arts. 94/105/117, Acta references and `DECLARAR DESIERTA`; Tesseract repeatedly changes 94 to 74 and corrupts legal nouns.
- **Pages 11-19:** Paddle preserves R.A. 170-178, article lists, dates and operative decisions; Tesseract loses or corrupts headings, articles and date lines.
- **Pages 20-21:** Paddle preserves the administrative-law body and the R.A. 179 / R.A. 109 references; Tesseract misreads resolution references and legal vocabulary.
- **Pages 22-29:** Paddle preserves R.A. 180-187, Actas 39/41/42, Arts. 64/94/105/117 and the law-project text; Tesseract damages titles and confuses article numbers.
- **Pages 30-38:** Paddle preserves R.A. 188-194, the Planetario decision, Actas 43/44 and the cultural-honours body; Tesseract alters numbers, names and paragraph content. Page 30's `GOTO 65` and pages 37-38's names still need final visual confirmation before publication.
- **Pages 39-44:** Paddle preserves R.A. 195-200, Arts. 64/88/94/105, Acta 45, the PROSOL decision and APROCA; Tesseract best changes article numbers and damages operative sentences.

## Decision

PaddleOCR is now the candidate engine for the next representative gold set. Do **not** reprocess the national corpus yet: first create an independent character-perfect gold on 120-200 representative pages, calculate real CER/WER, verify every flagged date and numeral visually, and preserve the historical OCR with page-level provenance for every candidate output.

## Evidence

- `docs/agents/evidencia/2026-09-24-03-ocr-full44-review.json`
- `pipeline/benchmark_ocr.py`
- Raw run: `/tmp/ocr-full44/report.json`
- Source PDF SHA-256: `6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784`

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (deployment does not apply; no production change)
Review externo:  no emitido (deuda declarada)
Instrumento:     BRAIN via MUDH Gateway build.run, `/tmp/ocr-full44/report.json`, exit=0
