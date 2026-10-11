import sys
import pyperclip
from memory_manager import generate_context_prompt
from chat_cleaner import ingest_raw_conversation

def copy_context():
    """Copies the compact context prompt to the clipboard."""
    prompt = generate_context_prompt()
    pyperclip.copy(prompt)
    print("\n[Success] Context prompt copied to clipboard!")
    print("Now go directly to gemini.google.com and press Ctrl + V.\n")

def save_from_clipboard(category="chat_notes", importance=3):
    """Retrieves the current text from the clipboard and ingests it into memory."""
    raw_text = pyperclip.paste()
    if not raw_text.strip():
        print("\n[Error] Clipboard is empty. Please copy some text first.")
        return

    print("\n[Processing] Ingesting text from clipboard...")
    ingest_raw_conversation(raw_text, category=category, default_importance=importance)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python clipboard_bridge.py copy   -> Copies context to clipboard")
        print("  python clipboard_bridge.py save   -> Saves clipboard text to memory")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "copy":
        copy_context()
    elif action == "save":
        # Optional category parameter support: e.g. python clipboard_bridge.py save technical
        cat = sys.argv[2] if len(sys.argv) > 2 else "chat_notes"
        save_from_clipboard(category=cat)
    else:
        print(f"[Error] Unknown command: '{action}'. Use 'copy' or 'save'.")