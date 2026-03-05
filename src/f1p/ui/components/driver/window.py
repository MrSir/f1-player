from decimal import Decimal

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GraphicsWindow, PerspectiveLens, Camera, NodePath, TextNode, PGTop, Point3, \
    OrthographicLens, DisplayRegion, LVecBase4f, Vec4, CardMaker, VBase4


class DriverWindow(DirectObject):
    def __init__(
        self,
        width: int,
        height: int,
        driver_number: str,
        first_name: str,
        last_name: str,
        team_color_obj: LVecBase4f,
        team_name: str,
        app: ShowBase,
        strategy: dict[int, dict[str, str | int]],
    ):
        super().__init__()

        self.width = width
        self.height = height
        self.driver_frame_height = 380
        self.telemetry_frame_height = 225

        self.driver_number = driver_number
        self.first_name = first_name
        self.last_name = last_name
        self.team_color_obj = team_color_obj
        self.team_name = team_name
        self.app = app
        self.strategy = strategy
        self.is_open = False

        self._window_properties: WindowProperties | None = None
        self._window: GraphicsWindow | None = None

        self._lens2d: OrthographicLens | None = None
        self._camera2d: Camera | None = None
        self._camera2d_np: NodePath | None = None

        self._render2d: NodePath | None = None
        self._pixel2d: NodePath | None = None

        self._lens: PerspectiveLens | None = None
        self._camera: Camera | None = None
        self._camera_np: NodePath | None = None

        self.position: OnscreenText | None = None
        self.laps: OnscreenText | None = None
        self.speed_kph: OnscreenText | None = None
        self.speed_mph: OnscreenText | None = None
        self.rpm: DirectFrame | None = None
        self.gear_N: OnscreenText | None = None
        self.gear_1: OnscreenText | None = None
        self.gear_2: OnscreenText | None = None
        self.gear_3: OnscreenText | None = None
        self.gear_4: OnscreenText | None = None
        self.gear_5: OnscreenText | None = None
        self.gear_6: OnscreenText | None = None
        self.gear_7: OnscreenText | None = None
        self.gear_8: OnscreenText | None = None
        self.drs: OnscreenText | None = None
        self.brake: DirectFrame | None = None
        self.throttle: DirectFrame | None = None

        self.blue_color = (103/255, 190/255, 217/255, 1)
        self.green_color = (102/255, 217/255, 126/255, 1)
        self.red_color = (217/255, 110/255, 102/255, 1)
        self.white_color = (1, 1, 1, 1)
        self.gray_color = (0.7, 0.7, 0.7, 1)
        self.dark_gray_color = (0.5, 0.5, 0.5, 1)

        self.accept(f"closeDriver{self.driver_number}", self.close)

    @property
    def window_properties(self) -> WindowProperties:
        if self._window_properties is None:
            self._window_properties = WindowProperties()
            self._window_properties.setSize(self.width, self.height)
            self._window_properties.setFixedSize(True)
            self._window_properties.setTitle(f"Driver {self.driver_number} - {self.first_name} {self.last_name}")

        return self._window_properties

    @property
    def window(self) -> GraphicsWindow:
        if self._window is None:
            self._window = self.app.openWindow(props=self.window_properties, makeCamera=False)
            self._window.setCloseRequestEvent(f"closeDriver{self.driver_number}")
            self._window.setClearColor(VBase4(0.3, 0.3, 0.3, 1))

        return self._window

    @property
    def render2d(self) -> NodePath:
        if self._render2d is None:
            self._render2d = NodePath(f'render2d{self.driver_number}')
            self._render2d.setDepthTest(False)
            self._render2d.setDepthWrite(False)

            camera2d_np = self.app.makeCamera2d(self.window)
            camera2d_np.reparentTo(self._render2d)

        return self._render2d

    @property
    def pixel2d(self) -> NodePath:
        if self._pixel2d is None:
            self._pixel2d = self.render2d.attachNewNode(PGTop(f'pixel2d{self.driver_number}'))
            self._pixel2d.setPos(-1, 0, 1)
            width, height = self.window.getSize()
            self._pixel2d.setScale(2.0 / width, 1.0, 2.0 / height)
            self._pixel2d.reparentTo(self.render2d)

        return self._pixel2d

    @property
    def lens(self) -> PerspectiveLens:
        if self._lens is None:
            self._lens = PerspectiveLens()
            self._lens.setAspectRatio(640 / 480)

        return self._lens

    @property
    def camera(self) -> Camera:
        if self._camera is None:
            self._camera = Camera(f"camera{self.driver_number}")
            self._camera.setLens(self.lens)

        return self._camera

    @property
    def camera_np(self) -> NodePath:
        if self._camera_np is None:
            self._camera_np = NodePath(self.camera)
            self._camera_np.reparentTo(self.app.render)

        return self._camera_np

    def make_camera_region(self) -> None:
        dr = self.window.makeDisplayRegion(0.675, 0.975, 0.525, 0.825)
        dr.setSort(10)
        dr.setClearColorActive(True)
        dr.setClearColor(Vec4(0.3, 0.3, 0.3, 1))
        dr.setCamera(self.camera_np)

    def make_driver_widget(self) -> None:
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, 260, 0, self.driver_frame_height),
            pos=Point3(530, 0, -(self.height - (self.height - self.driver_frame_height - 10))),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, 260, 0, title_frame_height),
            pos=Point3(0, 0, self.driver_frame_height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="DRIVER",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(260/ 2, title_frame_height - 20, 0),
        )

        OnscreenText(
            parent=frame,
            text=f"#{self.driver_number} {self.first_name} {self.last_name}",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(10, self.driver_frame_height - title_frame_height - 25, 0),
        )

        DirectFrame(
            parent=frame,
            frameColor=self.team_color_obj,
            frameSize=(0, 19, 0, 19),
            pos=(10, 0, self.driver_frame_height - title_frame_height - 54),
            sortOrder=20,
        )

        OnscreenText(
            parent=frame,
            text=self.team_name,
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(33, self.driver_frame_height - title_frame_height - 50, 0),
        )

        OnscreenText(
            parent=frame,
            text="POSITION",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(10, self.driver_frame_height - title_frame_height - 70, 0),
        )

        self.position = OnscreenText(
            parent=frame,
            text="TBD",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, self.driver_frame_height - title_frame_height - 90, 0),
        )

        OnscreenText(
            parent=frame,
            text="LAPS",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(100, self.driver_frame_height - title_frame_height - 70, 0),
        )

        self.laps = OnscreenText(
            parent=frame,
            text="TBD",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(120, self.driver_frame_height - title_frame_height - 90, 0),
        )

    def make_telemetry_widget(self) -> None:
        width = 260
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, width, 0, self.telemetry_frame_height),
            pos=Point3(530, 0, -(self.height - (self.height - self.telemetry_frame_height - self.driver_frame_height - 20))),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, self.telemetry_frame_height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="TELEMETRY",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, title_frame_height - 21, 0),
        )

        OnscreenText(
            parent=frame,
            text="GEARS",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 20, 0),
        )

        gear_spacer = 20
        initial_space = 45
        self.gear_N = OnscreenText(
            parent=frame,
            text="N",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.green_color,
            pos=(initial_space, self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_1 = OnscreenText(
            parent=frame,
            text="1",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 1), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_2 = OnscreenText(
            parent=frame,
            text="2",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 2), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_3 = OnscreenText(
            parent=frame,
            text="3",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 3), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_4 = OnscreenText(
            parent=frame,
            text="4",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 4), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_5 = OnscreenText(
            parent=frame,
            text="5",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 5), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_6 = OnscreenText(
            parent=frame,
            text="6",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 6), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_7 = OnscreenText(
            parent=frame,
            text="7",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 7), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        self.gear_8 = OnscreenText(
            parent=frame,
            text="8",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(initial_space + (gear_spacer * 8), self.telemetry_frame_height - title_frame_height - 40, 0),
        )

        rpm_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(0, 240, 0, 10),
            pos=Point3(10, 0, self.telemetry_frame_height - title_frame_height - 60),
        )

        self.rpm = DirectFrame(
            parent=rpm_frame,
            frameColor=self.blue_color,
            frameSize=(0, 0, 0, 10),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ALeft,
            scale=11,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(10, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        OnscreenText(
            parent=frame,
            text="15",
            align=TextNode.ARight,
            scale=11,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width - 10, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        OnscreenText(
            parent=frame,
            text="RPM x1000",
            align=TextNode.ACenter,
            scale=11,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        brake_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(60, 0, self.telemetry_frame_height - title_frame_height - 170),
        )
        self.brake = DirectFrame(
            parent=brake_frame,
            frameColor=self.red_color,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="BRAKE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(60, self.telemetry_frame_height - title_frame_height - 185, 0),
        )

        OnscreenText(
            parent=frame,
            text="KM/H",
            align=TextNode.ACenter,
            scale=15,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 90, 0),
        )

        self.speed_kph = OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ACenter,
            scale=18,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 110, 0),
        )

        self.drs =OnscreenText(
            parent=frame,
            text="DRS",
            align=TextNode.ACenter,
            scale=14,
            font=self.app.text_font,
            fg=self.blue_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 132, 0),
        )

        self.speed_mph = OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.dark_gray_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 155, 0),
        )

        OnscreenText(
            parent=frame,
            text="MPH",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.dark_gray_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 170, 0),
        )

        throttle_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(width - 60, 0, self.telemetry_frame_height - title_frame_height - 170),
        )
        self.throttle = DirectFrame(
            parent=throttle_frame,
            frameColor=self.green_color,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="THROTTLE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width - 60, self.telemetry_frame_height - title_frame_height - 185, 0),
        )

    def make_tire_strategy_widget(self) -> None:
        height = 90
        width = 260
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, width, 0, height),
            pos=Point3(530, 0, -(self.height - (self.height - height - self.driver_frame_height - self.telemetry_frame_height - 30))),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="TIRE STRATEGY",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, title_frame_height - 21, 0),
        )

        padding = 10
        total_width = width - (padding * 2)
        total_laps = max(i["LapNumber"] for i in self.strategy.values())
        start = padding + 0
        for stint, info in self.strategy.items():
            current_ratio = info["LapNumber"] / total_laps
            end = padding + (total_width * current_ratio)
            DirectFrame(
                parent=frame,
                frameColor=(0.4, 0.4, 0.4, 1),
                frameSize=(start, end, 0, 30),
                pos=Point3(0, 0, height - title_frame_height - 40),
            )
            DirectFrame(
                parent=frame,
                frameColor=info["CompoundColor"],
                frameSize=(start + 1, end - 1, 1, 29),
                pos=Point3(1, 0, height - title_frame_height - 41),
            )

            start = end

        OnscreenText(
            parent=frame,
            text="1",
            align=TextNode.ALeft,
            scale=11,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(10, height - title_frame_height - 50, 0),
        )

        OnscreenText(
            parent=frame,
            text=f"{total_laps:.0f}",
            align=TextNode.ARight,
            scale=11,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width - 10, height - title_frame_height - 50, 0),
        )

    def update_standings(self, position_index: int, lap: float, total_laps: str) -> None:
        if self.position.text != f"{position_index + 1}":
            self.position["text"] = f"{position_index + 1}"

        if self.laps.text != f"{int(lap)}/{total_laps}":
            self.laps["text"] = f"{int(lap)}/{total_laps}"

    def update_telemetry(
        self,
        gear: str,
        rpm: float,
        brake: bool,
        speed_kph: float,
        drs: float,
        speed_mph: float,
        throttle: float,
    ) -> None:
        current_gear_N_color = self.gear_N.textNode.getTextColor()
        gear_N_color = self.green_color if gear == "N" else self.gray_color
        if current_gear_N_color != gear_N_color:
            self.gear_N["fg"] = gear_N_color

        current_gear_1_color = self.gear_1.textNode.getTextColor()
        gear_1_color = self.green_color if gear == "1" else self.gray_color
        if current_gear_1_color != gear_1_color:
            self.gear_1["fg"] = gear_1_color

        current_gear_2_color = self.gear_2.textNode.getTextColor()
        gear_2_color = self.green_color if gear == "2" else self.gray_color
        if current_gear_2_color != gear_2_color:
            self.gear_2["fg"] = gear_2_color

        current_gear_3_color = self.gear_3.textNode.getTextColor()
        gear_3_color = self.green_color if gear == "3" else self.gray_color
        if current_gear_3_color != gear_3_color:
            self.gear_3["fg"] = gear_3_color

        current_gear_4_color = self.gear_4.textNode.getTextColor()
        gear_4_color = self.green_color if gear == "4" else self.gray_color
        if current_gear_4_color != gear_4_color:
            self.gear_4["fg"] = gear_4_color

        current_gear_5_color = self.gear_5.textNode.getTextColor()
        gear_5_color = self.green_color if gear == "5" else self.gray_color
        if current_gear_5_color != gear_5_color:
            self.gear_5["fg"] = gear_5_color

        current_gear_6_color = self.gear_6.textNode.getTextColor()
        gear_6_color = self.green_color if gear == "6" else self.gray_color
        if current_gear_6_color != gear_6_color:
            self.gear_6["fg"] = gear_6_color

        current_gear_7_color = self.gear_7.textNode.getTextColor()
        gear_7_color = self.green_color if gear == "7" else self.gray_color
        if current_gear_7_color != gear_7_color:
            self.gear_7["fg"] = gear_7_color

        current_gear_8_color = self.gear_8.textNode.getTextColor()
        gear_8_color = self.green_color if gear == "8" else self.gray_color
        if current_gear_8_color != gear_8_color:
            self.gear_8["fg"] = gear_8_color

        current_rpm_size = self.rpm["frameSize"]
        rpm_size = (0, rpm / 15000 * 240, 0, 10)
        if current_rpm_size != rpm_size:
            self.rpm["frameSize"] = rpm_size

        current_brake_size = self.brake["frameSize"]
        brake_size = (-10, 10, 0, 100 if brake else 0)
        if current_brake_size != brake_size:
            self.brake["frameSize"] = brake_size

        if self.speed_kph.text != f"{speed_kph:.0f}":
            self.speed_kph["text"] = f"{speed_kph:.0f}"

        current_drs_color = self.drs.textNode.getTextColor()

        drs_color = self.blue_color
        match drs:
            case 0.0:
                drs_color = self.blue_color
            case 1.0:
                drs_color = self.red_color
            case 14.0:
                drs_color = self.green_color

        if current_drs_color != drs_color:
            self.drs["fg"] = drs_color

        if self.speed_mph.text != f"{speed_mph:.0f}":
            self.speed_mph["text"] = f"{speed_mph:.0f}"

        current_throttle_size = self.throttle["frameSize"]
        throttle_size = (-10, 10, 0, throttle)
        if current_throttle_size != throttle_size:
            self.throttle["frameSize"] = throttle_size

    def update_camera_position(self, x: Decimal, y: Decimal, z: Decimal) -> None:
        self.camera_np.setX(x + 5)
        self.camera_np.setY(y + 5)
        self.camera_np.setZ(z + 5)
        self.camera_np.lookAt(x, y, z)

    def update(self, current_record: dict) -> None:
        self.update_standings(current_record["PositionIndex"], current_record['LapNumber'], current_record["TotalLaps"])

        self.update_telemetry(
            current_record["nGear"],
            current_record["RPM"],
            current_record["Brake"],
            current_record["Speed"],
            current_record["DRS"],
            current_record["SpeedMph"],
            current_record["Throttle"],
        )

        precision = Decimal("0.001")
        x = Decimal(current_record["X"]).quantize(precision)
        y = Decimal(current_record["Y"]).quantize(precision)
        z = Decimal(current_record["Z"]).quantize(precision)
        self.update_camera_position(x, y, z)

    def open(self) -> None:
        if self.is_open:
            return

        self.is_open = True
        self.make_driver_widget()
        self.make_camera_region()
        self.make_telemetry_widget()
        self.make_tire_strategy_widget()

    def close(self) -> None:
        self.is_open = False
        self.window.removeAllDisplayRegions()
        self.render2d.removeNode()
        self.app.closeWindow(self.window)

        self._window = None
        self._render2d = None
        self._pixel2d = None
        self._lens = None
        self._camera = None
        self._camera_np = None