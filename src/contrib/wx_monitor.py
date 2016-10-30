#!python
# -----------------------------
# Name:     PyPubSubMonitor
# Purpose:  A pubsub activity monitor
#
# Author:   Josh English
#
# Date:     20-Aug-2008
# Last Rev: 127 (Last revision this code was checked with)
# -------------------------------------

# NOTE: The Tool and Mixin components (including the
# docstrings) borrow heavily on Robin Dunn's wxInspectionTool

### Next problem: TreeCtrl doesn't send messages...
import wx
from pubsub import pub
import pubsub.utils as utils
from pubsub import pubsubconf as conf

conf.setNotifierClass(utils.NotifyByPubsubMessage)
pub.setNotificationFlags(all=True)


### MonitorTopics
###  Three topics for Pypubsub messages to control the monitor
class MonitorTopics(utils.TopicTreeDefnSimple):
    class monitor:
        """Messages controlling the monitor"""

        class show:
            """Shows or hides the monitor"""
            show = "Boolean value to show (True) or hide (False) the monitor"
            _required = ('show',)

        class hide:
            """Hides the monitor. Same as message ('monitor.show', show=False)"""

        class toggle:
            """Toggles the monitor to be shown or hidden"""


pub.addTopicDefnProvider(MonitorTopics())


class MonitorTool:
    """
    The MonitorTool is a singleton based on the
    wx.lib.inspection.InspectionTool.
    """
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'initialized'):
            self.initialized = False
        pub.subscribe(self.Show, 'monitor.show')
        print
        "Made Monitor Tool"
        tobj = pub.getTopic('monitor.show')
        print
        tobj

    def Init(self, app=None):
        self._frame = None
        self._app = app
        if not self._app:
            self._app = wx.GetApp()
        self.initialized = True
        print
        "Monitor Tool Init"

    def Show(self, show):
        print
        "Monitor Tool Show"
        if not self.initialized:
            self.Init()

        parent = self._app.GetTopWindow()
        if not self._frame:
            self._frame = MonitorFrame(parent=parent)
        self._frame.Show(show)


class MonitorMixin(object):
    """
    This class is intended to be used as a mix-in with the wx.App
    class.  When used it will add the ability to popup a
    MonitorFrame window.  The default key sequence to activate the inspector is
    Ctrl-Alt-M (or Cmd-Alt-M on Mac) but this can be changed via
    parameters to the `Init` method, or the application can call
    `ShowInspectionTool` from other event handlers if desired.

    To use this class simply derive a class from wx.App and
    MonitorMixin and then call the `Init` method from the app's
    OnInit.
    """

    def Init(self, alt=True, cmd=True, shift=False, keycode=ord('M')):
        self.Bind(wx.EVT_KEY_DOWN, self._OnKeyPress)
        self._alt = alt
        self._cmd = cmd
        self._shift = shift
        self._keycode = keycode
        MonitorTool().Init(self)
        print
        "Mixin Init"

    def _OnKeyPress(self, evt):
        if evt.AltDown() == self._alt and \
                        evt.CmdDown() == self._cmd and \
                        evt.ShiftDown() == self._shift and \
                        evt.GetKeyCode() == self._keycode:
            self.ShowMonitorTool()
        else:
            evt.Skip()

    def ShowMonitorTool(self):
        print
        "Mixin Show"
        MonitorTool().Show(True)


