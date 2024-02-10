Special: `$or`, `$and`, `$Nof`
Special Operator Examples:

At least one of the requirements must be met
```json
{ "$or": [
    {  },
    {  }
  ]
}
```

All of the requirements must be met
```json
{ "$and": [
    {  },
    {  }
  ],
}
```

At least N (1) requirements must be met
```json
{ "$Nof": [
    {  },
    {  }
  ],
  "N":1
}
```

Course:
```json
{
  "name":"COURSE101",
  "credits":3,
  "coreq": {},
  "prereq": {} 
}
```


Requisite:
```json
{
  "name":"COURSE101",
  "min_grade": "C" //Assumed C if not present, may be excluded if it is C
}
```
OR
```json
{
  "standing":"Senior, Sophomore, etc."
}
```
The `standing` field is only present for defining restrictions on class standing.
OR
```json
{
  "placement":true
}
```
The `placement` field is only present when defining placement testing; true to indicate that a placement test validates this requirement. Otherwise, it should not be included. Department or Advisor approval should not be represented by this, or at all.
OR
```json
{
  "major":"Computer Science, Digital Design, etc."
}
```
The `major` field is only present for defining restrictions on major.

---
This format does not account for courses being equivalent, and thus that should not be represented.