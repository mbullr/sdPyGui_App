# sdgui_functions.py
# sd PyGUI common functions module
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
# function to reset window 
import FreeSimpleGUI as sg

SDME_FM  = chr(254)
SDME_VM  = chr(253)
SDME_SVM = chr(252)
SDME_TM =  chr(251)

def reset_form(window):
  for key, element in window.key_dict.items():
    # Reset text inputs to empty or specific defaults
    if isinstance(element, sg.Input) or isinstance(element, sg.Multiline):
      element.update(value="")
    elif isinstance(element, sg.Checkbox):
      element.update(value=False)
    elif isinstance(element, sg.Radio):
      element.update(value=False)
    elif isinstance(element, sg.Combo) or isinstance(element, sg.OptionMenu):
      element.update(value="")
    elif isinstance(element, sg.Spin):
      element.update(value=element.InitialValue)
    elif isinstance(element, sg.Table):
      element.update(values=[])
      
# save current window values
#this does not work as expected, see snapshot_output.txt
#def snapshot(window):
  # Extract live values across all widgets manually without reading the window again
  # see Anatomy of a Dictionary Comprehension to better understand this statement
#  snapshot_values = {
# 1. Target key-value structure
#    key: obj.Values if hasattr(obj, 'Values') else obj.get()
# 2. Source loop
#    for key, obj in window.AllKeysDict.items()
# 3. Inclusion filters
#    if hasattr(obj, 'get') or hasattr(obj, 'Values')
#  }
#  return snapshot_values

# return current window values in dictionary
def snapshot(window):
  # Extract live values across all widgets manually without reading the window again
  skip_keys = {"-STATUS-", "CM_LIST", "CS_LIST"}
  snapshot_values = {}
# Source loop
  for key, obj in window.AllKeysDict.items():
# skip status line
    if key in skip_keys: 
      pass
    else:      
      if hasattr(obj, 'get')or hasattr(obj, 'Values'):
        if isinstance(obj, sg.Table):
#          print(key,':',obj.Values)
          snapshot_values[key] = obj.Values   
        else:        
#          print(key,':',obj.get())
          snapshot_values[key] = obj.get()
          
  return snapshot_values
 
 # return current window values as string (sd dyn array)
def readwindow(window):
    # Extract live values across all widgets manually without reading the window again
  skip_keys = {"-STATUS-", "CM_LIST", "CS_LIST"}
  keys_list   = []
  values_list = []
# Source loop
  for key, obj in window.AllKeysDict.items():
# skip status line
    if key in skip_keys: 
      pass
    else:      
      if hasattr(obj, 'get')or hasattr(obj, 'Values'):
        keys_list.append(key)
        if isinstance(obj, sg.Table):
          # table data is list of lists row list of col lists  
          table_data = obj.Values
          rowdata = []
          for row in table_data:
               coldata = SDME_TM.join(row)
               rowdata.append(coldata)
          table_data = SDME_SVM.join(rowdata)     
          values_list.append(table_data)
                  
        else:        
          values_list.append(obj.get())
  
  dyn_array =  SDME_VM.join(keys_list) +  SDME_FM  + SDME_VM.join(values_list)
  return dyn_array  
  
  # return current window value for specified key as string (sd dyn array)
def readwindowvalue(window,key):
    # Extract live values across all widgets manually without reading the window again
  values_list = []
  obj = window.AllKeysDict.get(key)
  if obj:
    if hasattr(obj, 'get')or hasattr(obj, 'Values'):
      if isinstance(obj, sg.Table):
        # table data is list of lists row list of col lists  
        table_data = obj.Values
        rowdata = []
        for row in table_data:
             coldata = SDME_TM.join(row)
             rowdata.append(coldata)
        table_data = SDME_SVM.join(rowdata)     
        values_list.append(table_data)
                
      else:        
        values_list.append(obj.get())
  
  dyn_array =  SDME_VM.join(values_list)
  return dyn_array 


def data_changed(window,prior_values):
    if prior_values != {}:

#        print('prior_values')
#        for key, value in prior_values.items():
#            print(f"{key}: {value}")
            
        current_values = snapshot(window) 
#        print('current_values')
#        for key, value in current_values.items():
#            print(f"{key}: {value}")
            
        if current_values == prior_values:
            return False
        else:
            return True
    else:
        return False