class MonitorFrame(wx.Frame):
    """MonitorFrame
    This is the main monitor frame. Interaction between varying panels
    is done through direct method calls to prevent message clutter
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(700, 600), title="PyPubSubMonitor")
        panel = wx.Panel(self)
        splitter = wx.SplitterWindow(panel, style=wx.SP_BORDER)

        self.NotifyControl = NotifierPanel(panel)
        self.TopicTree = TopicTreePanel(splitter)
        self.Log = LogPanel(splitter)
        self.Entry = LastLogEntryPanel(panel)
        self.Count = CountPanel(panel)

        ##        redirect = Redirector(self.Log.getText())
        self.Logger = MonitorLogger(pub, self.Log)

        pub.subscribe(self.psUpdate, pub.ALL_TOPICS)
        pub.subscribe(self.psShow, 'monitor.show')
        pub.subscribe(self.psHide, 'monitor.hide')
        pub.subscribe(self.psToggle, 'monitor.toggle')

        sizer = wx.BoxSizer(wx.VERTICAL)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.NotifyControl, 0, wx.EXPAND | wx.ALL, 3)

        splitter.SetMinimumPaneSize(20)
        splitter.SetSashGravity(0.5)
        splitter.SplitVertically(self.TopicTree, self.Log, 0)

        row.Add(splitter, 1, wx.EXPAND | wx.GROW | wx.ALL, 3)
        sizer.Add(row, 1, wx.EXPAND | wx.GROW | wx.ALL, 3)
        sizer.Add(self.Entry, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.Count, 0, wx.EXPAND | wx.ALL, 3)
        panel.SetSizerAndFit(sizer)
        self.Layout()
        self.Refresh()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        print
        "Frame Init"

    def OnClose(self, evt):
        """Turn off notifications before closing down
        """
        pub.setNotificationFlags(all=False)
        evt.Skip()

    def psShow(self, show): self.Show(bool(show))

    def psHide(self): self.Hide()

    def psToggle(self): self.Show(not self.IsShown())

    def psUpdate(self, msgTopic=pub.AUTO_TOPIC):
        self.Entry.SetMessage(self.Logger.lastMsg.strip())
        self.Entry.SetTopic(self.Logger.lastTopic)
        self.Entry.SetPSTopic(self.Logger.lastLogTopic.getName())
        self.Count.count(self.Logger.lastLogTopic.getName())


class NotifierPanel(wx.Panel):
    """NotifierPanel
    Seven toggle buttons to control which kinds of messages the
    monitor will pay attention to.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, name="notifier control")
        box = wx.StaticBox(self, label="Notifiers")

        allBtn = wx.ToggleButton(self, label="all")
        allBtn.SetValue(True)
        allBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnNotifyAll)

        self.subBtn = wx.ToggleButton(self, label="subscribe")
        self.subBtn.SetValue(True)
        self.subBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnSubscribe)

        self.unsubBtn = wx.ToggleButton(self, label="unsubscribe")
        self.unsubBtn.SetValue(True)
        self.unsubBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnUnsubscribe)

        self.sendBtn = wx.ToggleButton(self, label="sendMessage")
        self.sendBtn.SetValue(True)
        self.sendBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnSendMessage)

        self.newTBtn = wx.ToggleButton(self, label="newTopic")
        self.newTBtn.SetValue(True)
        self.newTBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnNewTopic)

        self.delTBtn = wx.ToggleButton(self, label="delTopic")
        self.delTBtn.SetValue(True)
        self.delTBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnDelTopic)

        self.deadBtn = wx.ToggleButton(self, label="deadListener")
        self.deadBtn.SetValue(True)
        self.deadBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnDead)

        btnpad = wx.LEFT | wx.RIGHT | wx.EXPAND
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(allBtn, 0, btnpad, 3)
        sizer.Add(wx.StaticLine(self, wx.HORIZONTAL), 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.subBtn, 0, btnpad, 3)
        sizer.Add(self.unsubBtn, 0, btnpad, 3)
        sizer.Add(self.sendBtn, 0, btnpad, 3)
        sizer.Add(wx.StaticLine(self, wx.HORIZONTAL), 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.newTBtn, 0, btnpad, 3)
        sizer.Add(self.delTBtn, 0, btnpad, 3)
        sizer.Add(self.deadBtn, 0, btnpad, 3)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def OnNotifyAll(self, evt):
        val = evt.IsChecked()
        self.subBtn.SetValue(val)
        self.unsubBtn.SetValue(val)
        self.sendBtn.SetValue(val)
        self.newTBtn.SetValue(val)
        self.delTBtn.SetValue(val)
        self.deadBtn.SetValue(val)
        pub.setNotificationFlags(all=val)

    def OnSubscribe(self, evt):
        pub.setNotificationFlags(subscribe=evt.IsChecked())

    def OnUnsubscribe(self, evt):
        pub.setNotificationFlags(unsubscribe=evt.IsChecked())

    def OnSendMessage(self, evt):
        pub.setNotificationFlags(sendMessage=evt.IsChecked())

    def OnNewTopic(self, evt):
        pub.setNotificationFlags(newTopic=evt.IsChecked())

    def OnDelTopic(self, evt):
        pub.setNotificationFlags(delTopic=evt.IsChecked())

    def OnDead(self, evt):
        pub.setNotificationFlags(deadListener=evt.IsChecked())


