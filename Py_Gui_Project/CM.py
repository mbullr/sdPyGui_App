#CM.py
# Customer window, paired with basic program CM.BP
# intent is to create a fully (or somewhat fully) functional app to demo (read test) PyGui integration
# Notes:
# All imports happen within the _setup.py script
# We should define windows within a function to ensure objects used during creation (the layout) get garbage collected.
# Because we are running embedded within the sd app and it is possible the sd process could be alive for long periods of
#  time, we should clean up (set to None) any objects created either within the _setup.py or _step.py script.
# Also at some point the sd Python function PY_PYGUISTEP()  (sd_py_gui_step in sdext_py.c) should be passed the name of #  the function defined in the _step.py script (in this example gui_step).  Currently it is hardcoded.
import FreeSimpleGUI as sg
# import json
# rem the sd module is an extension module defined in sdext_py.c created by the sd VM using the python c api 
#   
import sd


SDME_FM  = chr(254)
SDME_VM  = chr(253)
SDME_SVM = chr(252)

_gui_closed = False
_close_event_sent = False
values = {} 
PUP_window = None

# function to define our popup (cannot use freesimplegui standard pop up (they will be blocking)
# todo add buttons to calling params
def my_popup(my_title, my_message):
    my_layout = [
                  [sg.Text(my_message)],
                  [sg.Button('Yes', key='-YES-'), sg.Button('No', key='-NO-')]
                  ]
    return sg.Window(my_title, my_layout, location=(100, 200), modal=True, finalize=True)
    
#
# function to define the main app window

def app_window():
  Frame1_layout = [
  [sg.Text(text='Customer Id',size=(11,1)),sg.Combo(cm_id_options, default_value='Choose...', key='CM_ID', enable_events=True,size=(11,1), readonly=True),sg.Button(button_text='Get',size=(5,1)), sg.Button(button_text='New',size=(5,1))],
  [sg.Text(text='Name',size=(9,1)),sg.Input(size=(29,1),key='CM_NAME')],
  [sg.Text(text='Addr1',size=(9,1)),sg.Input(size=(29,1),key='CM_ADDR')],
  [sg.Text(text='Addr2',size=(9,1)),sg.Input(size=(29,1),key='CM_ADDR2')],
  [sg.Text(text='City, St.',size=(9,1)),sg.Input(size=(21,1),key='CM_CITY'),sg.Listbox(size=(8,1),key='CM_STATE',values='')],
  [sg.Text(text='Zip, Co',size=(9,1)),sg.Input(size=(13,1),key='CM_ZIP'),sg.Input(size=(16,1),key='CM_COUNTRY')],
  [sg.Text(text='AR Limit',size=(9,1)),sg.Input(size=(11,1),key='CM_AR_LIMIT'),sg.Text(text='Terms',size=(5,1)),sg.Listbox(size=(11,1),key='CM_TERMS',values='')],
  [sg.Text(text='Phone',size=(9,1)),sg.Input(size=(12,1),key='CM_PHONE'),sg.Text(text='Fax',size=(5,1)),sg.Input(size=(12,1),key='CM_FAX')],
  [sg.Text(text='Web Site',size=(8,1)),sg.Input(size=(19,1),key='CM_WEB'),sg.Text(text='Status',size=(5,1)),sg.Listbox(size=(11,1),key='CM_STATUS',values='')],
  [sg.Text(text='Rep',size=(8,1)),sg.Input(size=(19,1),key='CM_REP'),sg.Button(button_text='Create ShipTo',size=(7,2))] 
  ] 
  
  frmShipTo_layout = [
  [sg.Text(text='Name',size=(5,1)),sg.Input(size=(30,1),key='CS_NAME')],
  [sg.Text(text='Addr1',size=(5,1)),sg.Input(size=(30,1),key='CS_ADDR')],
  [sg.Text(text='Addr2',size=(5,1)),sg.Input(size=(30,1),key='CS_ADDR2')],
  [sg.Text(text='City, St.',size=(9,1)),sg.Input(size=(21,1),key='CS_CITY'),sg.Listbox(size=(8,1),key='CS_STATE',values='')],
  [sg.Text(text='Zip, Co',size=(9,1)),sg.Input(size=(12,1),key='CS_ZIP'),sg.Input(size=(15,1),key='CS_COUNTRY')],
  [sg.Text(text='Phone',size=(9,1)),sg.Input(size=(12,1),key='CS_PHONE'),sg.Text(text='Fax',size=(3,1)),sg.Input(size=(12,1),key='CS_FAX')],
  [sg.Text(text='Status',size=(5,1)),sg.Listbox(size=(11,1),key='CS_STATUS',values='')],
  [sg.Checkbox(text='Default Ship To',size=(12,2),key='chkDefault')],
  [sg.Button(button_text='Delete ShipTo',size=(8,2))] 
  ]
  
  CM_layout = [
  [sg.Frame(size=(259,300),title='',layout = Frame1_layout,expand_x=True,expand_y=True),sg.Frame(title='Ship To',size=(260,300),layout = frmShipTo_layout,expand_x=True,expand_y=True),sg.Menu([['Menu',['Help','About']]])],
  [],
  [sg.Text(text='Customer Contacts',size=(17,1))],
  [sg.Table(headings=['Customer Name', 'Contact Phone', 'Contact Email', 'Contact Fax'],values=[['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', '']],num_rows=6,key='CM_CONTACT',alternating_row_color="light steel blue")],
  [sg.Button(button_text='File',size=(8,1)),sg.Button(button_text='Cancel',size=(8,1)),sg.Button(button_text='Delete Customer',size=(8,2))]
  ] 
  return sg.Window('Customers', CM_layout, size=(861,527), resizable=True,  finalize=True)
  
