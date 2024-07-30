from datetime import date
from helpers.memoryHelper import Memory
from helpers.conversationHelper import OAIHelper
import wx, json, os



###
# CLASS FOR GENERATING THE USER EXPERIENCE FOR THE USER
###
class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)
        
        # Set up the panel
        panel = wx.Panel(self)
        
        # Create two columns to manage the layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        hbox.Add(left_sizer, proportion=3, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(right_sizer, proportion=5, flag=wx.EXPAND | wx.ALL, border=10)
        self.text_ctrls = {}
        self.buttons = {}
        
        # Add memory heading
        heading = wx.StaticText(panel, label="My memories")
        left_sizer.Add(heading, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        # Add memory text box
        self.text_ctrls['memories'] = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        left_sizer.Add(self.text_ctrls['memories'], proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Add a button
        self.buttons['saveConvo'] = wx.Button(panel, label="Save conversation to memory")
        left_sizer.Add(self.buttons['saveConvo'], flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Add input heading
        heading = wx.StaticText(panel, label="Hello, what would you like to talk about?")
        right_sizer.Add(heading, flag=wx.ALIGN_CENTER | wx.TOP, border=10)
        
        # Add input text field
        self.text_ctrls['userInput'] = wx.TextCtrl(panel)
        right_sizer.Add(self.text_ctrls['userInput'], proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        # Add LLM router button
        self.buttons['submitStd'] = wx.Button(panel, label="Use standard router")
        right_sizer.Add(self.buttons['submitStd'], flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # Add RouteLLM buttom
        self.buttons['submitRoute'] = wx.Button(panel, label="Use RouteLLM")
        right_sizer.Add(self.buttons['submitRoute'], flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # Add VectorDB buttom
        self.buttons['submitVector'] = wx.Button(panel, label="Use Vector DB")
        right_sizer.Add(self.buttons['submitVector'], flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Add the GPT output text box
        self.text_ctrls['output'] = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        right_sizer.Add(self.text_ctrls['output'], proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Add a button
        self.buttons['fullConvo'] = wx.Button(panel, label="Show full conversation")
        right_sizer.Add(self.buttons['fullConvo'], flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        # Set the sizer for the panel
        panel.SetSizer(hbox)
        
        # Bind the button event
        self.buttons['submitStd'].Bind(wx.EVT_BUTTON, self.startStdConvo)
        self.buttons['submitRoute'].Bind(wx.EVT_BUTTON, self.startRouteConvo)
        self.buttons['submitVector'].Bind(wx.EVT_BUTTON, self.startVectorConvo)        
        self.buttons['saveConvo'].Bind(wx.EVT_BUTTON, self.saveConversationToMemory)
        self.buttons['fullConvo'].Bind(wx.EVT_BUTTON, self.showFullConversation)
        
        # Set the frame size and show it
        self.SetSize((1000, 750))
        self.Show(True)
        MyFrame.loadMemories(self)


###
# CLASS FOR MANAGING USER INTERACTIONS ON THE PAGE
###
class InteractionHandler():
    ###
    # Loads all the memory from long-term storage.
    ###
    def loadMemories(self):
        # Load memories
        memories = Memory.getALLMemories()
        formatted_json = json.dumps(memories, indent=4)
        self.text_ctrls['memories'].SetValue(str(formatted_json))

    ###
    # Uses GPT-4o-mini to specify a model for a prompt
    ###
    def startStdConvo(self, event):
        MyFrame.startConvo(self,event,0)

    ###
    # Uses RouteLLM to define the model for a prompt
    ###
    def startRouteConvo(self, event):  
        MyFrame.startConvo(self,event,1)
    
    ###
    # Uses the vector DB to retrieve a model for a prompt
    ###
    def startVectorConvo(self, event):  
        MyFrame.startConvo(self,event,2)

    ###
    # When a submit button is clicked, this function manages the interaction and calls conversation helper.
    ###
    def startConvo(self, event, convoType):
        # Handle button click event
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        input_text = self.text_ctrls['userInput'].GetValue()
        response = OAIHelper.conversationHandler(input_text, self.text_ctrls['memories'].GetValue(),convoType)
        self.text_ctrls['output'].SetValue(response)
        self.SetCursor(wx.NullCursor)
        self.text_ctrls['userInput'].SetValue("")
        self.text_ctrls['userInput'].SetFocus()

    ###
    # retrieves the full conversation, which has been saved to an environment variable.
    ###
    def showFullConversation(self, event):
        self.text_ctrls['output'].SetValue(os.environ["fullConversationStr"])
    ###
    # Takes the full session conversation and saves it to long-term memory.
    ###
    def saveConversationToMemory(self, event):
        dialog = wx.MessageDialog(self, "Ready to save your conversation to memory?", "Confirm", wx.YES_NO | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        if result == wx.ID_YES:
            self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
            summaryConvo = OAIHelper.summarizeConvo(os.environ["fullConversationStr"])
            if summaryConvo is None:
                    self.SetCursor(wx.NullCursor)
                    wx.MessageBox("Conversation failed to save!", "Info", wx.OK | wx.ICON_INFORMATION)
                    raise ValueError("Failed to summarize conversation")
            elif summaryConvo is not None:
                summaryJSON = json.loads(summaryConvo)
                Memory.putMemory(summaryJSON["TITLE"], summaryJSON["MEMORY"], date.today())
                self.SetCursor(wx.NullCursor)
                wx.MessageBox("Conversation successfully saved!", "Info", wx.OK | wx.ICON_INFORMATION)
            MyFrame.loadMemories(self)
        dialog.Destroy()



if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None, title="Simple GPT app")
    app.MainLoop()