'''
Created on Oct 14, 2020

CSV file utils.  General CSV stuff, as well as BOM, Feed Description and Package Description CSV file parsers used by auto-setup system.


@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/


Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

import csv as csv_module
import psypnp.repl
import psypnp.debug



class CSVFile:
    ''' 
    CSVFile
    @summary: basic CSV file parser with useful additions for type conversions/processing.
    
    This class is used by the more specific csv file readers, below, by composition so we
    can avoid dealing with the various python2/3 issues related to super()/inheritance.
    '''
    def __init__(self, filepath, delimiter=',', 
                 ignoreCommentedFirstLine=True):
        self.success = False 
        self.delimiter = delimiter
        self.filename = filepath
        
        self._contents = []
        try:
            f = open(filepath, 'r')
        except:
            print("Can't open %s " % filepath)
            return 
        
        if f is None or not f:
            return
        
        
        try:
            rdr = csv_module.reader(f, delimiter=delimiter)
        except:
            print("Issue reading csv %s " % filepath)
            return 
        
        for aline in rdr:
            if aline and len(aline):
                if len(self._contents) == 0 \
                  and ignoreCommentedFirstLine:
                    hashsearch = aline[0].find('#')
                    if hashsearch >= 0 and hashsearch < 2:
                        ignoreCommentedFirstLine = False
                    else:
                        self._contents.append(aline)
                else:
                    self._contents.append(aline)
        if len(self._contents):
            self.success = True
            
        f.close()
        
    def numRows(self):
        return len(self._contents)
            
            
    def convertToInt(self, v):
        ''' convertToInt
            @return:  v as an int, if possible, -1 otherwise.
        '''
        try: 
            retval = int(v)
        except:
            retval = -1
        
        return retval
    
    def convertToFloat(self, v):
        ''' convertToFloat
            @return:  v as an float, if possible, -1 otherwise.
        '''
        try: 
            retval = float(v)
        except:
            retval = -1
        
        return retval
    
    def processThroughConverters(self, aRow, convertersList):
        '''
            called for a given CSV file row, along with a
            list of converters (None entries ignored).
            This allows useful type conversions over the entire
            file, easily, through processEachRow()
        '''
        retRow = []
        if not aRow or not len(aRow):
            return retRow
        numConv = len(convertersList)
        for i in range(len(aRow)):
            v = aRow[i]
            if i < numConv and convertersList[i]:
                v = convertersList[i](aRow[i])
            
            retRow.append(v)
        
        return retRow
    
    def processEachRow(self, throughCallback, converters=None):
        '''
            process each row in the CSV through a given
            callback, after processing through any converter 
            functions provided.
        '''
        for anEntry in self._contents:
            if converters is not None and len(converters):
                anEntry = self.processThroughConverters(anEntry, converters)
            throughCallback(anEntry)


class PackageDescRow:
    def __init__(self, name, width=0, pitch=0, tapetype='', comments=''):
        self.name = name
        self.width = width 
        self.pitch = pitch 
        self.tapetype = tapetype
        self.comments = comments
        
    def __string__(self):
        return '%s (%i/%i)' % (self.name, self.width, self.pitch)
    
    def __repr__(self):
        return '<PackageDescRow %s>' % self.__string__()
    
        

class PackageDescCSV:
    ''' 
        A CSV describing component packages.
        CSV format 
        # package,    width,     pitch,    tape type (black|white|clear)
    '''
    def __init__(self, filepath, delimiter=',', 
                 ignoreCommentedFirstLine=True):
        self.csv = CSVFile(filepath, delimiter, ignoreCommentedFirstLine)
        
        self.packages = dict()
        converters = [
            None, 
            self.csv.convertToInt,
            self.csv.convertToInt
        ]
        if self.csv.success:
            self.csv.processEachRow(self.parsePackages, converters)   
        
        
    
    def isOK(self):
        return self.csv.success
    
    def parsePackages(self, anEntry):
        aPkg = PackageDescRow(*anEntry)
        if aPkg.name is not None and len(aPkg.name):
            self.packages[aPkg.name] = aPkg
            
    def numEntries(self):
        return len(self.packages)
            
    def entries(self):    
        return [self.packages[i] for i in self.packages]
    
    
    
    
    def findFor(self, bomEntry):
        full_package = bomEntry.package
        if full_package is None or not len(full_package):
            return None
        for pkg in self.entries():
            if full_package.find(pkg.name) >= 0:
                return pkg
        return None
            
    def __string__(self):
        return 'description from "%s" with %i packages' % (
                        self.csv.filename,
                        self.numEntries())
        
    def __repr__(self):
        return '<PackageDescCSV %s>' % self.__string__()
            
class FeedDescRow:
    def __init__(self, name, width=0, length=0, enabled=True, comments=''):
        self.name = name
        self.width = width 
        self.length = length 
        self.enabled = enabled
        self.comments = comments
        
        
    def canCarry(self, aPackage):
        if aPackage is None or not hasattr(aPackage, 'width'):
            return False
        
        return self.width == aPackage.width
    
    
    
    
    def holdsUpTo(self, aPackage):
        if not self.canCarry(aPackage):
            return 0 
        
        if aPackage is None or not hasattr(aPackage, 'pitch'):
            return 0
        
        if self.length < 1:
            psypnp.debug.out.buffer('Feed description length 0: assuming reel (10k parts held)')
            return 10e3
        
        return int(self.length / aPackage.pitch)
    
            
    def __string__(self):
        return '%s (%i @ %i)' % (self.name, self.length, self.width)
    
    def __repr__(self):
        return '<FeedDescRow %s>' % self.__string__()
    
        
        
        
class FeedDescCSV:
    ''' 
       Feeds available description CSV.  Expecting format
       # Feedname,    width (mm),    length (mm), ENABLED, comment
       
       where "feedname" is to be some matchable substring of system feed names, e.g.
        8mm
       matching
        8mmRight_01, 8mmRight_02... 8mmLeft_14, etc
        
       width is width of tape supported, length is physical length for strip.
    '''
    def __init__(self, filepath, delimiter=',', 
                 ignoreCommentedFirstLine=True):
        psypnp.debug.out.buffer('Opening feed desc file %s' % filepath)
        self.csv = CSVFile(filepath, delimiter, ignoreCommentedFirstLine)
        
        self.feeds = dict()
        converters = [
            None, 
            self.csv.convertToInt,
            self.csv.convertToInt,
            self.convertEnabled
        ]
        if self.csv.success:
            self.csv.processEachRow(self.parseFeeds, converters)   
        
        
    
    
    def convertEnabled(self, v):
        ''' convertEnabled
            @return:  v as a bool
        '''
        if v is None or v == '':
            return True # enabled by default/mere presence
        
        if len(v) and v.lower() == '0' or v.lower() == 'false':
            return False
        
        return True 
        
    def isOK(self):
        return self.csv.success
    
    def parseFeeds(self, anEntry):
        aFeed = FeedDescRow(*anEntry)
        if aFeed.name is not None and len(aFeed.name):
            if aFeed.enabled:
                psypnp.debug.out.buffer('Have feed description for %s.'
                                         % aFeed.name);
                self.feeds[aFeed.name] = aFeed
            else:
                psypnp.debug.out.buffer('Have feed desc %s but is DISABLED. Skip.'
                                         % aFeed.name);
                                         
        psypnp.debug.out.flush()
            
    def findFor(self, aPackage):
        availableFeeds = []
        if aPackage is None:
            return availableFeeds
        
        for f in self.feeds:
            if f.enabled and self.feeds[f].canCarry(aPackage):
                availableFeeds.append(self.feeds[f])
        
        return availableFeeds
    
    def entries(self):
        return [self.feeds[i] for i in self.feeds]
    
    def numEntries(self):
        return len(self.feeds)
        
    def __string__(self):
        return 'description from "%s" with %i feeds' % (
                        self.csv.filename,
                        self.numEntries())
        
    def __repr__(self):
        return '<FeedDescCSV %s>' % self.__string__()
    
            
class BOMEntry:
    def __init__(self, references, qty, footprint_package, value=None):
        self.references = references
        self.quantity = qty 
        self.package = footprint_package
        self.value = value 
        self.ignore = False
        
    def shortReferences(self):
        refs = self.references.replace(' ', '')
        if refs is not None and len(refs) > 7:
            refs = refs[:6] + '...'
            
        return refs
        
    def __string__(self):
        refs = self.shortReferences()
        return "\"%s\" %i\t%s\t%s" % (
            refs,
            self.quantity,
            str(self.package), 
            self.value)
        
    def __repr__(self):
        return '<BOMEntry %s >' % self.__string__()
        
        

class BOMParserColumnMap:
    def __init__(self, quantity, package, value, references=None):
        self.col_quantity = quantity
        self.col_package = package
        self.col_value = value 
        self.col_references = references 
        
        v = [quantity, package, value]
        if references is not None:
            v.append(references)
            
        self.min_columns = sorted(v)[-1] + 1
        
        
    def minimumNumColumns(self):
        return self.min_columns
    
    def hasReferences(self):
        return self.col_references is not None 
    
class BOMParserBase(object):
    ''' 
        Project BOM parser, kicad version.  Expects CSV of format:
        #Item, Qty, Reference(s), Value, LibPart, Footprint
    '''
    def __init__(self, filepath, 
                 convertersList,
                 columnMap,
                 delimiter=',', 
                 ignoreCommentedFirstLine=True):
        
        self.columnMap = columnMap
        self.csv = CSVFile(filepath, delimiter, ignoreCommentedFirstLine)
        
        self.success = self.csv.success
        self.entries = []
        if self.csv.success:
            self.csv.processEachRow(self.parseBOMEntries, convertersList)   
            self.postProcessEntries()
            
    def postProcessEntries(self):
        pass 
    
    def numEntries(self):
        return len(self.entries)
    
    
    
    def parseBOMEntries(self, anEntry):
        bEntry = None
        if anEntry:
            pkg = None
            if len(anEntry) >= 6:
                pkg = anEntry[5]
                if len(pkg) == 3:
                    pkg = pkg[1]
                    
            if len(anEntry) >= self.columnMap.minimumNumColumns():
                
                bEntry = BOMEntry(
                    anEntry[self.columnMap.col_references], # references
                    anEntry[self.columnMap.col_quantity],# qty,
                    anEntry[self.columnMap.col_package], # package 
                    anEntry[self.columnMap.col_value]# value
                    
                    )
            
        if bEntry is not None:
            self.entries.append(bEntry)
            
            
class BOMParserGeneric(BOMParserBase):
    pass
            

        
class BOMCSV:
    ''' BOMCSV
        CSV file for project BOM, using specific parser type to do the dirty work.
        Only BOMParserKicad currently supported.  
        Example use:
           bom_csv = BOMCSV("/tmp/bom.csv", BOMParserKicad)
    '''
    def __init__(self, filepath, bomParserType, delimiter=',', 
                 ignoreCommentedFirstLine=True):
        self.parser = bomParserType(filepath, delimiter, ignoreCommentedFirstLine)
        self.filename = filepath
        
    def isOK(self):
        return self.parser.csv.success
    
    def entries(self):
        return self.parser.entries
    
    def numEntries(self):
        return self.parser.numEntries()
    
    def __string__(self):
        return 'BOM for "%s" with %i entries' % (
                        self.filename,
                        self.numEntries())
        
    def __repr__(self):
        return '<BOMCSV %s>' % self.__string__()
    

if __name__ == "__main__":
    # debugging assist... just run this module on command line
    from psypnp.project.bom_parsers import BOMParserKicad
    bom_csv = BOMCSV("/tmp/bom.csv", BOMParserKicad)
    package_csv = PackageDescCSV("../data/package_desc.csv")
    feed_csv = FeedDescCSV('../data/feed_desc.csv')
    v = psypnp.repl.getStandardEnvVars()
    v['bom_csv'] = bom_csv
    v['package_csv'] = package_csv
    v['feed_csv'] = feed_csv
    
    psypnp.repl.runInterpreter(v)
        