class TopicTreePanel(wx.Panel):
    """MonitorTreePanel
    Contains the topic tree and a few controls, including
    an instance of TopicDescriptionPanel
    """

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        box = wx.StaticBox(self, label="Topic Tree")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        label = wx.StaticText(self, label="RightClick on any item in the tree")
        ### Create a dummy panel
        self.tdp = wx.Panel(self)
        tree = TopicTree(self)
        refreshButton = wx.Button(self, label="Refresh")
        refreshButton.Bind(wx.EVT_BUTTON, tree._load)

        sizer.Add(label)
        sizer.Add(tree, 1, wx.EXPAND)
        sizer.Add(refreshButton, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.tdp, 0, wx.EXPAND)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def SetTopicDescription(self, tObj):
        """Replace the current topic description with a new one"""
        tdp = TopicDescriptionPanel(self, tObj)
        sizer = self.GetSizer()
        sizer.Detach(self.tdp)
        self.tdp.Destroy()
        sizer.Add(tdp, 0, wx.EXPAND | wx.ALL, 3)
        self.tdp = tdp
        self.Layout()
        self.Refresh()


class TopicTreeFiller(utils.ITopicTreeTraverser):
    """Link a pubsub.utils.ITopicTreeTraverser to a wxTreeCtrl
    Call traverse(topicObj) to fill
    """

    def __init__(self, wxTree=None, startTopic=None):
        if wxTree is None:
            raise RunTimeError, "TopicTreeFiller needs a wx.TreeCtrl to work with"

        self.Tree = wxTree
        if startTopic is None:
            self.startTopic = pub.getTopic(pub.ALL_TOPICS)
        self.root = self.Tree.AddRoot(str(self.startTopic.getName()))
        self.lastT = self.root
        self.Topics = [self.root]

    def _onTopic(self, topicObj):
        if topicObj is not self.startTopic:
            top = self.Tree.AppendItem(self.Topics[-1], str(topicObj.getName()))
            self.lastT = top

    def _startChildren(self):
        self.Topics.append(self.lastT)

    def _endChildren(self):
        self.Topics.pop()


class TopicTree(wx.TreeCtrl):
    """Subclass of wxTreeCtrl, sits in a TopicTreePanel object
    Uses direct method calls, even though this is exactly what
    pubsub is supposed to do. I don't want to create messasge static
    in the monitor
    """

    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent)
        self._load()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelection)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.OnRightClick)

    def SendPubSubMessage(self, evt):
        tName = self.GetItemText(self.GetSelection())
        tObj = pub.getTopic(str(tName))
        dlg = SendMessageDialog(self, tObj)
        dlg.ShowModal()

    def ShowListeners(self, evt):
        tName = self.GetItemText(self.GetSelection())
        tObj = pub.getTopic(str(tName))
        if tObj.hasListeners():
            llist = '\n'.join([repr(l.getCallable()) for l in tObj.getListenersIter()])
        else:
            llist = "No listeners"
        wx.MessageBox(llist, "Topic Listeners", style=wx.OK)

    def OnRightClick(self, evt):
        self.SelectItem(evt.GetItem())
        if not hasattr(self, 'sendmessageID'):
            self.sendmessageID = wx.NewId()
            self.showlistenersID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.SendPubSubMessage)
            self.Bind(wx.EVT_MENU, self.ShowListeners)
        menu = wx.Menu()
        menu.Append(self.sendmessageID, "Send Message")
        menu.Append(self.showlistenersID, "Show Listeners")
        self.PopupMenu(menu)

    def OnSelection(self, evt):
        tName = self.GetItemText(self.GetSelection())
        tObj = pub.getTopic(str(tName))
        self.Parent.SetTopicDescription(tObj)

    def _load(self, evt=None):
        self.DeleteAllItems()
        trv = TopicTreeFiller(self)
        trv.traverse(pub.getTopic(pub.ALL_TOPICS))
        self.Expand(self.GetRootItem())


