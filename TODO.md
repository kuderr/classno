Features:

- strict/lossless autocasting ?
- shadow attrs in as_dict
- features on fields ?
- can set cached properties if immutable ?
- validate callback on fields?
- cast callback on fields?
- setattrs builder
- process features if methods already set
- raise validation/cast error with ALL errors

Bugs:

- cast/validation recursion
  - i need to traverse mro in setattr functions, or somehow inject them as methods, so super() will do the work
  - also fix init_hook setattr
