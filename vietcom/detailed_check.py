import re

def detailed_check_template_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    blocks = []
    endblocks = []
    
    for i, line in enumerate(lines, 1):
        # Find {% block ... %}
        block_matches = re.findall(r'{%\s*block\s+(\w+)\s*%}', line)
        for match in block_matches:
            blocks.append((i, match))
        
        # Find {% endblock %}
        if '{% endblock %}' in line:
            endblocks.append(i)
    
    print("BLOCKS found:")
    for line_num, block_name in blocks:
        print(f"  Line {line_num}: {{% block {block_name} %}}")
    
    print(f"\nENDBLOCKS found:")
    for line_num in endblocks:
        print(f"  Line {line_num}: {{% endblock %}}")
    
    print(f"\nSummary:")
    print(f"  Total blocks: {len(blocks)}")
    print(f"  Total endblocks: {len(endblocks)}")
    
    if len(blocks) == len(endblocks):
        print("✅ Blocks are balanced!")
    else:
        print(f"❌ Mismatch: {len(blocks)} blocks vs {len(endblocks)} endblocks")
        if len(blocks) > len(endblocks):
            print(f"Missing {len(blocks) - len(endblocks)} endblock(s)")
        else:
            print(f"Extra {len(endblocks) - len(blocks)} endblock(s)")

detailed_check_template_tags('templates/wall.html')