class SendMessageDialog(wx.Dialog):
    """SendMessageDialog
    create a dialog with the topic description panel and
    a check and send and cancel options.
    Currently can only check the arguments, and even that
    does not work (as of Pypubsub rev 126) because topic.checkArgs does
    not return the boolean value the docs claim it returns.
    To get OnSendMessage to work, there needs to be a better
    way to know what the listener expects for each argument.
    """

    def __init__(self, parent, tObj):
        wx.Dialog.__init__(self, parent, title="Send Message")
        self.topicObj = tObj
        s = wx.BoxSizer(wx.VERTICAL)
        self.tdp = TopicDescriptionPanel(self, tObj, useTextCtrl=True)
        checkButton = wx.Button(self, label="Check")
        checkButton.Bind(wx.EVT_BUTTON, self.CheckTopic)

        sendButton = wx.Button(self, id=wx.ID_OK, label="Send")
        sendButton.Bind(wx.EVT_BUTTON, self.OnSendMessage)

        cancelButton = wx.Button(self, wx.ID_CANCEL)

        s.Add(self.tdp, 1, wx.EXPAND | wx.ALL, 3)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(checkButton, 0)
        row.Add(sendButton, 0, wx.LEFT, 6)
        row.Add(cancelButton, 0, wx.LEFT, 6)
        s.Add(row, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 6)
        self.SetSizerAndFit(s)
        self.Layout()

    def CheckTopic(self, evt):
        args = {}
        for key in self.tdp.topicArgs:
            args[key] = self.tdp.topicArgs[key].GetValue()
        ##        print args
        ok = self.topicObj.checkArgs(args)
        ### currently gets None from topic.checkArgs
        ###  topic.checkArgs should return True or False
        if ok:
            wx.MessageBox('Arguments check out', 'Check Args')
        else:
            wx.MessageBox("Arguments don't check", "Check Args")

    def OnSendMessage(self, evt):
        """OnSendMessage
        This should create the dialog box,
        """
        wx.MessageBox("This feature is not complete. See the doc string", "Not Implemented")


