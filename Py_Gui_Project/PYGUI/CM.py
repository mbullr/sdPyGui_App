#CM.py
# Customer window, paired with basic program CM.BP
# intent is to create a fully (or somewhat fully) functional app to demo (read test) PyGui integration
# Notes:
# All imports happen within the _setup.py script
# We should define windows within a function to ensure objects used during creation (the layout) get garbage collected.
# Because we are running embedded within the sd app and it is possible the sd process could be alive for long periods of
#  time, we should clean up (set to None) any objects created either within the _setup.py or _step.py script.
# Also at some point the sd Python function PY_PYGUISTEP()  (sd_py_gui_step in sdext_py.c) should be passed the name of #  the function defined in the _step.py script (in this example gui_step).  Currently it is hardcoded.
#**************************************************************************
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>
#*************************************************************************


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


# need this known global object to load dropdown lists
MY_CM_LIST = []
MY_CS_LIST = []
STATES_LIST = [
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", 
    "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", 
    "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"
]
CM_STAT_LIST = ['A : Active', 'I : Inactive', 'HS : Hold Shipment', 'HB : Hold Bookings']
CM_TERMS_LIST = ['2/10 Net 30', 'Net 10', 'Net 30', 'Net 45', 'Net 60', 'COD']
# and our table loader lists
#COL_LIST = []
#ROW_LIST = []
CUST_CONTACTS = []
#
# used to check for record changed
ValuesOnGet = {}

# used to read the GUI from the vm
# ie) PY_CALLFUNCTION("readwindow","screen_data","main_window")
# then) window_data = PY_STRGET("screen_data")
screen_data = ""


PUP_window = None
PUP_title = ""
PUP_message = ""
PUP_style = ""
PUP_pending_event =  ""

PY_PUP_OK = "PY_PUP_OK"
PY_PUP_YESNO = "PY_PUP_YESNO"
PY_PUP_OKCANCEL = "PY_PUP_OKCANCEL"

# function to define our popup (cannot use freesimplegui standard pop up (they will be blocking)
# keys to button are always -OK- to proceed, -NO- to not proceed
def create_popup(my_title, my_message,Style):
    if Style == PY_PUP_OK:
        btns = [sg.Button('OK', key='-OK-')]
    elif Style == PY_PUP_YESNO:
        btns = [sg.Button('Yes', key='-OK-'), sg.Button('No', key='-NO-')]
    elif Style == PY_PUP_OKCANCEL:
        btns = [sg.Button('OK', key='-OK-'), sg.Button('Cancel', key='-NO-')]
    else:
       btns = [sg.Button('Yes', key='-OK-'), sg.Button('No', key='-NO-')]
       
    my_layout = [
                  [sg.Text(my_message)],
                   btns
                  ]
    return sg.Window(my_title, my_layout, location=(100, 200), modal=True, finalize=True)
    
  
#
# function to define the main app window

