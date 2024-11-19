Features:

- strict/lossless autocasting ?
- shadow attrs in as_dict
- features on fields ?
- can set cached properties if immutable ?
- validate callback on fields?
- cast callback on fields?
- setattrs builder
- raise validation/cast error with ALL errors
- types for attrs

Bugs:

- process features if methods already set
  - processed features/methods override
- Classno class set None for other classses and features that sets like `Features.ORDER not in features` doesnt work
- set empty **call** method in Classno
