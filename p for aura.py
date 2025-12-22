import json
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================

SOURCE_FILE_NAME = 'aura.build.background.json'

# Since most of your items are similar (UnicornStudio/Spline backgrounds),
# we define a default target, but we can check the "description" or "code" 
# to categorize them slightly better if needed.
# For now, based on your previous structures, I'll map them like this:

DEFAULT_TARGET = "backgrounds.json"

# You can add specific keywords to map to different files if you want
# Format: "keyword_in_title_or_code": "target_file.json"
KEYWORD_MAPPING = {
    "Spline": "3d_backgrounds.json",
    "UnicornStudio": "unicorn_backgrounds.json",
    "Unicorn Studio": "unicorn_backgrounds.json",
    "Vanta": "backgrounds.json",
    "Three.js": "webgl_backgrounds.json",
    "Shader": "webgl_backgrounds.json",
    "WebGL": "webgl_backgrounds.json",
    "Tailwind": "tailwind_backgrounds.json", # Only if it explicitly mentions Tailwind in description
    "Particles": "visual_effects.json"
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_json_file(filepath):
    """Loads JSON from a file. Returns empty list if missing/empty."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content: return []
            return json.loads(content)
    except json.JSONDecodeError:
        print(f"  [Warning] '{filepath}' corrupted/invalid. Treating as empty.")
        return []

def save_json_file(filepath, data):
    """Saves data to JSON with pretty printing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def determine_target_file(item):
    """Analyzes title, description, and code to decide where the item goes."""
    text_content = (item.get('title', '') + " " + item.get('description', '') + " " + item.get('code', '')).lower()
    
    # Check specific mappings (order matters, earlier keys prioritize)
    if "spline" in text_content:
        return "3d_backgrounds.json"
    if "three.js" in text_content or "webgl" in text_content or "shader" in text_content:
        return "webgl_backgrounds.json"
    if "unicorn" in text_content:
        return "unicorn_backgrounds.json"
    if "vanta" in text_content or "particles" in text_content:
        return "visual_effects.json"
    
    # Default fallback
    return DEFAULT_TARGET

def distribute():
    print(f"--- Reading {SOURCE_FILE_NAME} ---")

    if not os.path.exists(SOURCE_FILE_NAME):
        print(f"[Error] Source file {SOURCE_FILE_NAME} not found.")
        return

    try:
        with open(SOURCE_FILE_NAME, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return

    # Buffer for new files: { "filename.json": [item1, item2] }
    updates = {}
    
    # Keep track of items remaining in source (in case of skip)
    remaining_in_source = []
    
    processed_count = 0
    duplicate_title_counter = {}

    print(f"--- Processing {len(source_data)} items ---")

    for index, item in enumerate(source_data):
        # 1. Generate a Unique ID
        # Since titles are duplicated, we append a number to make the ID unique
        # We perform a slugify on the title to create a clean ID
        base_title = item.get('title', f'item-{index}')
        clean_key = base_title.lower().replace(' ', '-').replace('/', '-').replace('.', '')
        
        # Handle duplicates logic
        if clean_key in duplicate_title_counter:
            duplicate_title_counter[clean_key] += 1
            unique_id = f"{clean_key}-{duplicate_title_counter[clean_key]}"
        else:
            duplicate_title_counter[clean_key] = 1
            unique_id = clean_key

        # Inject ID into the object
        item['id'] = unique_id

        # 2. Determine where to save
        target_file = determine_target_file(item)

        # 3. Add to buffer
        if target_file not in updates:
            updates[target_file] = []
        
        updates[target_file].append(item)
        processed_count += 1
        
        # Log logic (condensed for speed, enables specific logs if uncommented)
        # print(f"Processing: {unique_id} -> {target_file}")

    # ==========================================
    # 3. WRITE TO TARGET FILES
    # ==========================================
    print("\n--- Writing Data to Targets ---")
    
    for filename, new_items in updates.items():
        existing_data = load_json_file(filename)
        
        # Merge lists
        combined_data = existing_data + new_items
        
        try:
            save_json_file(filename, combined_data)
            print(f"✅ {filename}: Added {len(new_items)} items.")
        except IOError as e:
            print(f"❌ Error writing {filename}: {e}")
            # If write fails, keep these in source so we don't lose them
            remaining_in_source.extend(new_items)

    # ==========================================
    # 4. UPDATE SOURCE FILE
    # ==========================================
    print("\n--- Cleaning Source File ---")
    
    if len(remaining_in_source) == 0:
        save_json_file(SOURCE_FILE_NAME, [])
        print(f"🎉 Source file '{SOURCE_FILE_NAME}' has been completely emptied!")
    else:
        save_json_file(SOURCE_FILE_NAME, remaining_in_source)
        print(f"⚠️ Source file updated. {len(remaining_in_source)} items remain.")

    print(f"\nTotal Items Processed: {processed_count}")

if __name__ == "__main__":
    distribute()