#
# define the all important step function
# this is called by the VM basic program with the function PY_PYGUISTEP()
# Note the py function name "gui_step" is hardcoded into the c function sd_py_gui_step defined in sdext_py.c
#   at some point we should make the function name a parameter, but not today......
def gui_step(max_milliseconds=5):
    # note we must declare as global otherwise our sd functions will not find in global dict 
    global _gui_closed, _close_event_sent, values, PUP_window

    if _gui_closed:
        return 0

    if not main_window.TKroot.winfo_exists():
        _gui_closed = True
        return 0

    #event, values = window.read(timeout=max_milliseconds)
    window, event, values = sg.read_all_windows(timeout=max_milliseconds)
    
    if event == '__TIMEOUT__':
    # in an actual app we would not pass this event, for now we are doing it to track returns to VM
        sd.post_event(event, event) 
    
    # closing window logic
    elif event == sg.WIN_CLOSED:
        # main window?, if so close everything  down
        if window == main_window: 
            window.close()
            _gui_closed = True
            _close_event_sent = True
            # if the popup is still open, make sure it closes!
            if PUP_window: PUP_window.close()
            # finally tell the VM we are done
            sd.post_event("main_window", "closed")
            return 0
            
        # if it is our popup, close it and toss its object (otherwise we cannot re create it)
        elif window == PUP_window:
            window.close()
            PUP_window = None

        # other window, just close it
        else:
            window.close()
            
            
    # main window event logic
    #  catch all the defined events (for now just buttons)
    #  Note payload is limited in size to 4K? 
    #   The basic program will read the values dictionary so not need to pass data.
    elif window == main_window:

        if event == 'Get':
            payload = "Get Click"
            sd.post_event(event,payload)
        # #
        elif event == 'New':
            payload = "New Click"
            sd.post_event(event,payload)
        # #
        elif event == 'File':
            payload = "File Click"
            sd.post_event(event,payload)
        # #
        elif event == 'Cancel':
            payload = "Cancel Click"
            sd.post_event(event,payload)
        # #
        elif event == 'Delete':
            payload = "Delete Click"
            sd.post_event(event,payload)
        # #
        elif event == 'Delete ShipTo':
            payload = "Delete ShipTo Click"
            sd.post_event(event,payload)        
        
        elif event == '-PUP-':
            if PUP_window == None:
                PUP_window = my_popup('The PopUp','This PopUp Is For YOU!')
                PUP_Visable = True
                
    elif window == PUP_window:
        sd.post_event("Pup_window",event)
            
    return 0    
    
    
    
main_window = my_main_window()
#
# rem print(window.key_dict.keys()) to list keys in window
# dict_keys(['-UNAME-', '-DOB-', '-ACCOUNT-', 'Ok'])
# • Replace all text: Pass a new string into the update() method to clear the old content and show the new text.
# • Append new text: Use window["key"].update("additional text", append=True) to add new lines to the bottom without deleting # existing text.

main_window.TKroot.update_idletasks()
main_window.TKroot.update()