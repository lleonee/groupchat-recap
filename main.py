import asyncio
import io
from pyscript import document, window
from js import Uint8Array, Blob, URL, document as js_doc, console, Object
from pyodide.ffi import create_proxy
import recap_logic
import pandas as pd
import zipfile

# Global state
selected_file = None
parsed_data = None
generated_pdf_bytes = None

def setup():
    """Initialize the application state."""
    print("Python environment ready.")
    
    # Enable UI logic
    # Enable UI logic - Switch from loading state to upload state
    document.getElementById("drop-loading").classList.add("hidden")
    document.getElementById("drop-content").classList.remove("hidden")
    
    # status_el is empty at start now, only used for process updates
    status_el = document.getElementById("status-msg")
    status_el.classList.remove("status-loading")
    
    # Bind events
    file_input = document.getElementById("file-upload")
    file_proxy = create_proxy(on_file_change)
    file_input.addEventListener("change", file_proxy)
    
    gen_btn = document.getElementById("generate-btn")
    gen_proxy = create_proxy(on_generate_click)
    gen_btn.addEventListener("click", gen_proxy)

    # Bind Result Buttons
    view_btn = document.getElementById("view-btn")
    view_proxy = create_proxy(on_view_click)
    view_btn.addEventListener("click", view_proxy)
    
    down_btn = document.getElementById("download-btn")
    down_proxy = create_proxy(on_download_click)
    down_btn.addEventListener("click", down_proxy)

    # Drag & Drop
    drop_area = document.getElementById("drop-area")
    
    prevent_proxy = create_proxy(prevent_defaults)
    drop_area.addEventListener("dragenter", prevent_proxy)
    drop_area.addEventListener("dragover", prevent_proxy)
    drop_area.addEventListener("dragleave", prevent_proxy)
    
    drop_proxy = create_proxy(on_drop)
    drop_area.addEventListener("drop", drop_proxy)

def prevent_defaults(e):
    e.preventDefault()
    e.stopPropagation()

def on_drop(event):
    event.preventDefault()
    event.stopPropagation()
    files = event.dataTransfer.files
    handle_files(files)

def on_file_change(event):
    files = event.target.files
    handle_files(files)

def handle_files(files):
    if files.length > 0:
        global selected_file
        selected_file = files.item(0)
        # console.log(f"File selected: {selected_file.name}")
        document.getElementById("filename").innerText = selected_file.name
        document.getElementById("file-info").classList.remove("hidden")
        
        status_el = document.getElementById("status-msg")
        status_el.innerText = "Dosya okunuyor ve analiz ediliyor..."
        status_el.classList.add("status-loading")
        status_el.classList.remove("status-success")
        
        # Trigger async processing
        asyncio.ensure_future(process_selected_file())
    else:
        reset_state()

def reset_state():
    global selected_file, parsed_data, generated_pdf_bytes
    selected_file = None
    parsed_data = None
    generated_pdf_bytes = None
    document.getElementById("generate-btn").disabled = True
    document.getElementById("user-mapping-area").classList.add("hidden")
    document.getElementById("user-mapping-list").innerHTML = ""
    document.getElementById("result-options").classList.add("hidden")
    document.getElementById("result-options").style.display = "none"

async def process_selected_file():
    global parsed_data, selected_file
    if not selected_file:
        return

    try:
        # Read file
        filename = selected_file.name.lower()
        text_content = ""

        if filename.endswith(".zip"):
            document.getElementById("status-msg").innerText = "ZIP dosyası açılıyor..."
            # Handle ZIP file
            array_buf = await selected_file.arrayBuffer()
            js_array = Uint8Array.new(array_buf)
            data_bytes = bytes(js_array)

            with zipfile.ZipFile(io.BytesIO(data_bytes)) as z:
                txt_files = [f for f in z.namelist() if f.endswith(".txt") and not f.startswith("__MACOSX")]
                if not txt_files:
                    raise Exception("ZIP dosyası içinde .txt dosyası bulunamadı.")
                
                # Take the first text file
                target_file = txt_files[0]
                # console.log(f"Extracted: {target_file}")
                text_content = z.read(target_file).decode("utf-8")
        else:
            # Handle Text file
            text_content = await selected_file.text()
        
        # Parse
        parsed_data = recap_logic.parse_chat(text_content)
        
        if not parsed_data['messages']:
            document.getElementById("status-msg").innerText = "Hata: Geçerli mesaj bulunamadı."
            document.getElementById("status-msg").classList.remove("status-loading")
            return

        # Enable Generation
        document.getElementById("generate-btn").disabled = False
        status_el = document.getElementById("status-msg")
        status_el.innerText = "Dosya analiz edildi! İsimleri düzenleyebilir veya PDF oluşturabilirsiniz."
        status_el.classList.remove("status-loading")
        
        # Extract senders for mapping
        df = pd.DataFrame(parsed_data['messages'], columns=parsed_data['columns'])
        
        # Clean Universal Garbage (System, =, $)
        df = df[df['sender'] != "System"]
        df = df[~df['sender'].str.startswith('=')]
        df = df[~df['sender'].str.startswith('$')]
        
        # Check current unique senders count
        initial_senders = df['sender'].unique()
        
        # AUTO DETECT DM: If exactly 2 people, it is DM.
        if len(initial_senders) == 2:
            detected_is_dm = True
            document.getElementById("status-msg").innerText = "2 Kişilik Sohbet (DM) Algılandı. Analiz hazır."
            # console.log("Auto-detected DM mode (2 users). Filters disabled.")
        else:
            # If not 2, try standard filtering (removing 'grubu' etc)
            # This handles cases where "Group Name" appears as sender in Groups
            df_filtered = df[~df['sender'].str.contains('grubu', case=False, na=False)]
            filtered_senders = df_filtered['sender'].unique()
            
            if len(filtered_senders) == 2:
                # If filtering reduced it to 2, it was a DM with noise
                detected_is_dm = True
                df = df_filtered # Apply filter
                document.getElementById("status-msg").innerText = "2 Kişilik Sohbet (DM) Algılandı. Analiz hazır."
                # console.log("Auto-detected DM mode after noise filtering.")
            else:
                # It's a group chat
                detected_is_dm = False
                df = df_filtered # Apply filter
                document.getElementById("status-msg").innerText = f"{len(filtered_senders)} Kişilik Grup Sohbeti Algılandı. Analiz hazır."
                # console.log("Detected Group mode.")
        
        # Store global state
        window.detected_is_dm = detected_is_dm
        
        unique_senders = sorted(df['sender'].unique())
        populate_user_mapping_ui(unique_senders)
        
    except Exception as e:
        console.error(f"Error processing file: {e}")
        document.getElementById("status-msg").innerText = f"Error: {e}"

