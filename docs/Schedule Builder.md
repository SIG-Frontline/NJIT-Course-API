# Schedule Builder Data Format
All entries are unmarked arrays, so we have to assign meaning to them just by looking at them.
Here is what the course entry may look like for a given course:
```json
[
    "ACCT115",
    "FUND OF FINANCIAL ACCOUNTING",
    3,
    [
        "ACCT115",
        "002",
        10001,
        "43 \/ 43",
        "Seda, Wilson",
        0,
        0,
        "",
        "FUND OF FINANCIAL ACCOUNTING"
        ,[
            [2,52200,57000,"KUPF 207"],
            [5,52200,57000,"KUPF 207"]
        ]
    ],
    [
        "ACCT115",
        "004",
        10002,
        "43 \/ 43",
        "Lee, Heejae",
        0,
        0,
        "",
        "FUND OF FINANCIAL ACCOUNTING",
        [
            [2,52200,57000,"KUPF 108"],
            [5,52200,57000,"KUPF 108"]
        ]
    ],
    [
        "ACCT115",
        "MSE",
        16071,
        "0 \/ 0",
        null,
        0,
        0,
        "For The Academy for Math Science & Engineering Students Only",
        "FUND OF FINANCIAL ACCOUNTING",
        []
    ]
],
```
The first three elements of the list for a course are course code, course title, and amount of credits, respectively.
Then, the rest of the elements are sections offered for that specific course.

So we can simplify the structure of a course entry as follows:
```json
[
    "COURSE CODE",
    "COURSE TITLE",
    CREDITS,
    [ section 1 ],
    [ section 2 ],
    [ section 3 ],
    ...
]
```

Sections can also be simplified to this structure:
```json
[
    "COURSE CODE",
    "SECTION NUMBER",
    "CRN",
    "SEATS TAKEN / SEATS AVAILABLE",
    "PROFESSOR",
    [Unknown],
    [Unknown],
    "COMMENT / INFO",
    [
        [Meeting Time 1],
        [Meeting Time 2],
        ...
    ]
]
```

Meeting times are defined in individual blocks, defined by the weekday, start time, end time, and room location.
Weekdays are defined as integers, starting at 2 for Monday, to 7 for Saturday:
> Monday = 2
Tuesday = 3
Wednesday = 4
Thursday = 5
Friday = 6
Saturday = 7

Sunday is seemingly never scheduled for classes, but would likely be represented as 1.

Start and end times are defined by the second in the day that they start. This is pretty trivial to convert into a standard time.

The structure of meeting times is as follows:
```json
[
    WEEKDAY,
    START_TIME,
    END_TIME,
    "ROOM XYZ"
]
```