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

<img src="https://github.com/aidausmanova/reportGRI/tree/main/frontend/public/counts.png" alt="Annotated disclosure distribution">

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
| GRI 303-1 | Interactions with water as a shared resource        | 19|
| GRI 303-2 | Management of water discharge-related impacts       | 14|
| GRI 303-3 | Water withdrawal       | 16|
| GRI 303-4 | Water discharge        | 2|
| GRI 303-5 | Water consumption        | 3|
| GRI 304-2 | Significant impacts of activities, products and services on biodiversity      | 1|
| GRI 304-3 | Habitats protected or restored     | 5|
| GRI 305-1 | Direct (Scope 1) GHG emissions        | 20|
| GRI 305-2 | Energy indirect (Scope 2) GHG emissions       | 15|
| GRI 305-3 | Other indirect (Scope 3) GHG emissions     | 16|
| GRI 305-4 | GHG emissions intensity      | 6|
| GRI 305-5 | Reduction of GHG emissions       | 23|
| GRI 306-1 | Water discharge by quality and destination       | 4|
| GRI 306-2 | Waste by type and disposal method       | 13|
| GRI 306-3 | Significant spills      | 4|
| GRI 308-1 | New suppliers that were screened using environmental criteria     | 12|
| GRI 308-2 | Negative environmental impacts in the supply chain and actions taken      | 4|
| GRI 401-1 | New employee hires and employee turnover       | 4|
| GRI 401-2 | Benefits provided to full-time employees       | 5|
| GRI 401-3 | Parental leave     | 4|
| GRI 403-1 | Occupational health and safety management system     | 19|
| GRI 403-2 | Hazard identification, risk assessment, and incident investigation      | 6|
| GRI 403-3 | Occupational health services      | 6|
| GRI 403-4 | Worker participation, consultation, and communication on occupational health and safety      | 4|
| GRI 403-5 | Worker training on occupational health and safety     | 7|
| GRI 404-1 | Average hours of training per year per employee       | 7|
| GRI 404-2 | Programs for upgrading employee skills and transition assistance programs      | 31|
| GRI 405-1 | Diversity of governance bodies and employees     | 25|
| GRI 405-2 | Ratio of basic salary and remuneration of women to men    | 3|
| GRI 413-1 | Operations with local community engagement      |11|
| GRI 413-2 | Operations with significant actual and potential negative impacts on local communities   | 1|
| GRI 415-1 | Political contributions      | 1|
| GRI 416-1 | Assessment of the health and safety impacts of product and service categories       | 6|
| GRI 416-2 | Incidents of non-compliance concerning the health and safety impacts of products and services     | 2|
| GRI 418-1 | Substantiated complaints concerning breaches of customer privacy and losses of customer data    |21|
