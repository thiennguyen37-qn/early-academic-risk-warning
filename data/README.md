# Open University Learning Analytics Dataset (OULAD)

## Sources

**Original Owner**

The Open University  
Walton Hall, Milton Keynes, MK7 6AA, United Kingdom  
Contact: Zdenek Zdrahal — zdenek.zdrahal@open.ac.uk

**Donors**

| Name | Affiliation | Email |
|------|-------------|-------|
| Jakub Kuzilek | Knowledge Media Institute, The Open University & CIIRC, CTU in Prague | jakub.kuzilek@gmail.com |
| Martin Hlosta | Knowledge Media Institute, The Open University | martin.hlosta@open.ac.uk |
| Zdenek Zdrahal | Knowledge Media Institute, The Open University & CIIRC, CTU in Prague | zdenek.zdrahal@open.ac.uk |

**Date received:** December 2015

---

## Overview

OULAD contains data about courses, students, and their interactions with the Virtual Learning Environment (VLE) across seven selected courses (modules). Course presentations start in **February** (`B`) and **October** (`J`). All tables are linked via unique identifiers and stored as CSV files.

More info: https://analyse.kmi.open.ac.uk/open_dataset

---

## Dataset Statistics

| Entity | Count |
|--------|------:|
| Students in courses | 32,953 |
| Course presentations | 22 |
| VLE pages | 6,364 |
| VLE log entries | 10,655,280 |
| Registration entries | 32,953 |
| Assessments | 206 |
| Assessment entries | 173,912 |
| **Total attributes** | **43** |

---

## Attribute Information

### `courses.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `code_module` | nominal | — | Identifier code of the module |
| `code_presentation` | nominal | — | Year + semester code (`B` = Feb, `J` = Oct) |
| `length` | integer | days | Duration of the module presentation |

---

### `assessments.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `code_module` | nominal | — | Module the assessment belongs to |
| `code_presentation` | nominal | — | Presentation the assessment belongs to |
| `id_assessment` | integer | — | Unique assessment identifier |
| `assessment_type` | nominal | — | Type of assessment |
| `date` | integer | days | Final submission date, relative to presentation start (day 0) |
| `weight` | integer | % | Weight of the assessment; Exams = 100%, all others sum to 100% |

---

### `vle.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `id_site` | integer | — | Unique identifier of the VLE material |
| `code_module` | nominal | — | Module the material belongs to |
| `code_presentation` | nominal | — | Presentation the material belongs to |
| `activity_type` | nominal | — | Role/type associated with the material |
| `week_from` | integer | week | Week the material is planned to be first used |
| `week_to` | integer | week | Week until which the material is planned to be used |

---

### `studentInfo.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `code_module` | nominal | — | Module the student is registered on |
| `code_presentation` | nominal | — | Presentation the student is registered for |
| `id_student` | integer | — | Unique student identifier |
| `gender` | nominal | — | Student's gender |
| `region` | nominal | — | Geographic region where the student lived during the module |
| `highest_education` | nominal | — | Highest education level on entry |
| `imd_band` | nominal | — | Index of Multiple Deprivation band of the student's location |
| `age_band` | nominal | — | Student's age band |
| `num_of_prev_attempts` | integer | — | Number of times the student has previously attempted this module |
| `studied_credits` | integer | — | Total credits for all modules the student is currently studying |
| `disability` | nominal | — | Whether the student has declared a disability |
| `final_result` | nominal | — | Student's final result in the module presentation |

---

### `studentRegistration.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `code_module` | nominal | — | Module identifier |
| `code_presentation` | nominal | — | Presentation identifier |
| `id_student` | integer | — | Unique student identifier |
| `date_registration` | integer | days | Registration date relative to presentation start (negative = before start) |
| `date_unregistration` | integer | days | Unregistration date relative to presentation start; empty if student completed the course |

---

### `studentAssessment.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `id_assessment` | integer | — | Assessment identifier |
| `id_student` | integer | — | Unique student identifier |
| `date_submitted` | integer | days | Submission date, measured from presentation start |
| `is_banked` | integer | — | Flag indicating the result was transferred from a previous presentation |
| `score` | integer | 0–100 | Student's score; scores below 40 are considered a Fail |

---

### `studentVle.csv`

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `code_module` | nominal | — | Module identifier |
| `code_presentation` | nominal | — | Presentation identifier |
| `id_student` | integer | — | Unique student identifier |
| `id_site` | integer | — | VLE material identifier |
| `date` | integer | days | Date of interaction, measured from presentation start |
| `sum_click` | integer | — | Number of times the student interacted with the material on that day |

---

## Missing Values

Yes — some attributes contain missing values.

---

## Class Distribution (`final_result`)

| Class | Count | % |
|-------|------:|--:|
| Distinction | 3,024 | 9.3% |
| Fail | 7,052 | 21.6% |
| Pass | 12,361 | 37.9% |
| Withdrawn | 10,156 | 31.2% |
| **Total** | **32,593** | **100%** |
