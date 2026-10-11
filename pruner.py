import os
import json
from datetime import datetime
from memory_manager import load_memory, save_memory, MEMORY_FILE

ARCHIVE_FILE = "memory_archive.json"

def get_file_size_mb(filepath):
    """Returns the size of the file in megabytes (MB)."""
    if not os.path.exists(filepath):
        return 0.0
    bytes_size = os.path.getsize(filepath)
    return round(bytes_size / (1024 * 1024), 4)

def check_storage_status():
    """Monitors the storage consumption against the configured limit."""
    data = load_memory()
    max_limit = data.get("system_config", {}).get("max_size_mb", 10.0)
    current_size = get_file_size_mb(MEMORY_FILE)
    
    usage_percent = (current_size / max_limit) * 100
    
    print("\n--- Storage Health Check ---")
    print(f"Current Size : {current_size} MB / {max_limit} MB ({usage_percent:.2f}% used)")
    print(f"Total Facts  : {len(data['facts'])}")
    
    # 80% threshold trigger
    if usage_percent >= 80.0:
        print("\n[WARNING] Storage usage has exceeded 80%! Pruning is recommended.")
    else:
        print("[Status] Storage status is healthy. No urgent cleanup needed.")

def archive_fact(fact_to_archive):
    """Appends a pruned fact to the archive file to preserve historical data."""
    archive_data = []
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
            
    archive_data.append(fact_to_archive)
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, indent=4)

def prune_low_value_facts(max_importance_threshold=2):
    """Interactively identifies and archives low-importance or obsolete facts."""
    data = load_memory()
    facts = data.get("facts", [])
    
    # Candidates for pruning: facts with importance <= threshold
    candidates = [f for f in facts if f.get("importance", 3) <= max_importance_threshold]
    
    if not candidates:
        print(f"\n[Pruning] No facts found with an importance score <= {max_importance_threshold}.")
        return

    print(f"\n[Pruning Candidates Found: {len(candidates)} items]")
    for item in candidates:
        print(f"- ID {item['id']} [{item['category']}]: {item['content']} (Score: {item['importance']})")

    confirm = input("\nDo you want to remove these facts from active memory and move them to archive? (y/n): ").strip().lower()
    
    if confirm == 'y':
        candidate_ids = {c["id"] for c in candidates}
        # Retain facts that are not marked as candidates
        retained = []
        for f in facts:
            if f["id"] in candidate_ids:
                archive_fact(f)
            else:
                retained.append(f)
                
        data["facts"] = retained
        save_memory(data)
        print(f"[Done] {len(candidates)} facts successfully moved to archive. Memory optimized!")
    else:
        print("[Cancelled] Pruning operation skipped.")

if __name__ == "__main__":
    check_storage_status()
    # Test run pruning check
    prune_low_value_facts(max_importance_threshold=2)