class TopicDescriptionPanel(wx.Panel):
    """TopicDescriptionPanel(parent, tObj)
    Creates a panel describing the topic object
    """

    def __init__(self, parent, tObj, useTextCtrl=False):
        wx.Panel.__init__(self, parent, name="topicDescription")
        box = wx.StaticBox(self, label="Topic Information")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        dtext = "%s [%s]\n(%d listener%s)" % \
                (tObj.getName(),
                 tObj.getDescription(),
                 tObj.getNumListeners(),
                 "" if tObj.getNumListeners() == 1 else "s")
        self.desc = wx.StaticText(self, label=dtext)
        self.desc.Wrap(self.Parent.GetSize()[0] - 6)
        sizer.Add(self.desc, 0, wx.EXPAND | wx.ALL, 2)
        grid = wx.FlexGridSizer(cols=2, vgap=3, hgap=2)
        grid.AddGrowableCol(1)
        req, opt, com = tObj.getArgs()
        dscs = tObj.getArgDescriptions()
        self.topicArgs = {}
        for arg in req + opt:
            lbl = "%s (%s): " % (arg, "required" if arg in req else "optional")
            grid.Add(wx.StaticText(self, label=lbl), 0, wx.ALIGN_RIGHT)
            if useTextCtrl:
                dsc = wx.TextCtrl(self)
                dsc.SetToolTipString(dscs.get(arg, "none"))
                self.topicArgs[arg] = dsc
            else:
                dsc = wx.StaticText(self, label=dscs.get(arg, "None"))
            grid.Add(dsc, 1, wx.ALIGN_LEFT | wx.EXPAND)

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizerAndFit(sizer)
        self.Layout()

        self.Bind(wx.EVT_SIZE, self.OnSize)
        # ~ print dir(tObj)
        ### Some code to explore the types of arguments the listener
        ### expects, strings, booleans, dictionary, etc.

    ##        if tObj.hasListeners():
    ##            listener = tObj.getListeners()[0]
    ##            print listener, listener.__class__, listener.getCallable()
    ##            print inspect.getargspec(listener.getCallable())

    def OnSize(self, evt):
        self.desc.Wrap(evt.GetSize()[0] - 6)

        self.Parent.Refresh()
        evt.Skip()


class MonitorLogger:
    """
    OBSOLETE, needs updating.

    Monitor logger for 'pubsub.*' topics. These topics are used
    automatically in various pubsub calls; e.g. when a new topic is
    created, a 'pubsub.newTopic' message is generated. Note that
    such messages are generated only if pub.setNotificationFlags() was called.

    Each method of DefaultLogger can be given
    to pub.subscribe() as a listener. A method's name indicates
    which 'pubsub' subtopic it can be listening for. E.g. you would
    subscribe the DefaultLogger.subscribe method to listen for
    'pubsub.subscribe' messages:

        from pubsub import pub
        from pubsub import pubsubconf

        from pubsub.utils import DefaultLogger,NotifyByPubsubMessage

        pubsubconf.setNotifier(NotifyByPubsubMessage)
        pub.setNotificationFlags(all=True)
        logger = DefaultLogger(pub)


    Any number of instances can be created. By default, the __init__
    will subscribe instance to all 'pubsub' subtopics. Class can also
    be derived to override default behavior.
    """

    prefix = 'PUBSUB: '
    import sys

    def __init__(self, publisher=None, out=sys.stdout):
        """If publisher is not None, then all self's methods
        are subscribed to the 'pubsub.*' topics by using
        publisher.subscribe(). """
        self._out = out
        self.lastMsg = ''
        self.lastTopic = ''
        self.lastLogTopic = ''
        self.counts = dict(send=0, sub=0, unsub=0, delt=0, newt=0, dead=0, all=0)

        if publisher is not None:
            pub = publisher
            pub.subscribe(self.subscribe, 'pubsub.subscribe')
            pub.subscribe(self.newTopic, 'pubsub.newTopic')
            pub.subscribe(self.delTopic, 'pubsub.delTopic')
            pub.subscribe(self.unsubscribe, 'pubsub.unsubscribe')
            pub.subscribe(self.sendMessage, 'pubsub.sendMessage')
            pub.subscribe(self.deadListener, 'pubsub.deadListener')
            pub.subscribe(self.all, 'pubsub')

    def setOut(self, out):
        self._out = out

    def all(self, msgTopic=pub.AUTO_TOPIC):
        self.counts['all'] += 1
        self.lastLogTopic = msgTopic

    def subscribe(self, topic=None, listener=None, didit=None):
        """Give this to pub.subscribe() as listener of
        'pubsub.subscribe' messages."""
        if didit:
            msg = '%sSubscribed listener %s to topic "%s"\n'
        else:
            msg = '%sSubscription of %s to topic "%s" redundant\n'
        msg = msg % (self.prefix, listener, topic.getName())
        self._out.write(msg)
        self.lastTopic = topic.getName()
        self.lastLogTopic = 'pubsub.subscribe'
        self.counts['sub'] += 1
        self.lastMsg = msg

    ##        print msg

    def unsubscribe(self, topic=None, listener=None, listenerRaw=None):
        """Give this to pub.subscribe() as listener of
        'pubsub.unsubscribe' mesages. """
        msg = '%sUnsubscribed listener %s from topic "%s"\n'
        msg = msg % (self.prefix, listener, topic.getName())
        self._out.write(msg)
        self.lastTopic = topic.getName()
        self.lastLogTopic = 'pubsub.unsubscribe'
        self.lastMsg = msg
        self.counts['unsub'] += 1

    ##        print msg

    def newTopic(self, topic=None, args=None, description=None, required=None):
        """Give this to pub.subscribe() as listener of
        'pubsub.newTopic' messages.
        Messages are only generated when pub.newTopic is called
        explicitly in the code, not on automatic topic generation
        """
        msg = '%sNew topic "%s" created (%s)\n'
        msg = msg % (self.prefix, topic.getName(), description)
        self._out.write(msg)
        self.lastTopic = topic.getName()
        self.lastLogTopic == 'pubsub.newTopic'
        self.lastMsg = msg
        self.counts['newt'] += 1

    ##        print msg

    def delTopic(self, name=None):
        """Give this to pub.subscribe() as listener of
        'pubsub.delTopic' messages. """
        msg = '%sTopic "%s" destroyed\n'
        msg = msg % (self.prefix, name)
        self._out.write(msg)
        self.lastTopic = name
        self.lastLogTopic = 'pubsub.delTopic'
        self.lastMsg = msg
        self.counts['delt'] += 1

    ##        print msg

    def sendMessage(self, topic=None, stage=None):
        """Give this to pub.subscribe() as listener of
        'pubsub.sendMessage' messages. """
        if stage == 'pre':
            msg = '%sSending message of topic "%s"\n'
            msg = msg % (self.prefix, topic.getName())
            self._out.write(msg)
            self.lastTopic = topic.getName()
            self.lastLogTopic = 'pubsub.sendMessage'
            self.lastMsg = msg
            self.counts['send'] += 1
        if stage == 'post':
            msg = "%sSent '%s' message\n"
            msg = msg % (self.prefix, topic.getName())
            self._out.write(msg)
        ##        print msg

    def deadListener(self, topic=None, listener=None):
        """Give this to pub.subscribe() as a listener of
        'deadListener' messages."""
        msg = "%sListener %s for topic '%s' is dead\n"
        msg = msg % (self.prefix, listener, topic.getName())
        self._out.write(msg)
        self.lastMsg = msg
        self.lastTopic = topic.getName()
        self.lastLogTopic = 'pubsub.deadlistener'
        self.counts['dead'] += 1


