"""
generate_sample_data.py

This script generates sample product data for two chatbots (Chatbot A and Chatbot B) 
in multiple formats: Markdown, CSV, and XLSX. The data is stored in the 
`chatbot_data` directory within the script's directory.

Usage:
    python generate_sample_data.py --generate
"""

import argparse
import os
import pandas as pd

def generate_data():
    """
    Generates sample data files for two chatbot directories: Chatbot A and Chatbot B.
    
    - Chatbot A:
        - products.md: Markdown format containing sample product information.
        - products.csv: CSV format with sample product listings.
    
    - Chatbot B:
        - products.xlsx: Excel format with sample product listings.

    The structure created:
    └── chatbot_data/
        ├── chatbot_A/
        │   ├── products.md
        │   └── products.csv
        └── chatbot_B/
            └── products.xlsx

    Directories are created if they do not already exist.
    """
    # Compute the base directory (i.e. where this script is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "chatbot_data")
    
    # Ensure directories exist for sample data
    chatbot_a_dir = os.path.join(data_dir, "chatbot_A")
    chatbot_b_dir = os.path.join(data_dir, "chatbot_B")
    os.makedirs(chatbot_a_dir, exist_ok=True)
    os.makedirs(chatbot_b_dir, exist_ok=True)

    # Sample data for Chatbot A (Markdown)
    markdown_data_a = """
# E-commerce Products
## Product: Widget A
- **Description:** A high-quality widget.
- **Price:** $19.99
- **Category:** Gadgets
## Product: Gizmo A
- **Description:** An advanced gizmo.
- **Price:** $29.99
- **Category:** Gadgets
    """
    md_path_a = os.path.join(chatbot_a_dir, "products.md")
    with open(md_path_a, "w") as f:
        f.write(markdown_data_a.strip())

    # Sample data for Chatbot A (CSV)
    csv_data_a = """id,name,description,price,category
1,Widget B,A compact widget,12.99,Gadgets
2,Gizmo B,A versatile gizmo,22.99,Gadgets
    """
    csv_path_a = os.path.join(chatbot_a_dir, "products.csv")
    with open(csv_path_a, "w") as f:
        f.write(csv_data_a.strip())

    # Sample data for Chatbot B (XLSX)
    xlsx_df_b = pd.DataFrame({
        "id": [1, 2],
        "name": ["Widget C", "Gizmo C"],
        "description": ["A lightweight widget", "A powerful gizmo"],
        "price": [16.99, 27.99],
        "category": ["Gadgets", "Gadgets"]
    })
    xlsx_path_b = os.path.join(chatbot_b_dir, "products.xlsx")
    xlsx_df_b.to_excel(xlsx_path_b, index=False)

    print("Sample data generated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample data for chatbots.")
    parser.add_argument('--generate', action='store_true', help="Generate sample data files.")
    args = parser.parse_args()
    if args.generate:
        generate_data()