def populate_user_mapping_ui(senders):
    container = document.getElementById("user-mapping-list")
    container.innerHTML = ""
    
    for sender in senders:
        div = js_doc.createElement("div")
        div.className = "user-item"
        
        label = js_doc.createElement("label")
        label.innerText = sender
        label.title = sender 
        
        input_field = js_doc.createElement("input")
        input_field.type = "text"
        input_field.value = sender
        input_field.setAttribute("data-original", sender)
        input_field.className = "user-map-input"
        
        div.appendChild(label)
        div.appendChild(input_field)
        container.appendChild(div)
        
    document.getElementById("user-mapping-area").classList.remove("hidden")

async def on_generate_click(event):
    global parsed_data, generated_pdf_bytes
    if not parsed_data:
        return
        
    btn = document.getElementById("generate-btn")
    btn.disabled = True
    document.getElementById("spinner").classList.remove("hidden")
    document.getElementById("btn-text").innerText = "Başlatılıyor..."
    
    status_el = document.getElementById("status-msg")
    status_el.innerText = "Oluşturma başlatılıyor..."
    status_el.classList.add("status-loading")
    status_el.classList.remove("status-success")
    
    # Allow UI to update
    await asyncio.sleep(0.1)
    
    try:
        # Collect User Map
        user_map = {}
        inputs = document.querySelectorAll(".user-map-input")
        for i in range(inputs.length):
            inp = inputs.item(i)
            original = inp.getAttribute("data-original")
            new_name = inp.value.strip()
            if new_name and new_name != original:
                user_map[original] = new_name
        
        
        # Check DM Mode (Auto Detected)
        is_dm = getattr(window, 'detected_is_dm', False)
            
        # Initialize Renderer
        # Use default blacklist embedded in logic
        renderer = recap_logic.RecapRenderer(parsed_data, user_map, is_dm=is_dm)
        
        # Create Buffer
        buffer = io.BytesIO()
        from matplotlib.backends.backend_pdf import PdfPages
        from datetime import datetime
        
        status_el.innerText = "PDF ortamı hazırlanıyor..."
        await asyncio.sleep(0.05)
        
        with PdfPages(buffer) as pdf:
            slides = renderer.get_slide_execution_list()
            total_slides = len(slides)
            
            for i, (name, method) in enumerate(slides):
                # Update Status
                percent = int(((i) / total_slides) * 100)
                msg = f"Hazırlanıyor %{percent}"
                document.getElementById("status-msg").innerText = msg
                # console.log(msg)
                
                # Yield control to UI
                await asyncio.sleep(0.02)
                
                # Execute Slide
                method(pdf)
            
            # Finalize
            document.getElementById("status-msg").innerText = "Hazırlanıyor %100"
            d = pdf.infodict()
            d['Title'] = 'Groupchat Yearly Recap'
            d['Author'] = 'PyScript Recap Generator'
            d['CreationDate'] = datetime.now()
            
        buffer.seek(0)
        generated_pdf_bytes = buffer.getvalue()
        
        # Show Result Options
        status_el = document.getElementById("status-msg")
        status_el.innerText = "Tamamlandı! Yukarıdan bir seçenek seçin."
        status_el.classList.remove("status-loading")
        status_el.classList.add("status-success")
        
        document.getElementById("generate-btn").classList.add("hidden")
        document.getElementById("result-options").classList.remove("hidden")
        document.getElementById("result-options").style.display = "flex"
        
    except Exception as e:
        console.error(f"Error generating PDF: {e}")
        document.getElementById("status-msg").innerText = f"Error: {e}"
    finally:
        btn.disabled = False
        document.getElementById("spinner").classList.add("hidden")
        document.getElementById("btn-text").innerText = "Özeti Oluştur (PDF)"

def on_view_click(event):
    if generated_pdf_bytes:
        create_blob_and_act(generated_pdf_bytes, "view")

def on_download_click(event):
    if generated_pdf_bytes:
        create_blob_and_act(generated_pdf_bytes, "download", "groupchat_recap.pdf")

def create_blob_and_act(pdf_bytes, action, filename="document.pdf"):
    js_array = Uint8Array.new(len(pdf_bytes))
    for i, b in enumerate(pdf_bytes):
        js_array[i] = b
    
    # Create options object explicity
    options = Object.new()
    options.type = "application/pdf"
    blob = Blob.new([js_array], options)
    
    url = URL.createObjectURL(blob)
    
    link = js_doc.createElement("a")
    link.href = url
    
    if action == "view":
        link.target = "_blank"
    else:
        link.download = filename
        
    js_doc.body.appendChild(link)
    link.click()
    js_doc.body.removeChild(link)
    
    # URL.revokeObjectURL(url) 

    # Load User Map
    # ... (existing code for user map)

# Run setup
setup()
