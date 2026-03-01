from decimal import Decimal

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GraphicsWindow, PerspectiveLens, Camera, NodePath, TextNode, PGTop, Point3, \
    OrthographicLens, DisplayRegion, LVecBase4f, Vec4, CardMaker


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
    ):
        super().__init__()

        self.width = width
        self.height = height
        self.driver_number = driver_number
        self.first_name = first_name
        self.last_name = last_name
        self.team_color_obj = team_color_obj
        self.team_name = team_name
        self.app = app
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

        return self._window

    @property
    def render2d(self) -> NodePath:
        if self._render2d is None:
            self._render2d = NodePath(f'render2d{self.driver_number}')
            self._render2d.setDepthTest(False)
            self._render2d.setDepthWrite(False)

        return self._render2d

    @property
    def pixel2d(self) -> NodePath:
        if self._pixel2d is None:
            self._pixel2d = self.render2d.attachNewNode(f'pixel2d{self.driver_number}')
            self._pixel2d.setPos(-1, 0, 1)
            width, height = self.window.getSize()
            self._pixel2d.setScale(2.0 / width, 1.0, 2.0 / height)
            self._pixel2d.reparentTo(self.render2d)

        return self._pixel2d

    def initialize_camera2d(self) -> None:
        camera2d_np = self.app.makeCamera2d(self.window)
        camera2d_np.reparentTo(self.render2d)

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
        dr = self.window.makeDisplayRegion(0.6875, 0.9875, 0.6125, 0.9125)
        dr.setSort(10)
        dr.setClearColorActive(True)
        dr.setClearColor(Vec4(0.3, 0.3, 0.3, 1))
        dr.setCamera(self.camera_np)

    def make_title_frame(self) -> None:
        height = 320
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, 260, 0, height),
            pos=Point3(540, 0, -(self.height - (self.height - height))),
            sortOrder=0,
        )

        title_frame_height = 60
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, 260, 0, title_frame_height),
            pos=Point3(0, 0, height-title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text=f"#{self.driver_number} {self.first_name} {self.last_name}",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(10, title_frame_height-21, 0),
        )

        square = DirectFrame(
            parent=title_frame,
            frameColor=self.team_color_obj, # TODO something is not right with the color of this frame, its darker
            frameSize=(0, 19, 0, 19),
            pos=(10, 0, title_frame_height-49),
            sortOrder=20,
        )
        square.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text=self.team_name,
            align=TextNode.ALeft,
            scale=14,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(33, title_frame_height-44, 0),
        )

    def make_telemetry_frame(self) -> None:
        height = 205
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, 260, 0, height),
            pos=Point3(540, 0, -(self.height - (self.height - height - 325))),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, 260, 0, title_frame_height),
            pos=Point3(0, 0, height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="TELEMETRY",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(260/2, title_frame_height - 21, 0),
        )

        OnscreenText(
            parent=frame,
            text="SPEED",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(10, height - title_frame_height - 20, 0),
        )

        OnscreenText(
            parent=frame,
            text="360.00km/h",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, height - title_frame_height - 40, 0),
        )

        OnscreenText(
            parent=frame,
            text="223.69mph",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(0.5, 0.5, 0.5, 1),
            pos=(130, height - title_frame_height - 40, 0),
        )

        OnscreenText(
            parent=frame,
            text="RPM",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(10, height - title_frame_height - 60, 0),
        )

        OnscreenText(
            parent=frame,
            text="12000",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, height - title_frame_height - 80, 0),
        )

        OnscreenText(
            parent=frame,
            text="GEAR",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(10, height - title_frame_height - 100, 0),
        )

        OnscreenText(
            parent=frame,
            text="8",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, height - title_frame_height - 120, 0),
        )

        OnscreenText(
            parent=frame,
            text="DRS",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(10, height - title_frame_height - 140, 0),
        )

        OnscreenText(
            parent=frame,
            text="ON",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, height - title_frame_height - 160, 0),
        )

        OnscreenText(
            parent=frame,
            text="BRAKE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(130, height - title_frame_height - 60, 0),
        )

        brake_frame = DirectFrame(
            parent=frame,
            frameColor=(1, 1, 1, 0.7),
            frameSize=(-10, 10, 0, 100),
            pos=Point3(130, 0, height - title_frame_height - 165),
            sortOrder=10,
        )
        brake_frame.clearColorScale()

        OnscreenText(
            parent=frame,
            text="THROTTLE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=(0.8, 1, 0, 0.7),
            pos=(210, height - title_frame_height - 60, 0),
        )

        throttle_frame = DirectFrame(
            parent=frame,
            frameColor=(1, 1, 1, 0.7),
            frameSize=(-10, 10, 0, 100),
            pos=Point3(210, 0, height - title_frame_height - 165),
            sortOrder=10,
        )
        throttle_frame.clearColorScale()


    def update_camera_position(self, x: Decimal, y: Decimal, z: Decimal) -> None:
        self.camera_np.setX(x + 5)
        self.camera_np.setY(y + 5)
        self.camera_np.setZ(z + 5)
        self.camera_np.lookAt(x, y, z)

    def open(self) -> None:
        if self.is_open:
            return

        self.is_open = True
        self.initialize_camera2d()
        self.make_title_frame()
        self.make_camera_region()
        self.make_telemetry_frame()

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