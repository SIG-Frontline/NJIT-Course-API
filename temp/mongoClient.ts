import mongodb from 'mongodb';
import { SCHEDULEBUILDER_DB_URI, BUILDER_NS } from '$env/static/private';
if (!SCHEDULEBUILDER_DB_URI) {
	throw new Error('Missing env variable SCHEDULEBUILDER_DB_URI');
}
export const client = new mongodb.MongoClient(SCHEDULEBUILDER_DB_URI);
await client.connect(); //top level await

// TYPES FOR Sections Collection
/**
 * Represents the days of the week on which a class can meet.
 * Each field is a boolean indicating whether the class meets on that day.
 * NOTE: The data ingestion pipeline is currently bugged for this field.
 */
export interface Days {
    /**
     * Monday
     */
    M: boolean;

    /**
     * Tuesday
     */
    T: boolean;

    /**
     * Wednesday
     */
    W: boolean;

    /**
     * Thursday
     */
    R: boolean;

    /**
     * Friday
     */
    F: boolean;

    /**
     * Saturday
     */
    S: boolean;

    /**
     * Sunday
     */
    U: boolean;
}

/**
 * Represents a scheduled time for a class, including the day, start and end times, and location.
 */
export interface Time {
    /**
     * The day of the week (e.g., "M" for Monday).
     */
    day: string;

    /**
     * The start time of the class.
     */
    start: Date;

    /**
     * The end time of the class.
     */
    end: Date;

    /**
     * The building where the class is held.
     */
    building: string;

    /**
     * The room number where the class is held.
     */
    room: string;
}

/**
 * Represents the summer period during which the course is offered.
 * Can be:
 * - 1: First half of the summer session
 * - 2: Second half of the summer session
 * - 4: Full summer session
 * - null: Not applicable
 */
export type SummerPeriod = 1 | 2 | 4 | null;

/**
 * Represents a section of a course, including all relevant information such as the term, course code, title, schedule, and more.
 */
export interface SectionDocument {
    /**
     * The unique identifier for the section.
     */
    _id: string;

    /**
     * The term code (e.g., "202410" for Fall 2024).
     */
    TERM: string;

    /**
     * The course code (e.g., "ACCT 115").
     */
    COURSE: string;

    /**
     * The title of the course.
     */
    TITLE: string;

    /**
     * The section number (e.g., "002").
     */
    SECTION: string;

    /**
     * The Course Reference Number (CRN).
     */
    CRN: string;

    /**
     * The method of instruction (e.g., "Face-to-Face").
     */
    INSTRUCTION_METHOD: string;

    /**
     * The days on which the class meets.
     */
    DAYS: Days;

    /**
     * The times and locations for the class meetings.
     */
    TIMES: Time[];

    /**
     * The maximum number of students allowed in the class.
     */
    MAX: number;

    /**
     * The current number of students enrolled in the class.
     */
    NOW: number;

    /**
     * The current status of the section (e.g., "Closed").
     */
    STATUS: string;

    /**
     * The name of the instructor for the section.
     */
    INSTRUCTOR: string;

    /**
     * Any additional comments related to the section.
     */
    COMMENTS: string | null;

    /**
     * The number of credits awarded for completing the course.
     */
    CREDITS: number;

    /**
     * A link to additional information or resources for the course.
     */
    INFO_LINK: string;

    /**
     * Indicates whether the section is an honors section.
     */
    IS_HONORS: boolean;

    /**
     * Indicates whether the section is asynchronous.
     */
    IS_ASYNC: boolean;

    /**
     * The subject code for the course (e.g., "ACCT").
     */
    SUBJECT: string;

    /**
     * The level of the course (e.g., 1 for introductory).
     */
    COURSE_LEVEL: number;

    /**
     * The summer period during which the course is offered, if applicable.
     */
    SUMMER_PERIOD: SummerPeriod;
}

// TYPES FOR Course_Static Collection

/**
 * Represents a node in the `tree` structure.
 * Each node can be either a string (course code or operator) or an array of `TreeNode`.
 */
export interface ReqTree extends Array<string | ReqTree> {
    0: '&' | '|';   // The first element is always one of these values, to denote how the requirements should be evaluated
}

/**
 * Represents a document in the `coursesCollection`.
 */
export interface CourseDocument {
    /**
     * Course Code for this specific course (e.g. "BIOL 382")
     */
    _id: string;

    /**
     * The string representation of the course prerequisites.
     */
    prereq_str: string;

    /**
     * A detailed description of the course.
     */
    description: string;

    /**
     * The subject code for the course (e.g., "BIOL").
     */
    subject: string;

    /**
     * The course number (e.g., "382").
     */
    course_number: string;

    /**
     * The prerequisite tree structure, defining logical prerequisites.
     * This can be nested to any depth.
     */
    tree: ReqTree;
}

export const sectionsCollection = client.db(BUILDER_NS).collection<SectionDocument>('Sections');
export const coursesCollection = client.db(BUILDER_NS).collection<CourseDocument>('Course_Static');


class CourseCache {
    private courses: CourseDocument[] = [];
    private lastRetrieved: Date | null = null;

    constructor(private collection: mongodb.Collection<CourseDocument>) {}

    /**
     * Retrieves the list of courses. If the list was last retrieved more than an hour ago, 
     * it refreshes the list from MongoDB.
     * @returns {Promise<CourseDocument[]>} The list of courses.
     */
    async getCourses(): Promise<CourseDocument[]> {
        const now = new Date();
        
        if (!this.lastRetrieved || (now.getTime() - this.lastRetrieved.getTime()) > 3600000) {
            this.lastRetrieved = now;
			this.courses = await this.collection.find().toArray();            
        }

        return this.courses;
    }
}
export const courseCache = new CourseCache(coursesCollection);