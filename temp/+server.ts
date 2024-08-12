// Import the sectionsCollection from the mongoClient
import { sectionsCollection } from '$lib/mongoClient';
import { check_prereq, check_tree } from '$lib/apiUtils.js';

// Define an asynchronous GET function that takes a request object as a parameter
export async function GET({ url }) {
	// Initialize an empty query object
	const query = {};
	// Extract the search parameters from the url
	const searchParams = url.searchParams;

	// Check if the search parameters include 'term' and add it to the query
	if (searchParams.has('term')) {
		addIntSearch(query, 'TERM', searchParams.get('term') as string);
	}
	// Repeat the process for other potential search parameters
	if (searchParams.has('course')) {
		addSubstrSearch(query, 'COURSE', searchParams.get('course') as string);
	}
	if (searchParams.has('title')) {
		addSubstrSearch(query, 'TITLE', searchParams.get('title') as string);
	}
	if (searchParams.has('subject')) {
		addSubstrSearch(query, 'SUBJECT', searchParams.get('subject') as string);
	}
	if (searchParams.has('instructor')) {
		addSubstrSearch(query, 'INSTRUCTOR', searchParams.get('instructor') as string);
	}
	if (searchParams.has('honors')) {
		addBooleanSearch(query, 'IS_HONORS', searchParams.get('honors') as string);
	}
	if (searchParams.has('async')) {
		addBooleanSearch(query, 'IS_ASYNC', searchParams.get('async') as string);
	}
	if (searchParams.has('credits')) {
		addIntSearch(query, 'CREDITS', searchParams.get('credits') as string);
	}
	if (searchParams.has('level')) {
		addIntSearch(query, 'COURSE_LEVEL', searchParams.get('level') as string);
	}
	if (searchParams.has('summer')) {
		addIntSearch(query, 'SUMMER_PERIOD', searchParams.get('summer') as string);
	}
	if (searchParams.has('method')) {
		addSubstrSearch(query, 'INSTRUCTION_METHOD', searchParams.get('method') as string);
	}
	// Initialize cursor and totalNumCourses variables
	let cursor, totalNumCourses;
	const pipeline = [
		// aggregate the sections collection
		{ $match: query },
		{ $sort: { COURSE: 1 } },
		{
			$group: {
				_id: '$COURSE',
				sections: { $push: '$$ROOT' }
			}
		}
	];
	try {
		// Attempt to get the sections from the sectionsCollection using the query
		// Limit the results to sectionsPerPage and skip the sections for the previous pages
		cursor = await sectionsCollection
			.aggregate(pipeline)
			.toArray();
		
		if (searchParams.has('requisites') && searchParams.get('requisites') != null) {
			const requisites = (searchParams.get('requisites') as string).split(',');

			const filteredCursor = await Promise.all(
				cursor.map(async (course) => {
					const isValid = await check_prereq(course._id, requisites);
					return isValid ? course : null;  // Return null for invalid courses
				})
			);

			// Filter out null values from the result
			cursor = filteredCursor.filter(course => course !== null) as typeof cursor;
		}
		cursor = cursor.sort((a, b) => {
			if (a._id < b._id) return -1;
			if (a._id > b._id) return 1;
			return 0;
		});

		// Get the total number of documents that match the query
		totalNumCourses = cursor.length
	} catch (e) {
		// Log the error and return a 500 response if there is an error querying the database
		console.error(e);
		return new Response('Error querying database', { status: 500 });
	}
	
	// Return a response with the courses and totalNumCourses in JSON format
	return new Response(JSON.stringify({ courses: cursor, totalNumCourses }), {
		headers: {
			'Content-Type': 'application/json'
		}
	});
}

// Define a function to add a substring search to the query
function addSubstrSearch(
	query: {
		[key: string]: { $regex: string; $options: string };
	},
	key: string,
	value: string
) {
	query[key] = { $regex: `.*${value}.*`, $options: 'i' };
}

// Define a function to add a boolean search to the query
function addBooleanSearch(
	query: {
		[key: string]: { $regex: string; $options: string } | { $eq: boolean };
	},
	key: string,
	value: string
) {
	query[key] = { $eq: value === 'true' };
}

// Define a function to add an integer search to the query
function addIntSearch(
	query: {
		[key: string]: { $regex: string; $options: string } | { $eq: string };
	},
	key: string,
	value: string
) {
	query[key] = { $eq: value };
}
