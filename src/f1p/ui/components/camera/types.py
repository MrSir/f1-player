from math import cos, sin

from panda3d.core import Camera, deg2Rad


class CameraController:
    def __init__(
        self,
        camera: Camera,
        pos: tuple[float, float, float],
        look_at: tuple[float, float, float] = (0, 0, 0)
    ):
        super().__init__()

        self.camera = camera
        self.default_pos = pos
        self.default_look_at = look_at
        self.default_vector = tuple([x - y for x, y in zip(self.default_pos, self.default_look_at)])

        self.zoom = 0

    def re_center(self) -> None:
        self.camera.setPos(*self.default_pos)
        self.camera.lookAt(*self.default_look_at)

    def animate_camera(self) -> None: ...

    def zoom_camera_in(self) -> None:
        if self.zoom + 1 > 100:
            self.zoom = 100
            return

        self.zoom += 1

        self.zoom_camera()

    def zoom_camera_out(self) -> None:
        if self.zoom - 1 < 0:
            self.zoom = 0
            return

        self.zoom -= 1

        self.zoom_camera()

    def zoom_camera(self) -> None: ...


class OrbitingCameraController(CameraController):
    def __init__(self, camera: Camera):
        super().__init__(camera, (0, -70, 40))

        self.rotation = 0

    def rotate_around_z(self, current_x: float, current_y: float, rad: float) -> tuple[float, float]:
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

    def zoom_camera(self) -> None:
        multiplier = 1 - (self.zoom / 100)

        x0, y0, z0 = self.default_look_at
        x1, y1, z1 = self.default_pos
        x1_rotated, y1_rotated = self.rotate_around_z(x1, y1, self.rotation)

        x_old_offset = x1_rotated - x0
        y_old_offset = y1_rotated - y0
        z_old_offset = z1 - z0

        x_offest = x_old_offset * multiplier
        y_offset = y_old_offset * multiplier
        z_offset = z_old_offset * multiplier

        x = x0 + x_offest
        y = y0 + y_offset
        z = z0 + z_offset

        self.camera.setPos(x, y, z)
        self.camera.lookAt(x0, y0, z0)


class TopDownCameraController(CameraController):
    def __init__(self, camera: Camera):
        super().__init__(camera, (0, 0, 100))

    def animate_camera(self) -> None:
        pass

    def zoom_camera(self) -> None:
        multiplier = 1 - (self.zoom / 100)

        x0, y0, z0 = self.default_look_at
        x_old_offset, y_old_offset, z_old_offset = self.default_vector

        x_offest = x_old_offset * multiplier
        y_offset = y_old_offset * multiplier
        z_offset = z_old_offset * multiplier

        x = x0 + x_offest
        y = y0 + y_offset
        z = z0 + z_offset

        self.camera.setPos(x, y, z)
        self.camera.lookAt(x0, y0, z0)