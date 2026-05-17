# file_generator.py - Copy this entire code
from datetime import datetime
import os

class FileGenerator:
    @staticmethod
    def generate_response_file(query: str, answer: str, references: list, output_dir="./generated_files"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(f"Query: {query}\n\n")
            f.write(f"Answer: {answer}\n\n")
            f.write("References:\n")
            for ref in references:
                f.write(f"- {ref}\n")
        return filepath
    
    @staticmethod
    def modify_response(original_file: str, modification_prompt: str) -> str:
        with open(original_file, "r") as f:
            content = f.read()
        new_content = f"{content}\n\n[Modified based on: {modification_prompt}]"
        new_path = original_file.replace(".txt", "_modified.txt")
        with open(new_path, "w") as f:
            f.write(new_content)
        return new_path