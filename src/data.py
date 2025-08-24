import json
from enum import Enum
from parser import *
from datetime import date
import threading
import time

class BuyingValues(Enum):
    BOUGHT_HISTORY = 0
    AVERAGE_BOUGHT_PRICE = 1
    TOTAL_BOUGHT_BLOCKS = 2


class SellingValues(Enum):
    SELLING_HISTORY = 0
    TOTAL_SOLD_BLOCKS = 1
    AVERAGE_SELLING_PRICE = 2



class BlockData:

    _buyingData = dict()
    _sellingData = dict()
    _lock = threading.Lock()

    def _init_selling(userID) -> None:
        
        BlockData._sellingData[userID] = dict()
        userSellingData = BlockData._sellingData[userID]
        userSellingData[SellingValues.SELLING_HISTORY] = []
        userSellingData[SellingValues.AVERAGE_SELLING_PRICE] = None
        userSellingData[SellingValues.TOTAL_SOLD_BLOCKS] = 0

    def _init_buying(userID) -> None:

        BlockData._buyingData[userID] = dict()
        userBuyingData = BlockData._buyingData[userID]
        userBuyingData[BuyingValues.BOUGHT_HISTORY] = []
        userBuyingData[BuyingValues.AVERAGE_BOUGHT_PRICE] = None
        userBuyingData[BuyingValues.TOTAL_BOUGHT_BLOCKS] = 0


    def _loadData() -> None:
        with open("data/buying.json", "r") as buyingDataF:
            rawBuyingData = json.load(buyingDataF)
            BlockData._buyingData = {BuyingValues[key]: val for key, val in rawBuyingData.items()}
        with open("data/selling.json", "r") as sellingDataF:
            rawSellingData = json.load(sellingDataF)
            BlockData._sellingData = {SellingValues[key]: val for key, val in rawSellingData.items()}

    def storeData(data : MessageParser) -> None:

        with BlockData._lock:
            if (not BlockData._buyingData) or (not BlockData._sellingData):
                BlockData._loadData()
            
            userID = data.msg.author.id
            if userID not in BlockData._buyingData:
                BlockData._init_buying(userID)

            if userID not in BlockData._sellingData:
                BlockData._init_selling(userID)

            userBuyingData = BlockData._buyingData[userID]
            userSellingData = BlockData._sellingData[userID]
            
            # if the user tried to buy a block
            if data.buyingData:
                userBuyingData[BuyingValues.BOUGHT_HISTORY].append(data.buyingData)
                if userBuyingData[BuyingValues.AVERAGE_BOUGHT_PRICE]:
                        oldAvg = userBuyingData[BuyingValues.AVERAGE_BOUGHT_PRICE]
                        oldCount = userBuyingData[BuyingValues.TOTAL_BOUGHT_BLOCKS]
                        newVal = data.buyingData[BuyingData.PRICE]
                        userBuyingData[BuyingValues.AVERAGE_BOUGHT_PRICE] = ((oldAvg * oldCount) + newVal) / (oldCount + 1)
                else:
                    userBuyingData[BuyingValues.AVERAGE_BOUGHT_PRICE] = data.buyingData[BuyingData.PRICE]
                
                userBuyingData[BuyingValues.TOTAL_BOUGHT_BLOCKS] += 1

            if data.sellingData:
                userSellingData[SellingValues.SELLING_HISTORY].append(data.sellingData)
                if userSellingData[SellingValues.AVERAGE_SELLING_PRICE]:
                    oldAvg = userSellingData[SellingValues.AVERAGE_SELLING_PRICE]
                    oldCount = userSellingData[SellingValues.TOTAL_SOLD_BLOCKS]
                    newVal = data.buyingData[SellingData.PRICE]
                    userSellingData[SellingValues.AVERAGE_SELLING_PRICE] = ((oldAvg * oldCount) + newVal) / (oldCount + 1)
                else:
                    userSellingData[SellingValues.AVERAGE_SELLING_PRICE] = data.sellingData[SellingData.PRICE]

                userSellingData[SellingValues.TOTAL_SOLD_BLOCKS] += 1


def stringify_enums(obj : dict) -> dict:
    if isinstance(obj, dict):
        return { (k.name if isinstance(k, Enum) else k): stringify_enums(v)
                 for k, v in obj.items() }
    elif isinstance(obj, list):
        return [stringify_enums(elem) for elem in obj]
    else:
        return obj

STORING_THREAD_LOCK_TIME = 60
def dataMain() -> None:
    while True:
        time.sleep(STORING_THREAD_LOCK_TIME)

        with BlockData._lock:
            stringifiedBuyingData = {userID: stringify_enums(userData)
                                    for userID, userData in BlockData._buyingData.items()}
            
            stringifiedSellingData = {userID: stringify_enums(userData)
                                    for userID, userData in BlockData._sellingData.items()}

            print(f"{stringifiedBuyingData} {stringifiedSellingData}")

            with open("data/buying.json", "w") as buyingF:
                json.dump(stringifiedBuyingData, buyingF, indent=4)
            with open("data/selling.json", "w") as sellingF:
                json.dump(stringifiedSellingData, sellingF, indent=4)
