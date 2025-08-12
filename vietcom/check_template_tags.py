import re

def check_template_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Django template tags
    tags = re.findall(r'{%\s*([^%]+)\s*%}', content)
    
    # Count opening and closing tags
    tag_counts = {}
    
    for tag in tags:
        tag_name = tag.strip().split()[0]
        
        if tag_name.startswith('end'):
            # This is a closing tag
            opening_tag = tag_name[3:]  # Remove 'end' prefix
            if opening_tag in tag_counts:
                tag_counts[opening_tag] -= 1
            else:
                tag_counts[opening_tag] = -1
        elif tag_name in ['if', 'for', 'block', 'with', 'spaceless', 'comment', 'verbatim', 'autoescape']:
            # This is an opening tag that needs closing
            if tag_name in tag_counts:
                tag_counts[tag_name] += 1
            else:
                tag_counts[tag_name] = 1
        # Other tags like 'extends', 'include', 'load', 'url', 'csrf_token', 'static' don't need closing
    
    print("Django Template Tags Analysis:")
    print("=" * 40)
    
    errors = []
    for tag, count in tag_counts.items():
        print(f"{tag}: {count}")
        if count != 0:
            if count > 0:
                errors.append(f"Missing {count} {{% end{tag} %}} tag(s)")
            else:
                errors.append(f"Extra {abs(count)} {{% end{tag} %}} tag(s)")
    
    if errors:
        print("\nERRORs FOUND:")
        for error in errors:
            print(f"❌ {error}")
    else:
        print("\n✅ All template tags are balanced!")
    
    return len(errors) == 0

# Check the wall.html file
check_template_tags('templates/wall.html')
