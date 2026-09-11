from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class SatelliteTracker(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        title = Label(
            text="🛰️ SATELLITE TRACKER",
            font_size=28
        )

        info = Label(
            text="ISS (ZARYA)\n\n"
                 "Altitude: --°\n"
                 "Direction: --°\n"
                 "Distance: -- km\n\n"
                 "Waiting for satellite data...",
            font_size=20
        )

        refresh = Button(
            text="🔄 REFRESH",
            font_size=20,
            size_hint_y=None,
            height=60
        )

        layout.add_widget(title)
        layout.add_widget(info)
        layout.add_widget(refresh)

        return layout


if __name__ == "__main__":
    SatelliteTracker().run()
