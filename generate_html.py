import json
from pathlib import Path
from html import escape

def generate_html_from_json(json_path, html_path):

    with open(json_path, "r") as f:
        data = json.load(f)
    
    summarized_files = data["data"]["files"]["summarised"]
    processed_files = data["data"]["files"]["processed"]
    raw_files = data["data"]["files"]["raw"]
    
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
        

        .layout {{
            display: flex;
            min-height: 100vh;
        }}
        
        .sidebar {{
            width: 240px;
            background-color: #00274D;
            box-shadow: 0px 8px 10px -5px rgba(0,0,0,0.2), 
                        0px 16px 24px 2px rgba(0,0,0,0.14), 
                        0px 6px 30px 5px rgba(0,0,0,0.12);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 1200;
        }}
        
        .sidebar-header {{
            padding: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);  
            min-height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;  
        }}

        .sidebar-nav {{
            padding: 8px 0;
        }}
        
        .nav-section {{
            margin-bottom: 8px;
        }}
        
        .nav-section-title {{
            padding: 16px 16px 8px 16px;
            font-size: 0.75rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.7);  
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            padding: 8px 16px;
            color: rgba(255, 255, 255, 0.87); 
            text-decoration: none;
            cursor: pointer;
            transition: background-color 150ms cubic-bezier(0.4, 0, 0.2, 1) 0ms;
            font-size: 0.85rem;  
            border-left: 3px solid transparent;
        }}

        .nav-item:hover {{
            background-color: rgba(255, 255, 255, 0.08);  
        }}

        .nav-item.active {{
            background-color: rgba(33, 150, 243, 0.16);  
            border-left-color: #42a5f5;  
            color: #42a5f5;  
            font-weight: 500;
        }}
        
        .nav-item-icon {{
            margin-right: 16px;
            font-size: 20px;
            min-width: 24px;
        }}
        
        .divider {{
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.12); 
            margin: 8px 0;
        }}
        

        .main-content {{
            flex: 1;
            margin-left: 240px;
            display: flex;
            flex-direction: column;
        }}

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
            position: sticky;
            top: 0;
            z-index: 1100;
        }}
        
        .app-bar h1 {{
            font-size: 1.25rem;
            font-weight: 500;
            letter-spacing: 0.0075em;
        }}
        
        /* Container */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 24px;
            width: 100%;
        }}
        
        .paper {{
            background-color: #fff;
            border-radius: 4px;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.2), 
                        0px 1px 1px 0px rgba(0,0,0,0.14), 
                        0px 1px 3px 0px rgba(0,0,0,0.12);
            padding: 16px;
            margin-bottom: 24px;
            scroll-margin-top: 80px;
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
        
        html {{
            scroll-behavior: smooth;
        }}
    </style>
</head>
<body>
    <div class="layout">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <span style="font-weight: 500;">Navigation</span>
            </div>
            
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <div class="nav-section-title">File Types</div>
                    <a href="#raw-files" class="nav-item active">
                        <span>Raw Files</span>
                    </a>
                    <a href="#processed-files" class="nav-item">
                        <span>Processed Files</span>
                    </a>
                    <a href="#summarised-files" class="nav-item">
                        <span>Summarised Files</span>
                    </a>
                </div>
                
                <hr class="divider">
                
                <div class="nav-item" style="cursor: default; flex-direction: column; align-items: flex-start; color: rgba(255, 255, 255, 0.87);">
                    <div style="margin-bottom: 8px;">
                        <strong style="color: white;">{len(raw_files)}</strong> Raw Files
                    </div>
                    <div style="margin-bottom: 8px;">
                        <strong style="color: white;">{len(processed_files)}</strong> Processed Files
                    </div>
                    <div>
                        <strong style="color: white;">{len(summarized_files)}</strong> Summarised Files
                    </div>
                </div>
            </nav>
        </aside>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- App Bar / Header -->
            <header class="app-bar">
                <h1>Data Preview</h1>
            </header>
            
            <!-- Container -->
            <main class="container">
                <!-- Location Information -->
                <div class="location-box">
                    <strong>Location:</strong> {escape(data['data']['location'])}
                </div>
                
                <div class="grid-container">
                    <!-- Raw Files Section -->
                    <section id="raw-files" class="paper">
                        <div class="section-header">
                            <h2 class="section-title">Raw Files</h2>
                        </div>
                        <div class="section-subtitle">{len(raw_files)} file(s) found</div>
                        <div class="table-container">
                            {generate_table(raw_files, 'raw')}
                        </div>
                    </section>
                    
                    <!-- Processed Files Section -->
                    <section id="processed-files" class="paper">
                        <div class="section-header">
                            <h2 class="section-title">Processed Files</h2>
                        </div>
                        <div class="section-subtitle">{len(processed_files)} file(s) found</div>
                        <div class="table-container">
                            {generate_table(processed_files, 'processed')}
                        </div>
                    </section>
                    
                    <!-- Summarised Files Section -->
                    <section id="summarised-files" class="paper">
                        <div class="section-header">
                            <h2 class="section-title">Summarised Files</h2>
                        </div>
                        <div class="section-subtitle">{len(summarized_files)} file(s) found</div>
                        <div class="table-container">
                            {generate_table(summarized_files, 'summarised')}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    </div>
    
    <script>
        // Handle navigation highlighting
        document.addEventListener('DOMContentLoaded', function() {{
            const navItems = document.querySelectorAll('.nav-item[href^="#"]');
            const sections = document.querySelectorAll('section[id]');
            
            // Click handler for nav items
            navItems.forEach(item => {{
                item.addEventListener('click', function(e) {{
                    // Remove active class from all items
                    navItems.forEach(nav => nav.classList.remove('active'));
                    // Add active class to clicked item
                    this.classList.add('active');
                }});
            }});
            
            // Scroll spy - highlight nav item based on scroll position
            window.addEventListener('scroll', function() {{
                let current = '';
                
                sections.forEach(section => {{
                    const sectionTop = section.offsetTop;
                    const sectionHeight = section.clientHeight;
                    if (window.scrollY >= (sectionTop - 100)) {{
                        current = section.getAttribute('id');
                    }}
                }});
                
                navItems.forEach(item => {{
                    item.classList.remove('active');
                    if (item.getAttribute('href') === '#' + current) {{
                        item.classList.add('active');
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
"""
    
    with open(html_path, "w") as f:
        f.write(html_content)
    print(f"HTML report generated at: {html_path}")


def generate_table(files, file_type):
    
    if not files:
        return "<div class='empty-state'>No files found</div>"
    
    table_html = """
    <style>
        .expand-btn {
            background: none;
            border: none;
            border-bottom: 1px solid #1976d2;
            color: #1976d2;
            cursor: pointer;
            font-size: 0.75rem;
            padding: 0 0 2px 0;
            margin-top: 4px;
            display: inline-block;
            font-family: inherit;
        }
        
        .expand-btn:hover {
            color: #1565c0;
            border-bottom-color: #1565c0;
        }
        
        .full-content {
            display: none;
        }
        
        .full-content.show {
            display: block;
        }
    </style>
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
    
    for idx, file in enumerate(files):
        file_name = escape(file.get('file_name', ''))
        file_size = file.get('file_size', '')
        directory = escape(file.get('directory', ''))
        
        # Handle sample_ids
        sample_ids_raw = file.get("sample_id", [])
        if isinstance(sample_ids_raw, list):
            sample_ids_list = sample_ids_raw
            sample_count = len(sample_ids_list)
        else:
            sample_ids_list = [sample_ids_raw]
            sample_count = 1
        
        # Handle patient_ids
        patient_ids_raw = file.get("patient_id", "")
        if isinstance(patient_ids_raw, list):
            patient_ids_list = patient_ids_raw
            patient_count = len(patient_ids_list)
        else:
            patient_ids_list = [patient_ids_raw] if patient_ids_raw else []
            patient_count = len(patient_ids_list)
        
        # Build patient cell
        if patient_count > 5:
            patient_preview = ', '.join(escape(str(p)) for p in patient_ids_list[:5])
            patient_full = ', '.join(escape(str(p)) for p in patient_ids_list)
            unique_id_patient = f"{file_type}-patient-{idx}"
            
            patient_cell = f"""
                <div id="preview-{unique_id_patient}">
                    {patient_preview}...
                </div>
                <div id="full-{unique_id_patient}" class="full-content">
                    {patient_full}
                </div>
                <button class="expand-btn" onclick="toggleCell('{unique_id_patient}', {patient_count})">
                    <span id="btn-{unique_id_patient}">Show more ({patient_count} total)</span>
                </button>
            """
        else:
            patient_cell = ', '.join(escape(str(p)) for p in patient_ids_list)
        
        # Build sample cell
        if sample_count > 5:
            sample_preview = ', '.join(escape(str(s)) for s in sample_ids_list[:5])
            sample_full = ', '.join(escape(str(s)) for s in sample_ids_list)
            unique_id_sample = f"{file_type}-sample-{idx}"
            
            sample_cell = f"""
                <div id="preview-{unique_id_sample}">
                    {sample_preview}...
                </div>
                <div id="full-{unique_id_sample}" class="full-content">
                    {sample_full}
                </div>
                <button class="expand-btn" onclick="toggleCell('{unique_id_sample}', {sample_count})">
                    <span id="btn-{unique_id_sample}">Show more ({sample_count} total)</span>
                </button>
            """
        else:
            sample_cell = ', '.join(escape(str(s)) for s in sample_ids_list)
        
        table_html += f"""
            <tr>
                <td>{file_name}</td>
                <td>{file_size}</td>
                <td>{patient_cell}</td>
                <td>{sample_cell}</td>
                <td>{directory}</td>
                <td>{ORGANIZATION}</td>
            </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    <script>
        function toggleCell(uniqueId, totalCount) {
            const preview = document.getElementById('preview-' + uniqueId);
            const full = document.getElementById('full-' + uniqueId);
            const btn = document.getElementById('btn-' + uniqueId);
            
            if (full.classList.contains('show')) {
                preview.style.display = 'block';
                full.classList.remove('show');
                btn.textContent = 'Show more (' + totalCount + ' total)';
            } else {
                preview.style.display = 'none';
                full.classList.add('show');
                btn.textContent = 'Show less';
            }
        }
    </script>
    """
    
    return table_html