import wx

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Layout Example", size=(900,600))

        # Prevent the window from being resized
        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())

        # Center the window on the screen
        self.Centre()

        # Create a menu bar
        menu_bar = wx.MenuBar()

        # Create menus
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        history_menu = wx.Menu()
        tools_menu = wx.Menu()
        about_menu = wx.Menu()

        # Add items to the 'File' menu
        file_menu.Append(wx.ID_SAVE, "Save")
        file_menu.Append(wx.ID_SAVEAS, "Save As")
        file_menu.Append(wx.ID_CLOSE, "Close")

        # Add items to the 'Edit' menu
        edit_menu.Append(wx.ID_COPY, "Copy")
        edit_menu.Append(wx.ID_PASTE, "Paste")

        # Add items to the 'History' menu
        history_menu.Append(wx.ID_ANY, "Recent")

        # Add items to the 'Tools' menu
        tools_menu.Append(wx.ID_ANY, "Robo")

        # Add menus to menu bar
        menu_bar.Append(file_menu, "File")
        menu_bar.Append(edit_menu, "Edit")
        menu_bar.Append(history_menu, "History")
        menu_bar.Append(tools_menu, "Tools")
        menu_bar.Append(about_menu, "About")

        # Set the menu bar
        self.SetMenuBar(menu_bar)


        # Create sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create header, footer, sidebar, and main content
        header = wx.Panel(self)
        header.SetBackgroundColour(wx.Colour(220, 220, 220))
        footer = wx.Panel(self)
        footer.SetBackgroundColour(wx.Colour(220, 220, 220))
        sidebar = wx.Panel(self)
        sidebar.SetBackgroundColour(wx.Colour(230, 230, 230))
        main_content = wx.Panel(self)
        main_content.SetBackgroundColour(wx.Colour(241, 241, 241))

        # Create a list view
        list_view = wx.ListView(sidebar)
        list_view.InsertColumn(0, 'Jobs', wx.LIST_FORMAT_RIGHT, width=200)

        # Add items to the list view
        for i in range(50):
            list_view.InsertItem(i, str(i)+' DAYS')

        # Create a sizer for the sidebar and add the tree view to it
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        sidebar_sizer.Add(list_view, 1, wx.EXPAND)
        sidebar.SetSizer(sidebar_sizer)

        # Add components to sizers
        header_sizer.Add(header, 1, wx.EXPAND)
        footer_sizer.Add(footer, 1, wx.EXPAND)
        body_sizer.Add(sidebar, 1, wx.EXPAND)
        body_sizer.Add(main_content, 3, wx.EXPAND)

        # Add sizers to main sizer
        main_sizer.Add(header_sizer, 1, wx.EXPAND)
        main_sizer.Add(body_sizer, 8, wx.EXPAND)
        main_sizer.Add(footer_sizer, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
