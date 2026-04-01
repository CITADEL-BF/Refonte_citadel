import os
import shutil
import re

# === CONFIG ===
OUTPUT_DIR = "output"
PAGES_DIR = "_pages"
POSTS_DIR = "_posts"
ASSETS_DIR = "assets/images"

TARGET_PAGES = [
    "Accueil", "Membres", "Missions", 
    "Sujets de recherche", "Publications", 
    "Blog", "Contact", "Formulaire de contact"
]

# Créer dossiers si inexistants
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# === UTILS ===

def long_path(path):
    """Ajoute le préfixe \\?\ pour supporter les chemins longs sur Windows."""
    abs_path = os.path.abspath(path)
    if os.name == 'nt' and not abs_path.startswith('\\\\?\\'):
        return '\\\\?\\' + abs_path
    return abs_path

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text

def extract_title(content):
    match = re.search(r"title:\s*[\"']?(.*?)[\"']?\n", content)
    return match.group(1).strip() if match else "post"

def is_draft(content):
    """Vérifie si le contenu est un brouillon."""
    # Vérifie 'published: false'
    if re.search(r"published:\s*false", content, re.IGNORECASE):
        return True
    # Vérifie 'status: draft' (courant dans certains exports)
    if re.search(r"status:\s*draft", content, re.IGNORECASE):
        return True
    return False

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
    safe_src = long_path(src_folder)
    if not os.path.exists(safe_src):
        return
    for file in os.listdir(safe_src):
        src = os.path.join(safe_src, file)
        dst = long_path(os.path.join(ASSETS_DIR, file))
        if os.path.isfile(src):
            shutil.copy2(src, dst)

# === TRAITEMENT POSTS ===
posts_path = os.path.join(OUTPUT_DIR, "posts")

if os.path.exists(posts_path):
    for root, dirs, files in os.walk(posts_path):
        for file in files:
            if file == "index.md":
                full_path = long_path(os.path.join(root, file))

                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if is_draft(content):
                    print(f"[SKIP DRAFT] {full_path}")
                    continue

                title = extract_title(content)
                slug = slugify(title)
                date = extract_date_from_path(root)
                
                new_filename = f"{date}-{slug}.md"
                new_path = os.path.join(POSTS_DIR, new_filename)

                # Gestion des images pour les posts
                images_folder = os.path.join(root, "images")
                copy_images(images_folder)
                content = fix_image_paths(content, images_folder)

                # S'assurer qu'il y a un layout post
                if "layout: post" not in content and "---" in content:
                    content = content.replace("---", "---\nlayout: post", 1)

                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"[POST] {new_filename}")


# === TRAITEMENT PAGES ===
pages_path = os.path.join(OUTPUT_DIR, "pages")

for root, dirs, files in os.walk(pages_path):
    for file in files:
        if file == "index.md":
            full_path = long_path(os.path.join(root, file))

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if is_draft(content):
                print(f"[SKIP DRAFT] {full_path}")
                continue

            title = extract_title(content)

            # Convertir les titres en minuscules pour une comparaison insensible à la casse
            if title.lower() not in [p.lower() for p in TARGET_PAGES]:
                print(f"[SKIP PAGE] Titre '{title}' non trouvé dans la liste des pages cibles. Chemin complet : {full_path}")
                continue

            slug = slugify(title)
            date = extract_date_from_path(root)
            new_filename = f"{date}-{slug}.md"
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