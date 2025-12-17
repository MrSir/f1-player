from direct.showbase.ShowBase import ShowBase


class F1PlayerApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)


app = F1PlayerApp()
app.run()