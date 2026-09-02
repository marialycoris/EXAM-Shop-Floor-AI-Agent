import os


def search_sop(query):
    sop_directory = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sops"
    )

    query = query.lower()

    results = []

    for filename in os.listdir(sop_directory):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(sop_directory, filename)

        with open(file_path, "r") as file:
            content = file.read()

        if query in content.lower() or query in filename.lower():
            results.append({
                "file": filename,
                "content": content,
                "source": f"SOP - {filename.replace('.md', '').replace('_', ' ').title()}"
            })

    if not results:
        return {
            "found": False,
            "results": [],
            "source": "SOP search"
        }

    return {
        "found": True,
        "results": results,
        "source": "SOP search"
    }