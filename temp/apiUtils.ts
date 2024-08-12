import { courseCache, type CourseDocument, type ReqTree } from "./mongoClient";

export function check_tree(tree: ReqTree, requisites: string[]) {
    if (tree === null || tree === undefined || tree.length <= 0) {
        return true
    }
    let is_and = tree[0] === '&'

    for (let i = 1; i < tree.length; i++) {
        let is_condition_valid = undefined
        if (typeof tree[i] === 'string') {
            is_condition_valid = requisites.includes(tree[i] as string)
        } else {
            is_condition_valid = check_tree(tree[i] as ReqTree, requisites)
        }

        if (is_and && !is_condition_valid) {
            // Check Failed; condition is AND and one of the courses are not present
            return false
        }
        else if (!is_and && is_condition_valid) {
            // Check Succeeded; condition is OR and one of the courses is present
            return true
        }
        // Other cases:
        // - Condition is AND and one of the courses is present; continue
        // - Condition is OR and one of the courses is not present; continue
    }

    // Cases:
    // - is_and == true; We reach the end of the loop if everything is present; return true
    // - is_and == false; We reach the end of the loop if nothing is present; return false
    return is_and
}

export async function get_static_data(course: string) {
    let static_courses = await courseCache.getCourses()
    
    static_courses = static_courses.filter((item) => item._id == course)
    
    if (static_courses.length < 1) {
        return undefined
    }
    else {
        return static_courses[0]
    }
}

export async function check_prereq(course: string, requisites: string[]) {
    let staticData = await get_static_data(course)
    if (staticData === undefined) {
        // Bias true if we can't find static data
        // Shouldn't really happen regardless
        return true
    }
    
    return check_tree(staticData.tree, requisites)
}