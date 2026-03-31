import os
import shutil
import re

# === CONFIG ===
OUTPUT_DIR = "output"
POSTS_DIR = "_posts"
PAGES_DIR = "_pages"
ASSETS_DIR = "assets/images"

# Créer dossiers si inexistants
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# === UTILS ===

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text

def extract_title(content):
    match = re.search(r"title:\s*[\"']?(.*?)[\"']?\n", content)
    return match.group(1) if match else "post"

def extract_date_from_path(path):
    parts = path.split(os.sep)
    for i, part in enumerate(parts):
        if part.isdigit() and len(part) == 4:  # year
            year = part
            month = parts[i+1] if i+1 < len(parts) else "01"
            return f"{year}-{month}-01"
    return "2025-01-01"

def fix_image_paths(content, local_image_folder):
    def replace(match):
        img = match.group(1)
        filename = os.path.basename(img)
        return f"![](/assets/images/{filename})"
    return re.sub(r"!\[\]\((.*?)\)", replace, content)

def copy_images(src_folder):
    if not os.path.exists(src_folder):
        return
    for file in os.listdir(src_folder):
        src = os.path.join(src_folder, file)
        dst = os.path.join(ASSETS_DIR, file)
        if os.path.isfile(src):
            shutil.copy2(src, dst)

# === TRAITEMENT POSTS ===

posts_path = os.path.join(OUTPUT_DIR, "posts")

for root, dirs, files in os.walk(posts_path):
    for file in files:
        if file == "index.md":
            full_path = os.path.join(root, file)

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            title = extract_title(content)
            slug = slugify(title)
            date = extract_date_from_path(root)

            new_filename = f"{date}-{slug}.md"
            new_path = os.path.join(POSTS_DIR, new_filename)

            # images
            images_folder = os.path.join(root, "images")
            copy_images(images_folder)

            # fix images path
            content = fix_image_paths(content, images_folder)

            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[POST] {new_filename}")

# === TRAITEMENT PAGES ===

pages_path = os.path.join(OUTPUT_DIR, "pages")

for root, dirs, files in os.walk(pages_path):
    for file in files:
        if file == "index.md":
            full_path = os.path.join(root, file)

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            title = extract_title(content)
            slug = slugify(title)

            new_filename = f"{slug}.md"
            new_path = os.path.join(PAGES_DIR, new_filename)

            # images
            images_folder = os.path.join(root, "images")
            copy_images(images_folder)

            # fix images path
            content = fix_image_paths(content, images_folder)

            # ajouter front matter si absent
            if "layout:" not in content:
                header = f"""---
layout: page
title: "{title}"
permalink: /{slug}/
---

"""
                content = header + content

            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[PAGE] {new_filename}")

print("\n✅ Migration terminée avec succès !")