"""
The MIT License (MIT)

Copyright (c) 2014 Jean-Philippe Jodoin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import os, collections
from xml.dom import minidom
import codecs
import csv
from OrderedSet import OrderedSet

def unescapeAndroidChar(text):
  text = text.replace("\\'", '\'')
  return text

# Reconstruct this element's body XML from dom nodes
def getChildXML(elem):
    out = ""
    for c in elem.childNodes:
        if c.nodeType == minidom.Node.TEXT_NODE:
            out += c.nodeValue
        else:
            if c.nodeType == minidom.Node.ELEMENT_NODE:
                if c.childNodes.length == 0:
                    out += "<" + c.nodeName + "/>"
                else:
                    out += "<" + c.nodeName + ">"
                    cs = ""
                    cs = getChildXML(c)
                    out += cs
                    out += "</" + c.nodeName + ">"
    return out

defaultLangage = input("Default langage ISO-639-1 code. (write en if your default langage is english):")
pathToProject = input("Path to Android project file:")
outputFilepath = input("Path to CSV file (output):")

ressourcePath = os.path.join(pathToProject,"res")
folderList = os.listdir(ressourcePath)
langageDict = dict()
for f in folderList:
  if f.startswith("values"):
    lang = defaultLangage
    tmp = f.split("-")
    if len(tmp) == 2:
      lang = tmp[1]
    print(lang)
    if lang == 'v31' or lang == 'night':
      continue
    langageDict[lang] = dict()
    stringsDict = langageDict[lang]
    valuesPath = os.path.join(ressourcePath,f)
    if os.path.isdir(valuesPath):
      filePath = os.path.join(valuesPath, "strings.xml")
      if os.path.exists(filePath):
        #Open String XML
        print(filePath)
        xmldoc = minidom.parse(filePath)
        rootNode = xmldoc.getElementsByTagName("resources")
        if len(rootNode) == 1:          
          nodeList = rootNode[0].childNodes
          for n in nodeList:
            attr = n.attributes
            if attr != None:
              tag = n.tagName
              if tag == 'string':
                key = attr['name'].nodeValue
                value = getChildXML(n)
                stringsDict[key] = value.strip()
                #print(key + " = " + value)
              elif tag == 'string-array':
                name = attr['name'].nodeValue
                itemList = n.getElementsByTagName("item")
                for idx, item in enumerate(itemList):
                  key = str(name)+","+str(idx)
                  value = item.childNodes[0].nodeValue
                  #print(key + " = " + value)
                  stringsDict[key] = value.strip()
              else:
                print("Unknown node")
        else:
          print('Invalid ressource file. We expect a ressources node')
        #for s in itemlist :          
          #print(s)

#Get all key list
uniqueKeys = set()
for k in langageDict:
  stringsDict = langageDict[k]
  for keys in stringsDict:
    uniqueKeys.add(keys)
uniqueKeys = OrderedSet(sorted(uniqueKeys))
#Write CSV
with codecs.open(outputFilepath, 'w', "utf-8") as f:
  writer = csv.writer(f)
  header = ["key"]
  header.extend(list(langageDict.keys()))
  writer.writerow(header)
  for key in uniqueKeys:
    langStrings = [key]
    for lang in langageDict:
      stringsDict = langageDict[lang]
      if key in stringsDict:
        langStrings.append(unescapeAndroidChar(stringsDict[key]))
      else:
        langStrings.append(" ") 
    writer.writerow(langStrings)  
