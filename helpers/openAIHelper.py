import os
from openai import OpenAI
from helpers.memoryHelper import Memory
import json

#CONFIGS
os.environ["OpenAI_userKey"] = '## YOUR OPENAI USER KEY ##'
os.environ["OpenAI_Org"] = '## YOUR OPENAI ORG KEY ##'
os.environ["OpenAI_projKey"] = '## YOUR OPENAI PROJECT KEY ##'
fullConversationStr = " "

class OAIHelper: 

    def initConvo():
        try:
            client = OpenAI(
                organization=os.environ["OpenAI_Org"],
                #project=OpenAI_projKey,
                api_key=os.environ["OpenAI_userKey"]
                )
        except RuntimeError:
            print("error initializing OpenAI connection")
        return client


    #Conversation manager
    def conversationHandler(userInput, memories):
        summaryInstructions = """
            The following is a JSON string will summaries of all previous conversations by this user.
            The JSON object includes a TITLE and CONTENT, which should be used. The ID and DATE can be ignored.
            Use this content to help you understand more about what this user cares about, how they structure their questions, and how best to repsond to them.
            
            Here is the entire set of memories

            """ + str(memories) + """
            
            """
        global fullConversationStr
        flag = False
        fullConversationStr += "\n" + userInput + "\n"
        returnStr = OAIHelper.callOpenAIConversation(summaryInstructions + " " + userInput)
        return returnStr
    

    #OpenAI Conversation Helper. Calls OpenAI and streams the results.
    def callOpenAIConversation(UserContent):
        global fullConversationStr
        client = OAIHelper.initConvo()
        dynamicModel = OAIHelper.modelSelectionHelper(UserContent)
        stream = client.chat.completions.create(
            model=dynamicModel,
            messages=[{"role": "user", "content": UserContent}],
            stream=True,)
        returnStr = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                returnStr += content
                fullConversationStr += str(content)
        return returnStr
    

    #Conversation manager
    def summarizeConvo(convoStr):
        summaryInstructions = """
            The following content is the entire converstaion between a user and an AI chat system. This conversation needs to be summarized for long-term memory storage.
            You will return a JSON object with a TITLE and MEMORY.
            The title will be a 1-5 word title for the memory. And the MEMORY will be a 1-4 sentence summary of the converstaion.
            Aim for short, specific words and details. It should not be verbose.
            You will only return a JSON object with a TITLE and MEMORY.
            
            Here is the entire conversation history

            """ + convoStr + """
            
            """
            
        client = OAIHelper.initConvo()
        dynamicModel = OAIHelper.modelSelectionHelper(summaryInstructions)
        stream = client.chat.completions.create(
            model=dynamicModel,
            messages=[{"role": "user", "content": summaryInstructions}],
            stream=True,)
        response = " "
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                response += content
        return response
    

    # gets the full conversation for a session
    def getFullConversation():
        return fullConversationStr
    

    #OpenAI Helper. Decides which model to use for a given prompt.
    def modelSelectionHelper(userPrompt):
        jsonFile = 'json/modelOptions.json'

        # Get the model options.
        try:
            with open(jsonFile, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
                data = [] #creates an empty file

        openAImodels = data["models"]["GPTModels"]
        
        #Set the instructions
        instructions = """
            You are an AI digital assitant that will help with the very first steps of an AI workflow for the user.
            The first thing that needs to be decided is which OpenAI model is best suited for the prompt.
            You will be given the prompt and a set of models to choose from. You will decide which model is best given the data provided and what you already know about the model.
            You will return the modelId string from the JSON object for the model you choose. You will ONLY return the modelId string. Nothing else.

            Here is the full user prompt

            """ + userPrompt + """
            
            And here is the list of available models in JSON form.

            """ + str(openAImodels) + """
            
            """

        client = OAIHelper.initConvo()
        stream = client.chat.completions.create(
            model="gpt-4o-mini", # GPT-4o mini is always used for this first call.
            messages=[{"role": "user", "content": instructions}],
            stream=True,)
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                response += content
        return response