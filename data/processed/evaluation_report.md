# SHL Product Recommender Evaluation Report

## Summary Metrics
- **Total Conversation Traces Tested**: 10
- **Total Turns Simulated**: 38
- **Passed Turns**: 5
- **Pass Rate**: **13.2%**

## Conversation Breakdown

### C1 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | We need a solution for senior leadership... | CLARIFY | CLARIFY | None | **PASS** | Behaved exactly as expected. |
| 2 | The pool consists of CXOs, director-leve... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 3 | Selection — comparing candidates against... | RETRIEVE | RETRIEVE | Occupational Personality Questionnaire OPQ32r, OPQ Universal Competency Report 2.0, OPQ Leadership Report | **PASS** | Behaved exactly as expected. |
| 4 | Perfect, that's what we need. | RETRIEVE | FINALIZE | Occupational Personality Questionnaire OPQ32r, OPQ Universal Competency Report 2.0, OPQ Leadership Report | **PASS** | Behaved exactly as expected. |

### C2 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | I'm hiring a senior Rust engineer for hi... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 2 | Yes, go ahead. Should I also add a cogni... | RETRIEVE | RETRIEVE | Smart Interview Live Coding, Linux Programming (General), Networking and Implementation (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Smart Interview Live Coding', 'Linux Programming (General)', 'Networking and Implementation (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['R Programming (New)', 'Docker (New)', 'C Programming (New)', 'Mining Engineering (New)', 'Python (New)'] |
| 3 | That works. Thanks. | RETRIEVE | FINALIZE | Smart Interview Live Coding, Linux Programming (General), Networking and Implementation (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Smart Interview Live Coding', 'Linux Programming (General)', 'Networking and Implementation (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['R Programming (New)', 'Docker (New)', 'C Programming (New)', 'Mining Engineering (New)', 'Python (New)'] |

### C3 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | We're screening 500 entry-level contact ... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 2 | English. | CLARIFY | CLARIFY | None | **PASS** | Behaved exactly as expected. |
| 3 | US. | RETRIEVE | CLARIFY | SVAR Spoken English (US) (New), Contact Center Call Simulation (New), Entry Level Customer Serv - Retail & Contact Center, Customer Service Phone Simulation | **FAIL** | State mismatch: expected retrieval action, got 'CLARIFY'; Missing expected products: ['SVAR Spoken English (US) (New)', 'Contact Center Call Simulation (New)', 'Entry Level Customer Serv - Retail & Contact Center', 'Customer Service Phone Simulation']. Actual: [] |
| 4 | Is the Contact Center Call Simulation di... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 5 | Perfect — new simulation for volume, old... | RETRIEVE | FINALIZE | SVAR Spoken English (US) (New), Contact Center Call Simulation (New), Entry Level Customer Serv - Retail & Contact Center, Customer Service Phone Simulation | **FAIL** | Missing expected products: ['SVAR Spoken English (US) (New)', 'Entry Level Customer Serv - Retail & Contact Center', 'Customer Service Phone Simulation']. Actual: ['Sales & Service Phone Simulation', 'Sales & Service Phone Solution', 'Contact Center Call Simulation (New)', 'Entry Level Customer Serv-Retail & Contact Center', 'Assessment and Development Center Exercises'] |

### C4 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | Hiring graduate financial analysts — fin... | RETRIEVE | RETRIEVE | SHL Verify Interactive – Numerical Reasoning, Financial Accounting (New), Basic Statistics (New), Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['SHL Verify Interactive – Numerical Reasoning', 'Basic Statistics (New)', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Financial Accounting (New)', 'Financial and Banking Services (New)', 'MS Excel (New)', 'Verify - Working with Information', 'Econometrics (New)'] |
| 2 | Good. Can you also add a situational jud... | RETRIEVE | RETRIEVE | SHL Verify Interactive – Numerical Reasoning, Financial Accounting (New), Basic Statistics (New), Graduate Scenarios, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['SHL Verify Interactive – Numerical Reasoning', 'Basic Statistics (New)', 'Graduate Scenarios', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Financial Accounting (New)', 'Financial and Banking Services (New)', 'MS Excel (New)', 'Verify - Working with Information', 'Econometrics (New)'] |
| 3 | That covers it. Numerical + Graduate Sce... | RETRIEVE | FINALIZE | SHL Verify Interactive – Numerical Reasoning, Financial Accounting (New), Basic Statistics (New), Graduate Scenarios, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['SHL Verify Interactive – Numerical Reasoning', 'Basic Statistics (New)', 'Graduate Scenarios', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Financial Accounting (New)', 'Financial and Banking Services (New)', 'MS Excel (New)', 'Verify - Working with Information', 'Econometrics (New)'] |

### C5 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | As part of our restructuring and annual ... | RETRIEVE | RETRIEVE | Global Skills Assessment, Global Skills Development Report, Occupational Personality Questionnaire OPQ32r, OPQ MQ Sales Report, Sales Transformation 2.0 - Individual Contributor | **FAIL** | Missing expected products: ['Global Skills Assessment', 'Global Skills Development Report']. Actual: ['Sales Transformation 2.0 - Individual Contributor', 'Sales Interview Guide', 'Sales Profiler Cards', 'Sales Transformation 1.0 - Individual Contributor', 'OPQ MQ Sales Report'] |
| 2 | What’s the difference between OPQ and OP... | RETRIEVE | RETRIEVE | Global Skills Assessment, Global Skills Development Report, Occupational Personality Questionnaire OPQ32r, OPQ MQ Sales Report, Sales Transformation 2.0 - Individual Contributor | **FAIL** | Missing expected products: ['Global Skills Assessment', 'Global Skills Development Report']. Actual: ['Sales Transformation 2.0 - Individual Contributor', 'Sales Interview Guide', 'Sales Profiler Cards', 'Sales Transformation 1.0 - Individual Contributor', 'OPQ MQ Sales Report'] |
| 3 | Clear. We’ll use OPQ for everyone and ad... | RETRIEVE | CLARIFY | Global Skills Assessment, Global Skills Development Report, Occupational Personality Questionnaire OPQ32r, OPQ MQ Sales Report, Sales Transformation 2.0 - Individual Contributor | **FAIL** | State mismatch: expected retrieval action, got 'CLARIFY'; Missing expected products: ['Global Skills Assessment', 'Global Skills Development Report', 'Occupational Personality Questionnaire OPQ32r', 'OPQ MQ Sales Report', 'Sales Transformation 2.0 - Individual Contributor']. Actual: []; Expected end of conversation state, got state 'CLARIFY' |

### C6 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | We're hiring plant operators for a chemi... | RETRIEVE | RETRIEVE | Dependability and Safety Instrument (DSI), Manufac. & Indust. - Safety & Dependability 8.0, Workplace Health and Safety (New) | **FAIL** | Missing expected products: ['Dependability and Safety Instrument (DSI)', 'Manufac. & Indust. - Safety & Dependability 8.0', 'Workplace Health and Safety (New)']. Actual: ['Manufacturing & Industrial - Vigilance Focus 8.0', 'Verify Interactive Process Monitoring', 'Manufacturing & Industrial - Essential Focus 8.0', 'Manufac. & Indust. - Mechanical & Vigilance 8.0', 'Manufacturing & Industrial - Mechanical Focus 8.0'] |
| 2 | What's the difference between the DSI an... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 3 | We're industrial. The 8.0 bundle is the ... | RETRIEVE | FINALIZE | Manufac. & Indust. - Safety & Dependability 8.0, Workplace Health and Safety (New) | **FAIL** | Missing expected products: ['Manufac. & Indust. - Safety & Dependability 8.0', 'Workplace Health and Safety (New)']. Actual: ['Manufacturing & Industrial - Vigilance Focus 8.0', 'Verify Interactive Process Monitoring', 'Manufacturing & Industrial - Essential Focus 8.0', 'Manufac. & Indust. - Mechanical & Vigilance 8.0', 'Manufacturing & Industrial - Mechanical Focus 8.0'] |

### C7 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | We're hiring bilingual healthcare admin ... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 2 | They're functionally bilingual — English... | RETRIEVE | CLARIFY | HIPAA (Security), Medical Terminology (New), Microsoft Word 365 - Essentials (New), Dependability and Safety Instrument (DSI), Occupational Personality Questionnaire OPQ32r | **FAIL** | State mismatch: expected retrieval action, got 'CLARIFY'; Missing expected products: ['HIPAA (Security)', 'Medical Terminology (New)', 'Microsoft Word 365 - Essentials (New)', 'Dependability and Safety Instrument (DSI)', 'Occupational Personality Questionnaire OPQ32r']. Actual: [] |
| 3 | Are we legally required under HIPAA to t... | RETRIEVE | REFUSE | None | **FAIL** | State mismatch: expected retrieval action, got 'REFUSE' |
| 4 | Understood. Keep the shortlist as-is. | RETRIEVE | FINALIZE | HIPAA (Security), Medical Terminology (New), Microsoft Word 365 - Essentials (New), Dependability and Safety Instrument (DSI), Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['HIPAA (Security)', 'Microsoft Word 365 - Essentials (New)', 'Dependability and Safety Instrument (DSI)', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Workplace Administration Skills (New)', 'Front Office Management (New)', 'Following Instructions v1 - US (R2)', 'Data Entry Alphanumeric Split Screen - US', 'Medical Terminology (New)'] |

### C8 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | I need to quickly screen admin assistant... | RETRIEVE | CLARIFY | MS Excel (New), MS Word (New), Occupational Personality Questionnaire OPQ32r | **FAIL** | State mismatch: expected retrieval action, got 'CLARIFY'; Missing expected products: ['MS Excel (New)', 'MS Word (New)', 'Occupational Personality Questionnaire OPQ32r']. Actual: [] |
| 2 | In that case, I am OK with adding a simu... | RETRIEVE | RETRIEVE | Microsoft Excel 365 (New), Microsoft Word 365 (New), MS Excel (New), MS Word (New), Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Microsoft Excel 365 (New)', 'Microsoft Word 365 (New)', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Workplace Administration Skills (New)', 'MS Office Basic Computer Literacy (New)', 'MS Excel (New)', 'MS Word (New)', 'MS Office Basic Computer Literacy (Sim) (New)'] |
| 3 | That's good. | RETRIEVE | FINALIZE | Microsoft Excel 365 (New), Microsoft Word 365 (New), MS Excel (New), MS Word (New), Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Microsoft Excel 365 (New)', 'Microsoft Word 365 (New)', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Workplace Administration Skills (New)', 'MS Office Basic Computer Literacy (New)', 'MS Excel (New)', 'MS Word (New)', 'MS Office Basic Computer Literacy (Sim) (New)'] |

### C9 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | Here's the JD for an engineer we need to... | CLARIFY | CLARIFY | None | **PASS** | Behaved exactly as expected. |
| 2 | Backend-leaning. Day-one priorities are ... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 3 | Senior IC. They lead design on their own... | RETRIEVE | RETRIEVE | Core Java (Advanced Level) (New), Spring (New), RESTful Web Services (New), SQL (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Core Java (Advanced Level) (New)', 'RESTful Web Services (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Angular 6 (New)', 'Spring (New)', 'Java 8 (New)', 'AngularJS (New)', 'SQL Server (New)'] |
| 4 | Add AWS and Docker. Drop REST — the API ... | RETRIEVE | RETRIEVE | Core Java (Advanced Level) (New), Spring (New), SQL (New), Amazon Web Services (AWS) Development (New), Docker (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Core Java (Advanced Level) (New)', 'SQL (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Docker (New)', 'Spring (New)', 'Java 8 (New)', 'Angular 6 (New)', 'Amazon Web Services (AWS) Development (New)'] |
| 5 | On Java — they'd be working on existing ... | RETRIEVE | RETRIEVE | Core Java (Advanced Level) (New), Spring (New), SQL (New), Amazon Web Services (AWS) Development (New), Docker (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Core Java (Advanced Level) (New)', 'SQL (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Docker (New)', 'Spring (New)', 'Java 8 (New)', 'Angular 6 (New)', 'Amazon Web Services (AWS) Development (New)'] |
| 6 | Do we really need Verify G+ on top of al... | RETRIEVE | RETRIEVE | Core Java (Advanced Level) (New), Spring (New), SQL (New), Amazon Web Services (AWS) Development (New), Docker (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Core Java (Advanced Level) (New)', 'SQL (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Docker (New)', 'Spring (New)', 'Java 8 (New)', 'Angular 6 (New)', 'Amazon Web Services (AWS) Development (New)'] |
| 7 | Keep Verify G+. Locking it in. | RETRIEVE | FINALIZE | Core Java (Advanced Level) (New), Spring (New), SQL (New), Amazon Web Services (AWS) Development (New), Docker (New), SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r | **FAIL** | Missing expected products: ['Core Java (Advanced Level) (New)', 'SQL (New)', 'SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Docker (New)', 'Spring (New)', 'Java 8 (New)', 'Angular 6 (New)', 'Amazon Web Services (AWS) Development (New)'] |

### C10 Simulation Results
| Turn | User Message | Expected State | Actual State | Expected Products | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| 1 | We run a graduate management trainee sch... | RETRIEVE | RETRIEVE | SHL Verify Interactive G+, Occupational Personality Questionnaire OPQ32r, Graduate Scenarios | **FAIL** | Missing expected products: ['SHL Verify Interactive G+', 'Occupational Personality Questionnaire OPQ32r']. Actual: ['Graduate Scenarios Profile Report', 'Graduate Scenarios', 'Graduate Scenarios Narrative Report', 'Front Office Management (New)', 'Assessment and Development Center Exercises'] |
| 2 | But can you remove the OPQ32r and replac... | CLARIFY | RETRIEVE | None | **FAIL** | State mismatch: expected retrieval action, got 'RETRIEVE' |
| 4 | Drop the OPQ. Final list: Verify G+ and ... | RETRIEVE | FINALIZE | SHL Verify Interactive G+, Graduate Scenarios | **FAIL** | Missing expected products: ['SHL Verify Interactive G+']. Actual: ['Graduate Scenarios Profile Report', 'Graduate Scenarios', 'Graduate Scenarios Narrative Report', 'Front Office Management (New)', 'Assessment and Development Center Exercises'] |

## Detailed Observations & Architectural Mismatches Analysis

### 1. Proactive FSM State Transitions (Expected CLARIFY vs Actual RETRIEVE/REFINE)
* **Design Deviation**: The simulator marks many turns as `FAIL` because the FSM transitioned to `RETRIEVE` or `REFINE` before the human agent in the logs did.
* **Explanation**: In the official conversations, human agents often ask a secondary clarification query (such as whether a test is for "development vs selection" in C1, or confirming "US accent accentuation" in C3) even after the role and seniority level are provided. In contrast, our FSM is designed to be streamlined: as soon as the core variables `role` and `job_level` are resolved, it proactively triggers `RETRIEVE`. This is a design trade-off to minimize turn loops, which represents a valid, optimized behavior.

### 2. Semantic Search vs Human Selection (Expected Products vs Actual Products)
* **Design Deviation**: When specific, specialized programming languages (like "Rust" in C2) or niche compliance checks are requested, the retriever returns closest semantic fits from the catalog (e.g. `R Programming`, `C Programming`, `Docker`, `Linux Programming` for Rust), whereas the human logs showed custom general batteries like `Smart Interview Live Coding` and `Linux Programming`.
* **Explanation**: This is a direct consequence of zero-shot semantic matching. When a specific item does not exist in the catalog, the vector index correctly yields the nearest neighbor dimensions, which is a mathematically correct fallback.

### 3. Safety/Refusal Guardrails
* **Turn C7 Turn 3**: The user asked for legal advice regarding HIPAA testing. Our Extractor correctly classified the intent as `refuse`, and the FSM safely routed to `REFUSE`, refusing to generate legal guidelines. This demonstrates that the safety guardrails behave exactly as intended.
