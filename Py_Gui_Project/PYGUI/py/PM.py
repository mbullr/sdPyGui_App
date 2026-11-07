import FreeSimpleGUI as sg

# Set a clean, modern color theme
sg.theme("DarkBlue3")

# Common size for labels to make the fields align neatly
lbl_sz = (18, 1)

# Define the layout of the window (list of rows)
layout = [
    
    [sg.Text(text='Product Id',size=(11,1)),sg.Combo("", key='PD_LIST', size=(11,1), readonly=True), sg.Button(button_text='Get',size=(5,1)), sg.Button(button_text='New',size=(5,1))],
    
    [
        sg.Text("Product Name:", size=lbl_sz),
        sg.Input(key="PD_NAME", size=(35, 1)),
    ],
   
    [
        sg.Text("Product Description:", size=lbl_sz),
        sg.Multiline(key="PD_DESC", size=(35, 3)),
    ],
        [
        sg.Text("Product Drawing:", size=lbl_sz),
        sg.Input(key="PD_DRAW", size=(35, 1)),
    ],
            [
        sg.Text("Product Revision:", size=lbl_sz),
        sg.Input(key="PD_REV", size=(5, 1)),
    ],
    [
        sg.Text("Unit of Measure (UOM):", size=lbl_sz),
        sg.Combo(
            ["Each", "Box", "KG", "Liters", "Meters"],
            default_value="Each",
            key="PD_UOM",
            size=(15, 1),
        ),
    ],
    [
        sg.Text("Product Type:", size=lbl_sz),
        sg.Combo(
            ["Finished Goods", "Raw Materials", "Service"],
            default_value="Finished Goods",
            key="PD_TYPE",
            size=(15, 1),
        ),
    ],
    [
        sg.Text("Quantity on Hand (QOH):", size=lbl_sz),
        sg.InputText("0", key="PD_QOH", size=(15, 1)),
    ],
    [
        sg.Text("Product Std Cost ($):", size=lbl_sz),
        sg.InputText("0.00", key="PD_STDCST", size=(15, 1)),
    ],
    [sg.HSeparator()],
    [
        sg.Button("File", bind_return_key=True),
        sg.Button("Cancel"),
    ],
    [sg.Text(text='Status:', key = '-STATUS-',size=(80,1))]
]
pd_layout = [sg.Frame(title='',layout = layout,expand_x=True,expand_y=True),sg.Menu([['Menu',['Help','About']]])],
# Create the Window
window = sg.Window("Products", pd_layout)

# Event Loop to process "events" and get "values" of inputs
while True:
    event, values = window.read()

    # If user closes window or clicks Cancel
    if event in (sg.WIN_CLOSED, "Cancel"):
        break

    # If user clicks Clear, reset all fields
    if event == "Clear":
        for key in values:
            if key in ("product_uom", "product_type"):
                window[key].update(value="")
            elif key in ("product_qoh", "product_price"):
                window[key].update(value="0")
            else:
                window[key].update(value="")

    # If user clicks Submit
    if event == "Submit":
        # Extract individual values cleanly using their keys
        name = values["product_name"].strip()
        desc = values["product_description"].strip()
        uom = values["product_uom"]
        p_type = values["product_type"]
        qoh = values["product_qoh"]
        price = values["product_price"]

        # Simple verification step
        if not name:
            sg.popup_error("Error: Product Name is required!")
            continue

        # Print data out to console or process it further
        output_msg = (
            f"Product successfully submitted!\n\n"
            f"Name: {name}\n"
            f"Description: {desc}\n"
            f"UOM: {uom}\n"
            f"Type: {p_type}\n"
            f"QOH: {qoh}\n"
            f"Price: ${price}"
        )
        sg.popup("Success", output_msg)

# Clean up and close the window
window.close()
