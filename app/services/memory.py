# app/services/memory.py
memory_store = {}

def save(key, value):
    memory_store[key] = value

def get(key):
    return memory_store.get(key, None)
