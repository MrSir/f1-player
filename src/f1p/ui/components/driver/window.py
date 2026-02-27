from decimal import Decimal

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GraphicsWindow, PerspectiveLens, Camera, NodePath, TextNode, PGTop, Point3, \
    OrthographicLens, DisplayRegion, LVecBase4f, Vec4


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
        dr = self.window.makeDisplayRegion(0.6875, 0.9875, 0.625, 0.925)
        dr.setSort(100)
        dr.setClearColorActive(True)
        dr.setClearColor(Vec4(0.3, 0.3, 0.3, 1))
        dr.setCamera(self.camera_np)

    def make_title_frame(self) -> None:
        title_frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, 260, 0, self.height),
            pos=Point3(540, 0, -self.height),
        )

        OnscreenText(
            parent=title_frame,
            text=f"#{self.driver_number} {self.first_name} {self.last_name}",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(10, self.height - 21, 0),
        )

        DirectFrame(
            parent=title_frame,
            frameColor=self.team_color_obj, # TODO something is not right with the color of this frame, its darker
            frameSize=(0, 19, 0, 19),
            pos=(10, 0, self.height - 49),
        )

        OnscreenText(
            parent=title_frame,
            text=self.team_name,
            align=TextNode.ALeft,
            scale=14,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(33, self.height - 44, 0),
        )

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