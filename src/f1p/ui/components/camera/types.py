from math import cos, sin

from panda3d.core import Camera, deg2Rad


class CameraController:
    def __init__(
        self,
        camera: Camera,
        pos: tuple[float, float, float],
        look_at: tuple[float, float, float] = (0, 0, 0),
    ):
        self.camera = camera
        self.default_pos = pos
        self.default_look_at = look_at

        self.current_look_at = self.default_look_at

        self.zoom = 0
        self.mouse_x = 0
        self.mouse_y = 0

    def re_center(self) -> None:
        self.camera.setPos(*self.default_pos)
        self.camera.lookAt(*self.default_look_at)

    def animate_camera(self) -> None: ...

    def zoom_camera_in(self) -> None:
        if self.zoom + 1 > 100:
            self.zoom = 100
            return

        self.zoom += 1

        self.move_camera()

    def zoom_camera_out(self) -> None:
        if self.zoom - 1 < 10:
            self.zoom = 10
            return

        self.zoom -= 1

        self.move_camera()

    def move_camera(self) -> None: ...


class OrbitingCameraController(CameraController):
    def __init__(self, camera: Camera):
        super().__init__(camera, (0, -70, 40))

        self.rotation = 0

    @staticmethod
    def rotate_around_z(current_x: float, current_y: float, rad: float) -> tuple[float, float]:
        x = (current_x * cos(rad)) - (current_y * sin(rad))
        y = (current_x * sin(rad)) + (current_y * cos(rad))

        return x, y

    def animate_camera(self) -> None:
        current_x = self.camera.getX()
        current_y = self.camera.getY()

        rad = deg2Rad(0.3)
        self.rotation += rad

        x, y = self.rotate_around_z(current_x, current_y, rad)

        self.camera.setX(x)
        self.camera.setY(y)
        self.camera.lookAt(*self.default_look_at)

    def move_camera(self) -> None:
        movement_amount = -10

        la_x, la_y, la_z = self.default_look_at
        pos_x, pos_y, pos_z = self.default_pos

        pos_x_rotated, pos_y_rotated = self.rotate_around_z(pos_x, pos_y, self.rotation)

        multiplier = 1 - (self.zoom / 100)
        x = la_x + ((pos_x_rotated - la_x) * multiplier)
        y = la_y + ((pos_y_rotated - la_y) * multiplier)

        moved_z = movement_amount * self.mouse_y
        z = la_z + ((pos_z - la_z) * multiplier) + moved_z

        self.camera.setPos(x, y, z)
        self.camera.lookAt(la_x, la_y, la_z)


class TopDownCameraController(CameraController):
    def __init__(self, camera: Camera):
        super().__init__(camera, (0, 0, 100))

    def move_camera(self) -> None:
        movement_amount = -10

        la_x, la_y, la_z = self.default_look_at
        pos_x, pos_y, pos_z = self.default_pos

        moved_x = movement_amount * self.mouse_x
        moved_y = movement_amount * self.mouse_y

        multiplier = 1 - (self.zoom / 100)
        x = la_x + moved_x + ((pos_x - la_x) * multiplier)
        y = la_y + moved_y + ((pos_y - la_y) * multiplier)
        z = la_z + ((pos_z - la_z) * multiplier)

        self.camera.setPos(x, y, z)
        self.camera.lookAt(la_x + moved_x, la_y + moved_y, la_z)
