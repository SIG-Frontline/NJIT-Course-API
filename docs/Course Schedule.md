# Course Schedule
## Internal Definitions
The course schedule splits data by term (e.g. Spring 2024) and by subject (e.g. CS)
### Term
Terms are defined as a 6-digit integer, with the first 4 being the year, and the second 2 defining the semester in that year. _(Usually this is passed as a string, but the content is numeric)_

Semesters are defined numerically as follows:

> FALL = 90
SPRING = 10
WINTER = 95
SUMMER = 50

For example, Spring 2024 is represented as `202410`; 2024 being the year, and 10 representing Spring.

### Subject
Subjects are referred to by their course code. "CS 100" falls under the "CS" subject. This applies for Rutgers courses as well, so "R089 104" would be found under the "R089" subject.

------
## Requests
There are two main requests that we are interested in. One to get the subjects with course offerings for a given term (`get_subjects`) and one to get the sections listed under a given subject, for a given term (`get_sections`).

### Encryption
Banner encodes the request parameters of all requests for some reason, even though this is fully public data. This is a pretty simple Base64 encoding, but the twist is that they take a random number from 0-99 _(which will always encode to 4 chars)_, encode it, and add it to the start of the encoded output.

So `202410` encodes to `MjAyNDEw` normally, but then they would pick a random number (let's say 15, which encodes to `MTU=`) and add that to the start, giving us a result of `MTU=MjAyNDEw`.

This process is done on keys and values in the request, which makes the whole thing pretty hard to read and confusing.

Thankfully, this is actually very easy to reverse. Because numbers between 0 and 99 always encode to 4 characters, we can just remove those and then decode the rest normally. _(There is also some fun stuff involving UTF-8 encoding but that's just formatting)_

So we would take `MTU=MjAyNDEw` and remove the first 4 characters, giving us `MjAyNDEw`. Then we would decode this as we would for any Base64 encoding to get our original text of `202410`.

> Sidenote: Check out https://cryptii.com/ if you want to mess around with encoding/decoding, it's pretty fun

### Subjects
The subjects request returns an array of objects that follow this format:
```json
{"ROW_NUMBER":X, "SUBJECT":"EXMPL"}
```
The course schedule takes a maximum of 150 subjects, so we do the same.

### Sections
The sections request returns an array of objects in the following format: 
(This is an example taken from real output)
```json
{
    "ROW_NUMBER": 1,
    "TERM": "202410",
    "COURSE": "CS100",
    "TITLE": "ROADMAP TO COMPUTING",
    "SECTION": "002",
    "CRN": "11654",
    "INSTRUCTION_METHOD": "Face-to-Face",
    "DAYS": "MR",
    "TIMES": "10:00 AM - 11:20 AM",
    "LOCATION": "CKB 204",
    "MAX": "80",
    "NOW": "60",
    "STATUS": "Open",
    "INSTRUCTOR": "Qerimaj, Jertishta",
    "COMMENTS": "This course has common exams.<br />See https://www.njit.edu/registrar/exams/ for details.<br />Students must bring their own device for this section.",
    "CREDITS": 3,
    "INFO_LINK": "https://www.bkstr.com/webapp/wcs/stores/servlet/booklookServlet?bookstore_id-1=584&term_id-1=2024 Spring&crn-1=11654"
}
```
In sections with more complicated schedules, there may be multiple entries for the same section, with different timings. So when trying to get the schedule of a section, you must search the array for all instances of that section. (The CRN is probably the most convenient way to do this)
