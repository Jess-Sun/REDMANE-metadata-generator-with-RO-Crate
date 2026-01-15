import json
from pathlib import Path
from html import escape
from params import ORGANIZATION

def generate_html_from_json(json_path, html_path):
    """
    Dummy implementation that creates HTML file from JSON.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    
    summarized_files = data["data"]["files"]["summarised"]
    processed_files = data["data"]["files"]["processed"]
    raw_files = data["data"]["files"]["raw"]
    
    # Generate the complete HTML with CSS
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Data Commons</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "Roboto", "Helvetica", "Arial", sans-serif;
            background-color: #f5f5f5;
            color: rgba(0, 0, 0, 0.87);
            line-height: 1.5;
        }}
        
        /* Header / AppBar */
        .app-bar {{
            background-color: #00274D;
            color: white;
            padding: 16px 24px;
            box-shadow: 0px 2px 4px -1px rgba(0,0,0,0.2), 
                        0px 4px 5px 0px rgba(0,0,0,0.14), 
                        0px 1px 10px 0px rgba(0,0,0,0.12);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .app-bar h1 {{
            font-size: 1.25rem;
            font-weight: 500;
            letter-spacing: 0.0075em;
        }}
        
        /* Main Container */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 24px;
        }}
        
        /* Paper/Card Component */
        .paper {{
            background-color: #fff;
            border-radius: 4px;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.2), 
                        0px 1px 1px 0px rgba(0,0,0,0.14), 
                        0px 1px 3px 0px rgba(0,0,0,0.12);
            padding: 16px;
            margin-bottom: 24px;
        }}
        
        /* Section Headers */
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        
        .section-title {{
            font-size: 1.25rem;
            font-weight: 500;
            color: rgba(0, 0, 0, 0.87);
            letter-spacing: 0.0075em;
        }}
        
        .section-subtitle {{
            font-size: 0.875rem;
            color: rgba(0, 0, 0, 0.6);
            margin-bottom: 16px;
        }}
        
        /* Location Info Box */
        .location-box {{
            background-color: #fff;
            border-radius: 4px;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.2), 
                        0px 1px 1px 0px rgba(0,0,0,0.14), 
                        0px 1px 3px 0px rgba(0,0,0,0.12);
            padding: 16px;
            margin-bottom: 24px;
            font-size: 0.875rem;
        }}
        
        .location-box strong {{
            color: rgba(0, 0, 0, 0.87);
            font-weight: 500;
        }}
        
        /* Table Styles */
        .table-container {{
            width: 100%;
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        
        thead {{
            background-color: transparent;
        }}
        
        th {{
            padding: 16px;
            text-align: left;
            font-weight: 500;
            color: rgba(0, 0, 0, 0.87);
            border-bottom: 1px solid rgba(224, 224, 224, 1);
            letter-spacing: 0.01071em;
        }}
        
        td {{
            padding: 16px;
            border-bottom: 1px solid rgba(224, 224, 224, 1);
            color: rgba(0, 0, 0, 0.87);
        }}
        
        tbody tr:hover {{
            background-color: rgba(0, 0, 0, 0.04);
        }}
        
        tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        
        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: rgba(0, 0, 0, 0.6);
            font-size: 0.875rem;
        }}
        
        /* Grid spacing */
        .grid-container {{
            display: grid;
            gap: 24px;
        }}
    </style>
</head>
<body>
    <!-- App Bar / Header -->
    <div class="app-bar">
        <h1>DataPreview</h1>
    </div>
    
    <!-- Main Container -->
    <div class="container">
        <!-- Location Information -->
        <div class="location-box">
            <strong>Location:</strong> {escape(data['data']['location'])}
        </div>
        
        <div class="grid-container">
            <!-- Raw Files Section -->
            <div class="paper">
                <div class="section-header">
                    <h2 class="section-title">Raw Files</h2>
                </div>
                <div class="section-subtitle">{len(raw_files)} file(s) found</div>
                <div class="table-container">
                    {generate_table(raw_files, 'raw')}
                </div>
            </div>
            
            <!-- Processed Files Section -->
            <div class="paper">
                <div class="section-header">
                    <h2 class="section-title">Processed Files</h2>
                </div>
                <div class="section-subtitle">{len(processed_files)} file(s) found</div>
                <div class="table-container">
                    {generate_table(processed_files, 'processed')}
                </div>
            </div>
            
            <!-- Summarised Files Section -->
            <div class="paper">
                <div class="section-header">
                    <h2 class="section-title">Summarised Files</h2>
                </div>
                <div class="section-subtitle">{len(summarized_files)} file(s) found</div>
                <div class="table-container">
                    {generate_table(summarized_files, 'summarised')}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_path, "w") as f:
        f.write(html_content)
    print(f"HTML report generated at: {html_path}")


def generate_table(files, file_type):
    """
    Helper function to generate Material-UI styled table for files.
    """
    if not files:
        return "<div class='empty-state'>No files found</div>"
    
    table_html = """
    <table>
        <thead>
            <tr>
                <th>File Name</th>
                <th>File Size (KB)</th>
                <th>Patient ID</th>
                <th>Sample ID</th>
                <th>Directory</th>
                <th>Organization</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for file in files:
        # Handle sample_ids
        sample_ids = file.get("sample_id", [])
        if isinstance(sample_ids, list):
            sample_ids = ', '.join(escape(str(s)) for s in sample_ids)
        else:
            sample_ids = escape(str(sample_ids))
        
        # Handle patient_ids
        patient_ids = file.get("patient_id", "")
        if isinstance(patient_ids, list):
            patient_ids = ', '.join(escape(str(p)) for p in patient_ids)
        else:
            patient_ids = escape(str(patient_ids))
        
        table_html += f"""
            <tr>
                <td>{escape(file.get('file_name', ''))}</td>  
                <td>{file.get('file_size', '')}</td>         
                <td>{patient_ids}</td>                      
                <td>{sample_ids}</td> 
                <td>{escape(file.get('directory', ''))}</td>  
                <td>{ORGANIZATION}</td>                      
            </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    """
    
    return table_html