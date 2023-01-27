import xml.etree.ElementTree as et
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import *
import pandas as pd
import sys, os, re

print("NETLIST TRANSLATOR FROM KICAD XML --> CSV...")
xml_file = ''
output_dir = ''
output_path = ''

def parse_XML(xml_path, destination_path):
    #get file contents
    xtree = et.parse(r"{}".format(xml_path))
    xroot = xtree.getroot() 

    # define sheet columns
    df_cols = ["refFrom", "pinFrom", "label","refTo", "pinTo", "Wire Gauge (AWG)", "Color"]
    rows = []
    spliceCount=0

    #iterate through each net connection
    for net in xroot.iter('net'):
        
        label=net.attrib["name"]
        if label[0:4] == "Net-":
            label="  "
        # else:
        #     label=label[1:]

        # check if single route or splice
        if len(net)==2:
            refFrom=net[0].attrib['ref']
            pinFrom=net[0].attrib['pin']
            try:
                pinFuncFrom=net[0].attrib['pinfunction']
            except:
                pinFuncFrom = 'N/A'

            refTo=net[1].attrib['ref']
            pinTo=net[1].attrib['pin']
            try:
                pinFuncTo=net[1].attrib['pinfunction']
            except:
                pinFuncTo = 'N/A'

            color = '  '

            if (re.search("Ground", label) or re.search("GND", label)):
                color = 'BK'
            elif (re.search("PWR", label) or re.search("POWER", label)):
                color = 'RD'

            label = str(pinFuncFrom + ' | ' + label + ' | ' + pinFuncTo)
            
            rows.append({"refFrom": refFrom, "pinFrom": pinFrom,  "label": label,
                            "refTo": refTo, "pinTo": pinTo, "Wire Gauge (AWG)": "20", "Color": color})
            
            label = net.attrib["name"]
            if label[0:4] == "Net-":
                label="  "

        elif len(net)>2:
            spliceCount+=1
            splice="SP%02d" %(spliceCount)
            color = '  '

            if (re.search("GROUND", label) or re.search("GND", label)):
                color = 'BK'

            if (re.search("PWR", label) or re.search("POWER", label)):
                color = 'RD'

            for node in net[0:]:
                refFrom=node.attrib['ref']
                pinFrom=node.attrib['pin']
                refTo=splice
                pinTo=""
                try:
                    pinRef=node.attrib['pinfunction']
                except:
                    pinRef = 'N/A'

                label = str(pinRef + ' | ' + label + ' | ')
                
                rows.append({"refFrom": refFrom, "pinFrom": pinFrom,  "label": label,
                            "refTo": refTo, "pinTo": pinTo, "Wire Gauge (AWG)": "20", "Color": color})
                
                label = net.attrib["name"]
                if label[0:4] == "Net-":
                    label="  "

    # add entry to final df
    wireList_df = pd.DataFrame(rows, columns = df_cols)

    refs=[]
    values=[]

    # iterate through components for references
    for comp in xroot.iter('comp'):
        
            ref=comp.attrib["ref"]
            value=comp.find("value").text
            
            if ref[0]=="J":
                refs.append(ref)
                values.append(value)

    # add references to df
    refs_df=pd.DataFrame({'Names': values,'References': refs})

    #df manipulation (combine df)
    wireList_df.replace({'':"N/A"}, inplace=True)
    wireList_df=wireList_df.reindex(columns=wireList_df.columns.tolist() + ['',' ','  '])
    wireList_df = pd.concat([wireList_df,refs_df], axis=1) 

    # wireList_df.fillna('', inplace=True)
    wireList_df.to_csv(destination_path,index=False)

def browse_xml():
    global xml_file
    xml_file = str(askopenfilename(title='Select XML File!', initialdir=os.path.split(os.path.dirname(__file__))[0]))#"Select xml file to translate..."
    if os.path.exists(xml_file):
        xml_current_path.config(text=xml_file)
    else:
        xml_current_path.config(text="ERROR FINDING FILE PATH")

def browse_output():
    global output_dir, output_path
    output_dir = str(askdirectory(title="Select Output Directory", initialdir=os.path.split(os.path.dirname(__file__))[0]))#"Select the output directory..."
    if os.path.isdir(output_dir):
        output_curr_path.config(text=output_dir)
        output_path = str(os.path.join(output_dir, 'wirelist_translation.csv'))
        if os.path.exists(output_path):
            console.config(text="WARNING: Overriding past translation!!")
    else:
        output_curr_path.config(text="ERROR FINDING FILE PATH")

def qualifier_passthrough():
    global xml_file, output_dir, output_path
    # os.path.exists(xml_file) # should be true
    # os.path.isdir(output_dir) # should be true
    # os.path.exists(output_path) # should be false
    
    if (os.path.exists(xml_file) and os.path.isdir(output_dir)):
        console.config(text="Parsing...")
        parse_XML(xml_file, output_path)
        console.config(text="Sucessfully Exported!")
    else:
        console.config(text="ERROR: either file or output directory path is incorrect")

def gui_exit():
    sys.exit(1)

# create gui window
window=Tk()

# Specify Grid / Scaling
Grid.rowconfigure(window,0,weight=1)
Grid.rowconfigure(window,1,weight=1)
Grid.rowconfigure(window,2,weight=1)
Grid.rowconfigure(window,3,weight=1)

Grid.columnconfigure(window,0,weight=1)
Grid.columnconfigure(window,1,weight=1)
Grid.columnconfigure(window,2,weight=1)
Grid.columnconfigure(window,3,weight=1)

# Create Widgets
output_curr_path = Label(window, text="Select output directory...")
xml_current_path = Label(window, text="Select XML file to translate...")

select_xml_button = Button(window, text="Browse!", command=browse_xml)
select_output_button = Button(window, text="Browse!", command=browse_output)

console = Label(window, text="awaiting user defined paths...")

translate_button = Button(window, text="Translate!", command=qualifier_passthrough)
exit_button = Button(window, text="Exit", command=gui_exit)

# Position Widgets
xml_current_path.grid(row=0, column=0, columnspan=3, sticky="NSEW")
output_curr_path.grid(row=1, column=0, columnspan=3, sticky="NSEW")

select_xml_button.grid(row=0, column=3, sticky="NSEW")
select_output_button.grid(row=1, column=3, sticky="NSEW")

console.grid(row=2, column=0, columnspan=4, sticky="NSEW")

translate_button.grid(row=3, column=2, columnspan=2, sticky="NSEW")
exit_button.grid(row=3, column=0, columnspan=2, sticky="NSEW")

# Window Config
window.title('Wirelist Translator')

# set window size / position
window.geometry("1000x250+300+0")

# run gui (exit on close)
window.mainloop()
sys.exit()