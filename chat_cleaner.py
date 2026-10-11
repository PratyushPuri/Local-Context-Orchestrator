import re
from difflib import SequenceMatcher
from memory_manager import load_memory, save_memory, add_fact

# 1. Boilerplate phrases jinhe drop karna zaroori hai
IRRELEVANT_PATTERNS = [
    r"^hello.*",
    r"^hi\b.*",
    r"^hey\b.*",
    r"sure,?\s*(i can help with that|here is|let me know).*",
    r"as an ai language model.*",
    r"i hope this helps.*",
    r"let me know if you need anything else.*",
    r"feel free to ask.*",
    r"thank you.*",
    r"you'?re welcome.*",
    r"good (morning|afternoon|evening).*",
]

def clean_raw_text(raw_text):
    """Raw text se unnecessary lines aur formatting noise remove karta hai."""
    lines = raw_text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check agar line boilerplate regex match karti hai
        is_boilerplate = any(re.match(pattern, stripped, re.IGNORECASE) for pattern in IRRELEVANT_PATTERNS)
        if is_boilerplate:
            continue

        # Markdown headers (#) aur extra bullet symbols clean karna
        cleaned_line = re.sub(r"^[#*>\-\d\.\s]+", "", stripped).strip()
        
        # Sirf meaningful length wale sentences retain karna
        if len(cleaned_line) > 15:
            cleaned_lines.append(cleaned_line)

    return cleaned_lines

def is_duplicate(new_text, existing_facts, similarity_threshold=0.75):
    """Check karta hai ki naya fact pehle se stored kisi fact se overly similar toh nahi."""
    for fact in existing_facts:
        ratio = SequenceMatcher(None, new_text.lower(), fact["content"].lower()).ratio()
        if ratio >= similarity_threshold:
            return True, fact["id"]
    return False, None

def ingest_raw_conversation(raw_text, category="general", default_importance=3):
    """Raw text ko process karke unique facts ko memory me save karta hai."""
    data = load_memory()
    extracted_lines = clean_raw_text(raw_text)

    added_count = 0
    duplicate_count = 0

    for line in extracted_lines:
        duplicate_found, matched_id = is_duplicate(line, data["facts"])
        if duplicate_found:
            duplicate_count += 1
            # Optional: duplicate milne par existing fact ka access count badha do
            for f in data["facts"]:
                if f["id"] == matched_id:
                    f["access_count"] = f.get("access_count", 0) + 1
            continue

        # Naya unique fact append karo
        fact_id = len(data["facts"]) + 1
        new_fact = {
            "id": fact_id,
            "category": category,
            "content": line,
            "importance": default_importance,
            "timestamp": "2026-10-11 21:40:00",
            "access_count": 1
        }
        data["facts"].append(new_fact)
        added_count += 1

    save_memory(data)
    print(f"\n[Ingestion Summary]")
    print(f"- Total lines evaluated : {len(extracted_lines)}")
    print(f"- Added unique facts    : {added_count}")
    print(f"- Dropped duplicates    : {duplicate_count}")

if __name__ == "__main__":
    # Test sample conversation dump
    sample_chat_dump = """
    Hello! I can certainly help you with your project setup.
    Sure, here is what we discussed earlier.
    We decided to use Python for the local memory pipeline.
    Prefers concise, practical code snippets.
    We are storing context locally in a JSON file for privacy.
    I hope this helps! Let me know if you need anything else.
    """

    print("Running Raw Ingestion Test...")
    ingest_raw_conversation(sample_chat_dump, category="project_decision", default_importance=4)