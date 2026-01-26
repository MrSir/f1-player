
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from panda3d.core import Camera

from f1p.ui.components.camera.enums import CameraType
from f1p.ui.components.camera.types import CameraController, OrbitingCameraController, TopDownCameraController


class MainCameraController(DirectObject):
    controller: CameraController
    camera_type: CameraType

    def __init__(self, task_manager: TaskManager, camera: Camera):
        super().__init__()

        self.task_manager = task_manager
        self.camera = camera
        self.enabled = False

        self.camera_controllers: dict[CameraType, CameraController] = {}
        self.camera_type: CameraType = CameraType.ORBITING

        self.accept("sessionSelected", self.enable)
        self.accept("wheel_up", self.zoom_camera_in)
        self.accept("wheel_down", self.zoom_camera_out)
        self.accept("switchCamera", self.switch_camera)

    def configure(self) -> None:
        self.camera_controllers[CameraType.ORBITING] = OrbitingCameraController(self.camera)
        self.camera_controllers[CameraType.TOP_DOWN] = TopDownCameraController(self.camera)

        self.camera_type = CameraType.ORBITING
        self.controller = self.camera_controllers[self.camera_type]
        self.controller.re_center()

    def enable(self) -> None:
        self.enabled = True

        self.task_manager.add(self.animate_camera, "animate_camera")

    def zoom_camera_in(self) -> None:
        if not self.enabled:
            return

        self.controller.zoom_camera_in()

    def zoom_camera_out(self) -> None:
        if not self.enabled:
            return

        self.controller.zoom_camera_out()

    def switch_camera(self, camera_type: CameraType) -> None:
        self.camera_type = camera_type
        self.controller = self.camera_controllers[self.camera_type]
        self.controller.re_center()

    def animate_camera(self, task) -> None:
        self.controller.animate_camera()

        return task.cont
