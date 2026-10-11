import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def init_memory():
    """Initializes the memory file with the default structure if it does not exist."""
    if not os.path.exists(MEMORY_FILE):
        default_data = {
            "system_config": {
                "max_size_mb": 10.0,
                "user_name": "User"
            },
            "facts": [],
            "active_projects": []
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        print(f"[Init] '{MEMORY_FILE}' created successfully.")

def load_memory():
    """Reads the memory file and returns its content as a dictionary."""
    init_memory()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    """Saves the memory data to the file."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_fact(category, content, importance=3):
    """Appends a new fact or permanent context entry with a unique ID and timestamp."""
    data = load_memory()
    fact_id = len(data["facts"]) + 1
    new_entry = {
        "id": fact_id,
        "category": category,
        "content": content,
        "importance": importance,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "access_count": 0
    }
    data["facts"].append(new_entry)
    save_memory(data)
    print(f"[Added] Fact #{fact_id} saved: {content}")

def generate_context_prompt():
    """Generates a compact context block formatted for pasting into web chat interfaces."""
    data = load_memory()
    
    # Sort facts by importance in descending order
    sorted_facts = sorted(data["facts"], key=lambda x: x["importance"], reverse=True)
    
    lines = ["[SYSTEM MEMORY INJECTION - PERMANENT CONTEXT]"]
    
    if data["active_projects"]:
        lines.append("\nActive Projects:")
        for p in data["active_projects"]:
            lines.append(f"- {p['project_name']}: {p['current_goal']}")
            
    if sorted_facts:
        lines.append("\nKey Facts & Preferences:")
        for f in sorted_facts[:10]:  # Top 10 most important facts
            lines.append(f"- [{f['category'].upper()}] {f['content']}")
            
    lines.append("\n[Use the above context implicitly without reciting it back to me.]\n")
    return "\n".join(lines)

if __name__ == "__main__":
    # Test execution
    init_memory()
    
    # Add sample facts for verification
    add_fact("preference", "Prefers concise, practical code snippets.", importance=5)
    add_fact("tech_stack", "Working with Python 3.10+ on local system.", importance=4)
    
    print("\n--- Generated Context Block ---")
    print(generate_context_prompt())