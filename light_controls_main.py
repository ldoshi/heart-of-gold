from lighting import light_controls
import wyze_sdk



wyze_client = wyze_sdk.Client(
    email="lyric-ta@mit.edu", password="HeartGold1015"
)

color_list = [
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=1800),
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=2800),
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=3800),
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=4800),
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=5800),
    light_controls.LightingColor(type=light_controls.ColorType.TEMPERATURE, value=6500),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="ff0000"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="ffff00"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="00ff00"),
    light_controls.LightingColor(type=light_controls.ColorType.COLOR, value="0000ff"),
]

light_control = light_controls.LightControls(
    wyze_client=wyze_client,
    nickname_prefix="bed_room",
    on_key="r",
    off_key="f",
    color_next_key="v",
    color_list=color_list
)

