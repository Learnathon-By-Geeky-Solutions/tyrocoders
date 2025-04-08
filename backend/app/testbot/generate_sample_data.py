import argparse
import os
import pandas as pd

def generate_data():
    # Compute the base directory (i.e. testbot directory)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "chatbot_data")
    
    # Ensure directories exist for sample data inside the testbot folder
    dir_chatbot_A = os.path.join(data_dir, "chatbot_A")
    dir_chatbot_B = os.path.join(data_dir, "chatbot_B")
    os.makedirs(dir_chatbot_A, exist_ok=True)
    os.makedirs(dir_chatbot_B, exist_ok=True)

    # Sample data for Chatbot A (Markdown)
    markdown_data_A = """
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
    md_path_A = os.path.join(dir_chatbot_A, "products.md")
    with open(md_path_A, "w") as f:
        f.write(markdown_data_A.strip())

    # Sample data for Chatbot A (CSV)
    csv_data_A = """id,name,description,price,category
1,Widget B,A compact widget,12.99,Gadgets
2,Gizmo B,A versatile gizmo,22.99,Gadgets
    """
    csv_path_A = os.path.join(dir_chatbot_A, "products.csv")
    with open(csv_path_A, "w") as f:
        f.write(csv_data_A.strip())

    # Sample data for Chatbot B (XLSX)
    xlsx_df_B = pd.DataFrame({
        "id": [1, 2],
        "name": ["Widget C", "Gizmo C"],
        "description": ["A lightweight widget", "A powerful gizmo"],
        "price": [16.99, 27.99],
        "category": ["Gadgets", "Gadgets"]
    })
    xlsx_path_B = os.path.join(dir_chatbot_B, "products.xlsx")
    xlsx_df_B.to_excel(xlsx_path_B, index=False)

    print("Sample data generated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample data for chatbots.")
    parser.add_argument('--generate', action='store_true', help="Generate sample data files.")
    args = parser.parse_args()

    if args.generate:
        generate_data()
