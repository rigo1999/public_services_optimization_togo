import os
import json
import base64

def extract_images_from_notebook(notebook_path, output_dir):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Error reading {notebook_path}: {e}")
        return

    notebook_name = os.path.splitext(os.path.basename(notebook_path))[0]
    
    img_count = 0
    for i, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'code':
            for j, output in enumerate(cell.get('outputs', [])):
                if 'data' in output:
                    data = output['data']
                    # Look for png or jpeg
                    for mime_type in ['image/png', 'image/jpeg']:
                        if mime_type in data:
                            img_data = data[mime_type]
                            # Sometimes it's a list of strings
                            if isinstance(img_data, list):
                                img_data = "".join(img_data)
                            
                            ext = 'png' if 'png' in mime_type else 'jpg'
                            img_filename = f"{notebook_name}_cell{i}_img{img_count}.{ext}"
                            img_path = os.path.join(output_dir, img_filename)
                            
                            try:
                                with open(img_path, 'wb') as img_file:
                                    img_file.write(base64.b64decode(img_data))
                                print(f"  Saved: {img_filename}")
                                img_count += 1
                            except Exception as e:
                                print(f"  Error saving {img_filename}: {e}")

if __name__ == "__main__":
    base_dir = r"d:\public_services_optimization_togo\01_Exploration_des_Donnees_EDA"
    notebooks_dir = os.path.join(base_dir, "EDA_notebooks")
    output_dir = os.path.join(base_dir, "EDA_visualizations")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(notebooks_dir):
        if filename.endswith(".ipynb"):
            print(f"Processing {filename}...")
            extract_images_from_notebook(os.path.join(notebooks_dir, filename), output_dir)
