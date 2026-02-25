from decimal import Decimal

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GraphicsWindow, PerspectiveLens, Camera, NodePath


class DriverWindow(DirectObject):
    def __init__(self, driver_number: str, first_name: str, last_name: str, app: ShowBase):
        super().__init__()

        self.driver_number = driver_number
        self.first_name = first_name
        self.last_name = last_name
        self.app = app
        self.is_open = False

        self._window_properties: WindowProperties | None = None
        self._window: GraphicsWindow | None = None

        self._lens: PerspectiveLens | None = None
        self._camera: Camera | None = None
        self._camera_np: NodePath | None = None

        self.accept(f"closeDriver{self.driver_number}", self.close)

    @property
    def window_properties(self) -> WindowProperties:
        if self._window_properties is None:
            self._window_properties = WindowProperties()
            self._window_properties.setSize(800, 800)
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
        dr = self.window.makeDisplayRegion(0.7, 1, 0.7, 1)
        dr.setCamera(self.camera_np)

    def update_camera_position(self, x: Decimal, y: Decimal, z: Decimal) -> None:
        self.camera_np.setX(x + 5)
        self.camera_np.setY(y + 5)
        self.camera_np.setZ(z + 5)
        self.camera_np.lookAt(x, y, z)

    def open(self) -> None:
        if self.is_open:
            return

        self.is_open = True
        self.make_camera_region()

    def close(self) -> None:
        self.is_open = False
        self.app.closeWindow(self.window)
        self._window = None
        self._lens = None
        self._camera = None
        self._camera_np = None