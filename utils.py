from pymongo import MongoClient
import openai
import functools
import hashlib
from dotenv import load_dotenv
import os
import json

load_dotenv()

mongo_client = MongoClient(os.environ.get("MONGO_CONNECTION_STRING"))

def cache_to_mongodb(db_name, collection_name):
    global mongo_client
    db = mongo_client[db_name]
    collection = db[collection_name]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on function arguments
            key = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            # Check if the result is already in the cache
            cache_item = collection.find_one({'_id': key})
            if cache_item is not None:
                print("___ Cache Hit ___")
                if 'result' in cache_item:
                    return cache_item['result']
                else:
                    del cache_item['_id']
                    return cache_item

            # Call the function and cache the result
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                result['_id'] = key
                collection.insert_one(result)
                del result['_id']
            else:
                collection.insert_one({'_id': key, 'result': result})

            return result

        return wrapper

    return decorator

def cond_cache_to_mongodb(db_name, collection_name, cond_func):
    global mongo_client
    db = mongo_client[db_name]
    collection = db[collection_name]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on function arguments
            key = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            # Decide whether to use cache based on should_use_cache_func
            use_cache = cond_func(*args, **kwargs)

            if use_cache:
                # Check if the result is already in the cache
                cache_item = collection.find_one({'_id': key})
                if cache_item is not None:
                    if 'result' in cache_item:
                        return cache_item['result']
                    else:
                        del cache_item['_id']
                        return cache_item

            # Call the function
            result = func(*args, **kwargs)

            # Replace existing entry in the cache or create a new one
            if isinstance(result, dict):
                result['_id'] = key
                collection.replace_one({'_id': key}, result, upsert=True)
                del result['_id']
            else:
                collection.replace_one({'_id': key}, {'_id': key, 'result': result}, upsert=True)

            return result

        return wrapper

    return decorator

def cache_to_file(filename):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            # Convert the arguments to a string key
            key = json.dumps(args)

            try:
                # Read the cache file
                with open(filename, 'r') as file:
                    cache = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                cache = {}

            if key in cache:
                # Return the cached result if available
                return json.loads(cache[key])

            result = func(*args)

            # Update the cache with the new result
            cache[key] = json.dumps(result)
            with open(filename, 'w') as file:
                json.dump(cache, file)

            return result

        return wrapper
    return decorator