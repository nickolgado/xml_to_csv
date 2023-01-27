import sys
import argparse
import errno
import os
import pandas as pd
import xml.etree.ElementTree as et


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), string)

parser = argparse.ArgumentParser(description="Convert XML to To/From List \n To export from KiCAD, use default exporter kicad_netlist_reader.py",
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("xmlSrcPath", type=file_path, help="path of xml to read")
parser.add_argument("-d", "--destPath", type=dir_path, default=os.getcwd(), help="dest directory of .csv (default: current directory)")

args = vars(parser.parse_args())


xmlPath = args["xmlSrcPath"]
destPath = args["destPath"]


# Below from Jupyter Lab

xtree = et.parse(r"{}".format(xmlPath))
xroot = xtree.getroot() 

df_cols = ["refFrom", "pinFrom", "label","refTo", "pinTo"]
rows = []
spliceCount=0
for net in xroot.iter('net'):
    
    label=net.attrib["name"]
    if label[0:4] == "Net-":
        label=""
    # else:
    #     label=label[1:]

    
    if len(net)==2:
        refFrom=net[0].attrib['ref']
        pinFrom=net[0].attrib['pin']
        refTo=net[1].attrib['ref']
        pinTo=net[1].attrib['pin']
        
        rows.append({"refFrom": refFrom, "pinFrom": pinFrom,  "label": label,
                         "refTo": refTo, "pinTo": pinTo})
    elif len(net)>2:
        spliceCount+=1
        splice="SP%d" %(spliceCount)
        
        for node in net[0:]:
            refFrom=node.attrib['ref']
            pinFrom=node.attrib['pin']
            refTo=splice
            pinTo=""
            
            rows.append({"refFrom": refFrom, "pinFrom": pinFrom,"label": label, 
                         "refTo": refTo, "pinTo": pinTo})

wireList_df = pd.DataFrame(rows, columns = df_cols)

refs=[]
values=[]

for comp in xroot.iter('comp'):
    
        ref=comp.attrib["ref"]
        value=comp.find("value").text
        
        if ref[0]=="J":
            refs.append(ref)
            values.append(value)

refs_df=pd.DataFrame({'Names': values,'References': refs})

wireList_df.replace({'':"N/A"}, inplace=True)

wireList_df=wireList_df.reindex(columns=wireList_df.columns.tolist() + ['',' ','  '])

wireList_df = pd.concat([wireList_df,refs_df], axis=1) 

# wireList_df.fillna('', inplace=True)


# Above from Jupyter Lab


fullDestPath = destPath + r"\wireListExport.csv"
wireList_df.to_csv(fullDestPath,index=False)

print(" \nExported to " + fullDestPath)