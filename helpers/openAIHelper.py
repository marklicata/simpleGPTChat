import os, json
from openai import OpenAI

#CONFIGS
os.environ["OPENAI_API_KEY"] = '## YOUR OPENAI USER KEY ##'
os.environ["OPENAI_ORG_ID"] = '## YOUR OPENAI ORG KEY ##'
os.environ["fullConversationStr"] = " "

# RouteLLM controller must be imported after OAI keys are set.
from routellm.controller import Controller

class OAIHelper: 

    def initConvo():
        try:
            client = OpenAI(
                organization=os.environ["OPENAI_ORG_ID"],
                api_key=os.environ["OPENAI_API_KEY"]
                )
        except RuntimeError:
            print("error initializing OpenAI connection")
        return client


    #Conversation manager
    def conversationHandler(userInput, memories, convoType):
        summaryInstructions = """
            The following is a JSON string will summaries of all previous conversations by this user.
            The JSON object includes a TITLE and CONTENT, which should be used. The ID and DATE can be ignored.
            Use this content to help you understand more about what this user cares about, how they structure their questions, and how best to repsond to them.
            
            Here is the entire set of memories

            """ + str(memories) + """
            
            """
        os.environ["fullConversationStr"] += "\n" + userInput + "\n"
        
        if convoType == 1:
            returnStr = OAIHelper.callRouteLLMConversation(summaryInstructions + " " + userInput)
        #elif convoType == 2:
            # for using models in a vector db store. Not built yet. 
            ## returnStr = OAIHelper.
        else:
            returnStr = OAIHelper.callOpenAIConversation(summaryInstructions + " " + userInput)

        return returnStr
    

    #OpenAI Conversation Helper. Calls OpenAI and streams the results.
    def callOpenAIConversation(UserContent):
        client = OAIHelper.initConvo()
        dynamicModel = OAIHelper.modelSelectionHelper(UserContent)
        returnStr = dynamicModel + "\n\n"
        os.environ["fullConversationStr"] += dynamicModel + "\n\n"
        stream = client.chat.completions.create(
            model=dynamicModel,
            messages=[{"role": "user", "content": UserContent}],
            stream=True,)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                returnStr += content
                os.environ["fullConversationStr"] += str(content)
        return returnStr
    

    #Summarizes the entire conversation
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
    

    # Uses RouteLLM to determine the model before making a call to OpenAI.
    def callRouteLLMConversation(UserContent):
        try:
            client = Controller(
                        routers=["mf"],
                        strong_model="gpt-4o",
                        weak_model="gpt-4o-mini"
            )
        except RuntimeError:
            print("error initializing RouteLLM client")

        stream = client.chat.completions.create(
            model="router-mf-0.11593",
            messages=[{"role": "user", "content": UserContent}],
            stream=True,)
        returnStr = stream.model + "\n\n"
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                returnStr += content
                os.environ["fullConversationStr"] += str(content)
        return returnStr