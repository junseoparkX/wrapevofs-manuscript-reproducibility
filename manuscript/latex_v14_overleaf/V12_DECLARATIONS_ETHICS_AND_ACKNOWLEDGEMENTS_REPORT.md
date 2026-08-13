# V12 declarations, ethics, and acknowledgements report

## Scope

This update was applied in place to V12. No GA, feature-selection stage, model fitting, held-out evaluation, bootstrap analysis, Bayesian analysis, STABL, BLiP, dataset, or empirical numerical result was rerun or changed.

## Author and declaration decisions

| Item | V12 wording/status | Evidence boundary |
|---|---|---|
| First author | Junseo Park | Confirmed by Junseo Park |
| Corresponding author | Huan Zhong, `huan.zhong@ubc.ca` | Confirmed by Junseo Park; UBC address visible in the supplied correspondence |
| Leonard J. Foster | Supervision; Writing--review & editing | Role supplied by Junseo Park |
| Huan Zhong | Supervision; Project administration; Writing--review & editing | Role and corresponding-author status supplied by Junseo Park |
| Funding | No specific grant supported the WrapEvoFS software development and analyses | Confirmed by Junseo Park; source-cohort funding is separately acknowledged |
| Competing interests | The authors declare no competing interests | Requested by Junseo Park; all-author sign-off remains required |
| Generative AI | ChatGPT coding assistance and grammar editing, human verification, and author responsibility are disclosed concisely in Methods | Nature Communications requires substantive LLM use to be documented in Methods; copy editing alone would not require disclosure |

## Acknowledgement verification

- Selina Parmar's written message confirmed her preferred formal name and willingness to be acknowledged. Junseo Park subsequently clarified that her role was limited to providing the CGGA data used in the study; the acknowledgement now states only that contribution.
- Junseo Park confirmed the formal name Ruihan Xu and clarified that Ruihan Xu provided the ADNI-derived and AMP-AD data used in the study. No documentation or data-preparation role is claimed.

## Ethics and consent correspondence

### ADNI

- ADNI documentation states that each phase uses an IRB-approved protocol.
- The ADNI protocol requires site IRB/REB approval and written informed consent from participants and/or authorized representatives.
- The current ADNI Data Use Agreement requires ADNI acknowledgement on the author line, methods language, funding acknowledgement, and administrative review by the ADNI Data and Publications Committee before journal submission.
- V12 now includes the corporate author-line acknowledgement, methods description, ethics statement, and current U19AG024904 source-data funding statement. To distinguish authorship roles, the three named authors occupy the first byline row and the italicized ADNI corporate acknowledgement occupies a separate row immediately below; the same separation appears on the Supplementary title page.

Official sources:

- https://adni.loni.usc.edu/wp-content/themes/adni_2023/documents/ADNI_Data_Use_Agreement.pdf
- https://adni.loni.usc.edu/help-faqs/faqs/
- https://adni.loni.usc.edu/wp-content/uploads/2017/09/ADNID_Approved_Protocol_11.19.14.pdf

### CGGA

The CGGA resource states that source research was approved by the Beijing Tiantan Hospital IRB, followed the Declaration of Helsinki, obtained written informed consent, and collected specimens under protocol KY2013-017-01. V12 reports those source-cohort facts without asserting a new UBC approval.

Official source: https://www.cgga.org.cn/about.jsp

### AMP-AD

The supplied matrix combines de-identified post-mortem frontal proteomic and metabolomic predictors from Emory, Mayo, Mount Sinai, and Rush. Its four-center composition, 1,388-metabolite block, and frontal-proteomic source correspond to the AMP-AD Diverse Cohorts Study. The study is identified as Synapse study `syn51732482`, with stable data DOI `10.7303/9618093`; the frontal-proteomic source file is `syn55249983`. The source descriptor is Reddy et al., *Alzheimer's & Dementia* 2024, DOI `10.1002/alz.14208`.

The AD Knowledge Portal requires a general portal acknowledgement, a study-specific acknowledgement, and a direct dataset DOI. V12 now contains the general portal statement, the AMP-AD Diverse Cohorts grant acknowledgement, the study DOI/Synapse identifier, and a Data Availability access route. The source descriptor reports institution-specific IRB approval and consent from participants or next of kin; V12 cites that source without inventing a single cross-cohort protocol number. The individual metabolomics file-level Synapse ID could not be recovered from the malformed supplied workbook package, but the stable whole-study DOI covers the identified Diverse Cohorts study and is the required manuscript-level access identifier.

Official and primary sources:

- https://help.adknowledgeportal.org/apd/data-use-acknowledgement
- https://adknowledgeportal.synapse.org/Explore/Studies/DetailsPage/StudyDetails?Study=syn51732482
- https://doi.org/10.7303/9618093
- https://doi.org/10.1002/alz.14208

### Private radiomics

The complete `DICOM_TO_RADIOMICS_END_TO_END_REPORT.pdf` was searched for `ethic`, `consent`, `IRB`, `approval`, and institution-specific approval language. The report documents a PHI-bearing clinical DICOM export, restricted HMAC-based linkage, pseudonymized outputs, and nonredistribution controls, but it does not identify a reviewing REB/IRB, approval/waiver number, or consent basis.

V12 therefore states the documented privacy boundary and explicitly marks the missing source-institution ethics details as a submission requirement. No exemption or waiver is inferred.

## Remaining blockers

1. Private-radiomics REB/IRB and consent/waiver details.
2. All-author approval.
3. ADNI DPC upload and administrative review. The current official IDA route is documented in `ADNI_DPC_SUBMISSION_PACKET.md`; no completed submission is claimed.

The private-radiomics blocker requires source-institution confirmation; `PRIVATE_RADIOMICS_ETHICS_EMAIL_TO_MO.md` provides the exact request. The ADNI blocker requires action through an authorized IDA account.
