### 📂 Directory Structure
- `reports/`  
  20 parsed PDF reports saved as JSON file in `_corpus.json`. GRI index predictions and completeness and materiality scores stored in `_final.json` file.

- `taxonomies/`  
  Reporting framework taxonomy in JSON file. Currently only GRI taxonomy has been tested. You can add a new reporting taxonomy following the structure of `gri_taxonomy_full_new.json`.

---

### GRI annotated dataset statistics
We annotated 5 reports manually according to their GRI index.

| Report   | Paragraph-disclosure pair counts |
|----------|-----------|
| Boeing Sustainability Report 2023 | 208  |
| BXP ESG Report 2022 | 117        |
| Mastercard ESG Report 2022 | 153        |
| McKinsey ESG Report 2022 | 123       |
| Paypal Global Impact Report 2022 | 121        |

| GRI Code  | Disclosure | Frequency  |
|----------|-----------|-----|
| GRI 2-1 | Organizational details | 7 |
| GRI 2-2 | Entities included in reporting| 5|
| GRI 2-5 | External assurance        | 11|
| GRI 2-9 | Governance structure and composition        | 46|
| GRI 2-12 | Role of highest governance body in oversseing managing impacts       | 7 |
| GRI 2-13| Delegation of responsibility for managing impacts        | 17|
| GRI 2-14 | Role of the highest governance body in sustainability reporting       | 6|
| GRI 2-15 | Conflict of interests | 3|
| GRI 2-16 | Communication of critical concerns        | 3|
| GRI 2-22 | Statement on sustainable development strategy        | 8|
| GRI 2-23 | Policy commitments        | 26|
| GRI 2-24 | Embedding policy commitments        | 28|
| GRI 2-25 | Processes to remediate negative impacts        | 11|
| GRI 2-26 | Mechanisms for seeking advice and raising concerns        | 4|
| GRI 2-27 | Compliance with laws and regulations        | 15|
| GRI 2-28 | Membership associations        | 9|
| GRI 2-29 | Approach to stakeholder engagement        | 21|
| GRI 201-1 | Direct economic value generated and distributed        | 15|
| GRI 201-2 | Financial implications and other risks and opportunities due to climate change        | 43|
| GRI 301-1 | Materials used by weight or volume        | 9|
| GRI 301-2 | Recycled input materials used        | 2|
| GRI 302-1 | Energy consumption within the organization        | 20|
| GRI 302-2 | Energy consumption outside of the organization        | 7|
| GRI 302-3 | Energy intensity        | 7|
| GRI 302-4 | Reduction of energy consumption        | 26|
| GRI 302-5 | Reductions in energy requirements of products and services        | 26|
