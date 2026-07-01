from pathlib import Path
import re

def parse_traces():
    data_dir = Path("/Users/drizy/Documents/SHL_AI_intern_assignment/data/GenAI_SampleConversations")
    for i in range(1, 11):
        file_path = data_dir / f"C{i}.md"
        content = file_path.read_text()
        print(f"\n--- C{i}.md ---")
        turns = content.split("### Turn ")
        for turn in turns[1:]:
            turn_lines = turn.strip().split("\n")
            turn_no = turn_lines[0].split()[0]
            
            # Find User message
            user_msg = ""
            user_found = False
            for line in turn_lines:
                if "**User**" in line:
                    user_found = True
                    continue
                if user_found and line.strip().startswith(">"):
                    user_msg = line.strip()[1:].strip()
                    break
            print(f"Turn {turn_no} User: {user_msg}")

if __name__ == "__main__":
    parse_traces()