def app_window():
  Frame1_layout = [
  [sg.Text(text='Customer Id',size=(11,1)),sg.Combo("", key='CM_LIST', size=(11,1), readonly=True), sg.Button(button_text='Get',size=(5,1))],
  [sg.Button(button_text='New',size=(5,1))],
  [sg.Text(text='Name',size=(9,1)),sg.Input(size=(29,1),key='CM_NAME')],
  [sg.Text(text='Addr1',size=(9,1)),sg.Input(size=(29,1),key='CM_ADDR')],
  [sg.Text(text='Addr2',size=(9,1)),sg.Input(size=(29,1),key='CM_ADDR2')],
  [sg.Text(text='City, St.',size=(9,1)),sg.Input(size=(21,1),key='CM_CITY'),sg.Combo(size=(8,1),key='CM_STATE',values=STATES_LIST)],
  [sg.Text(text='Zip, Co',size=(9,1)),sg.Input(size=(13,1),key='CM_ZIP'),sg.Input(size=(16,1),key='CM_COUNTRY')],
  [sg.Text(text='AR Limit',size=(9,1)),sg.Input(size=(11,1),key='CM_AR_LIMIT'),sg.Text(text='Terms',size=(5,1)),sg.Combo(size=(11,1),key='CM_TERMS',values=CM_TERMS_LIST)],
  [sg.Text(text='Phone',size=(9,1)),sg.Input(size=(12,1),key='CM_PHONE'),sg.Text(text='Fax',size=(5,1)),sg.Input(size=(12,1),key='CM_FAX')],
  [sg.Text(text='Web Site',size=(8,1)),sg.Input(size=(19,1),key='CM_WEB'),sg.Text(text='Status',size=(6,1)),sg.Combo(size=(11,1),key='CM_STATUS',values=CM_STAT_LIST)],
  [sg.Text(text='Rep',size=(8,1)),sg.Input(size=(19,1),key='CM_REP'),sg.Text(text='ShipTo',size=(6,1)),sg.Text(text='      ',size=(11,1), key = 'CM_DFLT_SHIP_ID') ],
  [sg.Button(button_text='Create ShipTo',size=(7,2), disabled=True)]  
  ] 
  
  frmShipTo_layout = [
  [sg.Text(text='Ship To Id',size=(11,1)),sg.Combo("", key='CS_LIST', size=(11,1)), sg.Button(button_text='Get ShipTo',size=(10,1))],
  [sg.Button(button_text='New Ship To',size=(11,1))],
  [sg.Text(text='Name',size=(5,1)),sg.Input(size=(30,1),key='CS_NAME')],
  [sg.Text(text='Addr1',size=(5,1)),sg.Input(size=(30,1),key='CS_ADDR')],
  [sg.Text(text='Addr2',size=(5,1)),sg.Input(size=(30,1),key='CS_ADDR2')],
  [sg.Text(text='City, St.',size=(9,1)),sg.Input(size=(21,1),key='CS_CITY'),sg.Combo(size=(8,1),key='CS_STATE',values=STATES_LIST)],
  [sg.Text(text='Zip, Co',size=(9,1)),sg.Input(size=(12,1),key='CS_ZIP'),sg.Input(size=(15,1),key='CS_COUNTRY')],
  [sg.Text(text='Phone',size=(9,1)),sg.Input(size=(12,1),key='CS_PHONE'),sg.Text(text='Fax',size=(3,1)),sg.Input(size=(12,1),key='CS_FAX')],
  [sg.Text(text='Status',size=(5,1)),sg.Combo(size=(11,1),key='CS_STATUS',values='')],
  [sg.Button(button_text='Set As Default',size=(12,2))]
  ]
  
  CM_layout = [
  [sg.Frame(size=(260,250),title='',layout = Frame1_layout,expand_x=True,expand_y=True),sg.Frame(title='Ship To',size=(260,250),layout = frmShipTo_layout,expand_x=True,expand_y=True),sg.Menu([['Menu',['Help','About']]])],
  [],
  [sg.Text(text='Customer Contacts',size=(17,1))],
  [sg.Table(headings=['Customer Name', 'Contact Phone', 'Contact Email', 'Contact Fax'],values=[],num_rows=6,key='CM_CONTACT',alternating_row_color="light steel blue",auto_size_columns=False,col_widths=[20, 12, 30,10])],
  [sg.Button(button_text='File',size=(8,1)),sg.Button(button_text='Cancel',size=(8,1)),sg.Button(button_text='Delete Customer',size=(8,2))],
  [sg.Text(text='Status:', key = '-STATUS-',size=(80,1))]
  ] 
  return sg.Window('Customers', CM_layout, size=(860,600),location=(100, 200),  resizable=True,  finalize=True)
  
def read_cm_key(window):
    cm_key = readwindowvalue(window,"CM_LIST")
    return cm_key
    
  
#
# define the all important step function
# this is called by the VM basic program with the function PY_PYGUISTEP()
# Note the py function name "gui_step" is hardcoded into the c function sd_py_gui_step defined in sdext_py.c
#   at some point we should make the function name a parameter, but not today......
def gui_step(max_milliseconds=5):
    # note we must declare as global otherwise our sd functions will not find in global dict 
    global _gui_closed, _close_event_sent, values, PUP_window, ValuesOnGet, PUP_pending_event, PUP_title, PUP_message
    
    

    if _gui_closed:
        return 0

    if not main_window.TKroot.winfo_exists():
        _gui_closed = True
        return 0

    #event, values = window.read(timeout=max_milliseconds)
    window, event, values = sg.read_all_windows(timeout=max_milliseconds)
  
    if event == '__TIMEOUT__':
    # in an actual app we would not pass this event, 
    #    unless you want to see the timeout returns to VM
    #    sd.post_event(event, event)
        pass
    
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

        main_window["-STATUS-"].update('Status: ')

        if event == 'Get':
            # check with we need to warn user
            payload = "Get Click"
            if data_changed(window,ValuesOnGet):
                PUP_title = "Warning"
                PUP_message = "Data Not Saved, Continue?"
                PUP_window =  create_popup(PUP_title, PUP_message,PY_PUP_YESNO)
                PUP_pending_event = event
            else:            
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
        elif event == 'Delete Customer':
            payload = "Delete Customer Click"
            sd.post_event(event,payload)
        # #
        elif event == 'Delete ShipTo':
            payload = "Delete ShipTo Click"
            sd.post_event(event,payload)
        # #
        elif event == 'Create ShipTo':
            payload = "Create ShipTo Click"
            sd.post_event(event,payload)
                
# pop up window event                
    elif window == PUP_window:
        payload = "PUP Click"
        if event == "-OK-":
            # test what the popup was asking about
            sd.post_event(PUP_pending_event,payload)
            window.close()
        else:
            window.close() 
            PUP_window =  create_popup("Notice", "Action Canceled", PY_PUP_OK)
        PUP_pending_event = ""

            
    return 0    
    
    
    
main_window = app_window()
#
# rem print(window.key_dict.keys()) to list keys in window
# dict_keys(['-UNAME-', '-DOB-', '-ACCOUNT-', 'Ok'])
# • Replace all text: Pass a new string into the update() method to clear the old content and show the new text.
# • Append new text: Use window["key"].update("additional text", append=True) to add new lines to the bottom without deleting # existing text.

main_window.TKroot.update_idletasks()
main_window.TKroot.update()