from enum import Enum

# I fucking love Enums (C is peak language)

# different types of messages that can occur in the 
# market channels
class ParserValue(Enum):
    DM = 0
    REQUEST = 1
    OTHER = 2
    UNDEFINED = 3

# the different values that each buy request stores
class SellingData(Enum):
    PRICE = 0
    PLATFORM = 1
    SELLER_ID = 2
    FAIL = 3
    USER_ID = 4

class BuyingData(Enum):
    PRICE = 0
    PLATFORM = 1
    LOCATION = 2
    USER_ID = 3

# Main class for parsing a singular message
# This will parse it, store the information in the fields of buyingData and sellingData
# This is intended to be used as 
# val = MessageParser(msg)
# val.parse()
# then use the data in the fields val.buyingData and val.sellingData 
# all other functions/fields are internal use only (starting with _)
class MessageParser:

    _Platforms = ["gh", "inPerson"]
    _Locations = ["hunan", "exchange"] # TODO: update ts 
    _cache = []
    _MAX_CACHE_LEN = 10

    def __init__(self, msg):
        self.msg = msg
        self.msgType = ParserValue.UNDEFINED
        self.buyingData = dict()
        self.sellingData = dict()

    # just a queue
    def _addToCache(self) -> None:
        if len(MessageParser._cache) >= MessageParser._MAX_CACHE_LEN:
            MessageParser._cache.pop(0)
        MessageParser._cache.append(self)
        
    # evaluate the DM request someone made
    # This will look through the message cache, and update what they 
    # DM'ed for. If there is a previous DM request (i.e two people
    # asked to DM, and this is the second), it will give the request 
    # to the first person, and ignore this one
    def _evalDM(self) -> bool:
        for cacheElem in reversed(MessageParser._cache):
            match cacheElem.msgType:
                case ParserValue.REQUEST: # saw a request first
                    # store all the good shit
                    self.buyingData[SellingData.PRICE] = cacheElem.sellingData[BuyingData.PRICE]
                    self.buyingData[SellingData.PLATFORM] = cacheElem.sellingData[BuyingData.PLATFORM]
                    self.buyingData[SellingData.SELLER_ID] = cacheElem.msg.author.id
                    return True
                case ParserValue.DM:
                    self.buyingData[SellingData.FAIL] = True
                    return False # did not succeed (someone else beat them to it)
                case _:
                    # if its a rando message then just ignore it
                    continue
        return False

    def _strAlmostEqual(self, s1 : str, s2 : str) -> bool:
        len_diff = abs(len(s1) - len(s2))
        if len_diff > 1: return False
        if abs(len(s1) - len(s2)) > 1: return False
        
        s1 = set(s1.lower())
        s2 = set(s2.lower())
        print(f"{s1} {s2}")
        diff = 0
        for char in s1:
            if char not in s2: 
                diff += 1
        return diff <= 1

    def _wordInContainer(self, word : str, container : list[str]) -> tuple[str, bool]:
        for elem in container:
            if self._strAlmostEqual(word, elem):
                return (elem, True)
        return ("Fuck you", False)

    
    def _isWordALocation(self, word : str) -> tuple[str, bool]:
        return self._wordInContainer(word, MessageParser._Locations)
    
    def _isWordAPlatform(self, word : str) -> tuple[str, bool]:
        return self._wordInContainer(word, MessageParser._Platforms)
    
    def _isWordAPrice(self, word : str) -> tuple[float, bool]:
        word = word.lower()
        if word[0] == "$":
            # strip any leading dollar signs
            word = word[1:]
        
        try:
            val = float(word)
            return (val, True)
        except ValueError:
            return (69.420, False)
        
    # The message being parsed is a request 
    # This will extract all of the information about the request, 
    # and store it in the respective fields for the parser

    def _evalRequest(self) -> None:
        
        for word in self.msg.content.lower().split():
            (location, validLocation) = self._isWordALocation(word)
            if validLocation:
                self.sellingData[BuyingData.LOCATION] = location

            (platform, validPlatform) = self._isWordAPlatform(word)
            if validPlatform:
                self.sellingData[BuyingData.PLATFORM] = platform

            (price, validPrice) = self._isWordAPrice(word)
            if validPrice:
                self.sellingData[BuyingData.PRICE] = price

        self.sellingData[BuyingData.USER_ID] = self.msg.author.id


    # This is probably the only external function to be called
    # It will take in a discord message, parse and extract 
    def parse(self) -> None:
        splitMsg = self.msg.content.split()
        if "dm" in splitMsg:
            self.msgType = ParserValue.DM
            self._evalDM()
            self._addToCache()
            return
        # if it mentions the Block-Seller role, then ima just 
        # assume its someone asking to buy a block
        for role in self.msg.role_mentions:
            if role.name == "Block-Seller":
                self.msgType = ParserValue.REQUEST
                self._evalRequest()
                self._addToCache()

