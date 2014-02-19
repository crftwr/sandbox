from lxml import etree
import difflib

class ElementAndDepth:

    def __init__( self, elm, depth ):
        self.elm = elm
        self.depth = depth
    
    def __eq__(self,other):
        return ( self.elm.tag == other.elm.tag 
             and self.elm.text == other.elm.text 
             and self.elm.attrib == other.elm.attrib )
    
    def __hash__(self):
        h = hash(self.elm.tag)
        if self.elm.text:
            h += hash(self.elm.text)
        for key, value in self.elm.attrib.iteritems():
            h += hash(key) + hash(value)
        return hash(h)

def eachElement( elm, depth ):

    yield ElementAndDepth(elm, depth)

    for child_elm in elm.getchildren():

        for elm_and_depth in eachElement( child_elm, depth+1 ):
            yield elm_and_depth

def docToElmList(doc):
    
    elm_list = []
    
    root_elm = doc.getroot()
    for elm_and_depth in eachElement( root_elm, 0 ):
        #print "  " * elm_and_depth.depth + elm_and_depth.elm.tag
        elm_list.append( elm_and_depth )
    
    return elm_list

original_doc = etree.parse("./original.html")
modified_doc = etree.parse("./modified.html")

original_elm_list = docToElmList(original_doc)
modified_elm_list = docToElmList(modified_doc)

sequence_matcher = difflib.SequenceMatcher( None, original_elm_list, modified_elm_list )

print "%3.2f%% match" % sequence_matcher.ratio()

for tag, i1, i2, j1, j2 in sequence_matcher.get_opcodes():
    print ("%7s a[%d:%d] b[%d:%d]" % (tag, i1, i2, j1, j2))

