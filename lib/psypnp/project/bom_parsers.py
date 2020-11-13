'''
Created on Nov 5, 2020

@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
'''


from psypnp.csv_file import BOMParserGeneric, BOMParserColumnMap

class BOMParserKicad(BOMParserGeneric):
    ''' 
        This is a sample BOM parser -- you can use this, make your own, 
        or fit the BOM to the schema

        #Item, Qty, Reference(s), Value, LibPart, Footprint
        
        
        This is (just one of oh-so-many) ways kicad can produce.  It's pretty
        easy to just make your own type by following this example to customize 
        your own processing.
        
    '''
    # we're going to call our parent super().__init__ but need 
    # couple of setup objects first
        
    # Converters for columns.
    # Columns are:
    #    Item, Qty, Reference(s), Value, LibPart, Footprint
    # we want to make sure:
    #  - qty and
    #  - footprint 
    # are massaged into shape, set by position, using None when
    # no converter required.
    # these converters are called for each row with enough fields 
    
    
    def __init__(self, filepath, delimiter=',', 
                 ignoreCommentedFirstLine=True):
        converters = [
            None,
            self.convertQty,  # Qty
            None,
            None,
            None,
            self.convertFootprint  # footprint -- want to extract package from that
        ]
        
        # mapping of columns (0-indexed)
        colmap = BOMParserColumnMap(quantity=1,
                                      references=2,
                                      value=3,
                                      package=5
                                      )
        # ok, init which will trigger everything else
        super(BOMParserKicad, self).__init__(filepath, converters, colmap, delimiter, ignoreCommentedFirstLine)
    
    
    
    def convertQty(self, v):    
            try: 
                retval = int(v)
            except:
                retval = -1
            return retval
            
    def convertFootprint(self, v):
        # my package is burried in the footprint field... 
        # kicad gives me LIBRARY:PKG_FOOTPRINT, like
        #  Package_TO_SOT_SMD:SOT-23-5
        # so we use this as one of the "converters"
        # simplest thing would be to return element[1], but this example
        # shows the post process.
        if v is None or not len(v):
            return ('DNP', 'DNP', False)
            
        comps = v.split(':')
        if comps and len(comps):
            if len(comps) == 2:
                return (comps[0], comps[1], True)
            return comps
        return (v, v, False)
    def postProcessEntries(self):
        # after all rows processed, they've been through any 
        # converters we set and are in a list: self.entries[]
        # so let's clean up our package data
        for ent in self.entries:
            if len(ent.package) == 3:
                ent.package = ent.package[1]

            


if __name__ == "__main__":
    import psypnp.repl
    # debugging assist... just run this module on command line
    bparser = BOMParserKicad("/tmp/bom.csv")
    v = dict()
    v['bom_parser'] = bparser
    psypnp.repl.runInterpreter(v)

