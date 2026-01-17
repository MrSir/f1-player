from f1p import F1PlayerApp


app = F1PlayerApp()
app.disableMouse()  # disable camera controls
app.configure_window().draw_menu().register_ui_components().run()
