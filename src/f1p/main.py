from f1p.app import F1PlayerApp

app = F1PlayerApp()
app.configure_window().draw_menu().register_ui_components().register_controls().run()
