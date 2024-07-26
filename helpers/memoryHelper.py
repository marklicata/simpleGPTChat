import json, datetime

jsonFile = 'json/memories.json'

class Memory:
    
    # OPENS THE MEMORY JSON FILE
    def openJSON():
        try:
            with open(jsonFile, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
                data = [] #creates an empty file
        return data
    
    # RETURNS A LIST OF MEMORIES IN THE JSON
    def getALLMemories():
        data = Memory.openJSON()
        return data["memories"]["memoryList"]
    
    # RETURNS 1-N MEMORIES THAT CONTAIN A GIVEN STRING
    def getMemory(str):
        data = Memory.openJSON()
        subList = {"memories":[]}
        for mem in data["memories"]["memoryList"]:
            if str in mem["title"] or str in mem["content"]:
                subList["memories"].append(mem)
        return subList
    
    # ADDS A NEW MEMORY TO THE JSON
    def putMemory(topic, content, date):
        data = Memory.openJSON()
        
        #create the new ID
        count = len(data["memories"]["memoryList"]) + 1

        #define the new memory
        newMemory = {
            "id":str(count),
            "title":topic,
            "content":content,
            "date":str(date)
            }
        
        #add new data to file
        data["memories"]["memoryList"].append(newMemory)
        with open(jsonFile, "w") as file:
            json.dump(data, file)
            file.close()

    # DELETES A SINGLE MEMORY FROM THE JSON
    def deleteMemoryById(_id):
        data = Memory.openJSON()
        memoryList = data["memories"]["memoryList"]
        for mem in memoryList:
            if _id == mem["id"]:
                data["memories"]["memoryList"].remove(mem)
                break
        with open(jsonFile, "w") as file:
            json.dump(data, file)
            file.close()

    # SCRUBS THE MEMORY OLD ENTRIES AND DELETES
    def memoryScrubber(deleteDate):
        data = Memory.openJSON()
        memoryList = data["memories"]["memoryList"]
        
        # Ensure deleteDate is a datetime.date object
        if isinstance(deleteDate, datetime):
            deleteDate = deleteDate.date()
        
        for mem in memoryList:
            memoryDate = datetime.strptime(mem["date"], '%Y-%m-%d').date()
            if memoryDate <= deleteDate:
                Memory.deleteMemoryById(mem["id"])
