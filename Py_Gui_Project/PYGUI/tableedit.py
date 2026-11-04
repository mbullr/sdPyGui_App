import FreeSimpleGUI as sg

# Initial table data (list of lists)
table_data = [
    ["1", "Alice", "Developer"],
    ["2", "Bob", "Designer"],
    ["3", "Charlie", "Manager"],
]
headings = ["ID", "Name", "Role"]

layout = [
    [
        sg.Table(
            values=table_data,
            headings=headings,
            display_row_numbers=False,
            auto_size_columns=True,
            key="-TABLE-",
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
        )
    ],
    [sg.Text("Selected Row to Edit:"), sg.Text("", key="-SELECTED_ROW-", text_color="yellow")],
    [
        sg.Text("ID"),
        sg.Input(key="-ID-", size=(8, 1)),
        sg.Text("Name"),
        sg.Input(key="-NAME-", size=(15, 1)),
        sg.Text("Role"),
        sg.Input(key="-ROLE-", size=(15, 1)),
    ],
    [sg.Button("Load Selected"), sg.Button("Update Row"), sg.Button("Exit")],
]

window = sg.Window("FreeSimpleGUI Edit Table Example", layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # When a row is clicked or "Load Selected" is clicked
    selected_indexes = values["-TABLE-"]
    if event == "Load Selected" or (event == "-TABLE-" and selected_indexes):
        if selected_indexes:
            row_idx = selected_indexes[0]
            row_values = table_data[row_idx]
            window["-SELECTED_ROW-"].update(f"Editing row index {row_idx}")
            window["-ID-"].update(row_values[0])
            window["-NAME-"].update(row_values[1])
            window["-ROLE-"].update(row_values[2])

    # When "Update Row" is clicked, save changes back to table_data and update UI
    if event == "Update Row":
        if selected_indexes:
            row_idx = selected_indexes[0]
            new_id = values["-ID-"]
            new_name = values["-NAME-"]
            new_role = values["-ROLE-"]

            # Update the Python list of lists
            table_data[row_idx] = [new_id, new_name, new_role]

            # Update the Table element visually
            window["-TABLE-"].update(values=table_data)
            sg.popup_quick_message("Row updated!", background_color="green", text_color="white")

window.close()