##        print msg

##class Redirector:
##    """Redirector(wxTextCtrl)
##    Simple wrapper to take output from DefaultLogger (which uses a
##    'write' method to a file-like object) to a wx.TextCtrl (which uses AppendText).
##    """
##    def __init__(self,LogCtrl):
##        self.text = LogCtrl
##        print "Redirector Text",self.text
##        print "Redirector Text parent", self.text.Parent
##
##    def write(self,text):
##        try:
##            self.text.AppendText(text)
##        except:
##            print "cannot print:", text

class LogPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, name="log")
        box = wx.StaticBox(self, label="Log")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.Text = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_DONTWRAP | wx.TE_MULTILINE)
        sizer.Add(self.Text, 1, wx.EXPAND | wx.GROW | wx.ALL, 2)
        self.SetSizerAndFit(sizer)
        self.Layout()

    def getText(self):
        return self.Text

    def write(self, text):
        ##        print "writing"
        self.Text.AppendText(text)


class LastLogEntryPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, name="last log")
        box = wx.StaticBox(self, label="Last Log Entry")

        messageLabel = wx.StaticText(self, label="Message:")
        self.messageText = wx.TextCtrl(self, name="messageText")
        topicLabel = wx.StaticText(self, label="Topic:")
        self.topicText = wx.TextCtrl(self, name="topicText")
        pstopicLabel = wx.StaticText(self, label="psTopic:")
        self.pstopicText = wx.TextCtrl(self, name="pstopicText")

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(messageLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        row.Add(self.messageText, 1, wx.LEFT | wx.EXPAND, 3)
        sizer.Add(row, 0, wx.EXPAND)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(topicLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        row.Add(self.topicText, 1, wx.LEFT | wx.EXPAND, 3)

        row.Add(pstopicLabel, 0, wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 6)
        row.Add(self.pstopicText, 1, wx.LEFT | wx.EXPAND, 3)
        sizer.Add(row, 0, wx.EXPAND | wx.TOP, 3)

        self.SetSizerAndFit(sizer)
        self.Layout()

    def SetMessage(self, text):
        self.messageText.SetValue(str(text))

    def SetTopic(self, text):
        self.topicText.SetValue(str(text))

    def SetPSTopic(self, text):
        self.pstopicText.SetValue(str(text))


class CountPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, name="counts")
        box = wx.StaticBox(self, label="Counts")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        grid = wx.GridSizer(cols=7, hgap=2, vgap=2)
        lbls = ['all', 'subscribe', 'unsub', 'send', 'newt', 'delt', 'dead']
        counts = {}
        for c in lbls:
            t = wx.StaticText(self, label="0", name="count_%s" % c,
                              style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE | wx.SIMPLE_BORDER)
            grid.Add(t, 0,
                     wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL, 2)
        for c in lbls:
            t = wx.StaticText(self, label=c)
            grid.Add(t, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(grid, 1, wx.EXPAND | wx.GROW)
        self.SetSizerAndFit(sizer)
        self.Layout()

    def count(self, topicname):
        ##        print "counting:",topicname
        garbage, topicname = topicname.split('.')
        if topicname == 'sendMessage':
            topicname = 'send'
        if topicname == 'unsubscribe':
            topicname = 'unsub'
        if topicname == 'newTopic':
            topicname = 'newt'
        if topicname == 'delTopic':
            topicname = 'delt'
        if topicname == 'deadListener':
            topicname = 'dead'
        lbl = self.FindWindowByName("count_%s" % topicname)
        if lbl:
            c = int(lbl.GetLabel())
            lbl.SetLabel(str(c + 1))
        else:
            print
            "something has gone wrong with", topicname
        alllbl = self.FindWindowByName('count_all')
        alllbl.SetLabel(str(int(alllbl.GetLabel()) + 1))


def test():
    """This test opens the MonitorFrame, as well as a frame
    with a show and hide button
    """

    class showFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, title="Monitor Toggle")
            sbtn = wx.Button(self, label="Show Frame")
            sbtn.Bind(wx.EVT_BUTTON, self.SendShowMsg)
            hbtn = wx.Button(self, label="Hide Frame")
            hbtn.Bind(wx.EVT_BUTTON, self.SendHideMsg)

            s = wx.BoxSizer(wx.VERTICAL)
            s.Add(sbtn, 0, wx.EXPAND)
            s.Add(hbtn, 0, wx.EXPAND)
            self.SetSizerAndFit(s)
            self.Layout()

        def SendShowMsg(self, evt):
            print
            "pressed show button"
            pub.sendMessage('monitor.show', show=True)

        def SendHideMsg(self, evt):
            print
            "pressed hide button"
            pub.sendMessage('monitor.hide')

    class myApp(wx.App, MonitorMixin):
        def OnInit(self):
            print
            "Making App"
            MonitorMixin.Init(self)
            show = showFrame(None)
            self.SetTopWindow(show)
            show.Show()
            show.Raise()
            print
            "OnInit end"
            return True

    a = myApp(False)
    print
    "Made app. Starting Mainloop"
    a.MainLoop()
    print
    "Done with main loop"
    a.Destroy()
    pub.delTopic('test')


if __name__ == '__main__':
    print
    "testing"
    test()
