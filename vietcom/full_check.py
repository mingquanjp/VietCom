import re

def check_all_template_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track all template tags that need closing
    tag_stack = []
    tag_counts = {
        'if': 0,
        'for': 0,
        'block': 0,
        'with': 0,
        'spaceless': 0,
        'comment': 0,
        'verbatim': 0,
        'autoescape': 0
    }
    
    # Find all template tags
    tags = re.findall(r'{%\s*([^%]+)\s*%}', content)
    
    print("All Django template tags found:")
    print("=" * 50)
    
    for tag in tags:
        tag_parts = tag.strip().split()
        tag_name = tag_parts[0]
        
        print(f"{{% {tag} %}}")
        
        # Handle opening tags
        if tag_name in tag_counts:
            tag_counts[tag_name] += 1
            tag_stack.append(tag_name)
        
        # Handle closing tags
        elif tag_name.startswith('end') and len(tag_name) > 3:
            base_tag = tag_name[3:]  # Remove 'end' prefix
            if base_tag in tag_counts:
                tag_counts[base_tag] -= 1
                if tag_stack and tag_stack[-1] == base_tag:
                    tag_stack.pop()
                else:
                    print(f"  ⚠️ Mismatched closing tag for {base_tag}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    
    errors = []
    for tag, count in tag_counts.items():
        if count != 0:
            if count > 0:
                errors.append(f"Missing {count} {{% end{tag} %}} tag(s)")
                print(f"❌ {tag}: {count} (missing endtag)")
            else:
                errors.append(f"Extra {abs(count)} {{% end{tag} %}} tag(s)")
                print(f"❌ {tag}: {count} (extra endtag)")
        else:
            print(f"✅ {tag}: balanced")
    
    if tag_stack:
        print(f"\n❌ Unclosed tags in stack: {tag_stack}")
    
    if not errors and not tag_stack:
        print("\n🎉 ALL TEMPLATE TAGS ARE PERFECTLY BALANCED!")
    else:
        print(f"\n💥 Found {len(errors)} error(s)")
    
    return len(errors) == 0 and len(tag_stack) == 0

# Check the wall.html file
check_all_template_tags('templates/wall.html')
