# Case 001 — NNC-Kho lessons

Use as reference only for sufficiently similar products: multi-role operational
software, real production data, devices or integrations. Do not copy
project-specific Firebase, Pi or MISA gates into another Mission.

General lessons observed:
- product authority is not technical architecture;
- BUILD COMPLETE is not PRODUCTION READY;
- PRODUCTION READY is not GO-LIVE;
- GO-LIVE is not MISSION COMPLETE;
- production reality should be measured rather than inferred from local tests;
- real-device/user UAT can expose problems unit tests cannot;
- rollback should exist before production mutation;
- freeze/hypercare may be appropriate around a risky release;
- post-live changes should be explicit Delta Missions.

A chatbot, Skill, report or simple configuration may need only a subset.
