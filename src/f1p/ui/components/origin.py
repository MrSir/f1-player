from panda3d.core import LineSegs, NodePath, Vec4


class Origin:
    def __init__(self, parent: NodePath):
        self.parent = parent

    def draw_line(self, parent_nodepath, color, start_point, end_point):
        lines = LineSegs()
        lines.setColor(color)
        lines.setThickness(3)  # Set desired thickness in pixels
        lines.moveTo(*start_point)
        lines.drawTo(*end_point)

        line_node_path = parent_nodepath.attach_new_node(lines.create())
        line_node_path.set_depth_test(False)
        line_node_path.set_depth_write(False)

    def render(self):
        axes = NodePath("WorldAxes")
        axes.reparentTo(self.parent)

        # X-axis (Red)
        self.draw_line(axes, Vec4(1, 0, 0, 1), (0, 0, 0), (5, 0, 0))
        # Y-axis (Green - typically points into depth in Panda3D's default system)
        self.draw_line(axes, Vec4(0, 1, 0, 1), (0, 0, 0), (0, 5, 0))
        # Z-axis (Blue - typically points up in Panda3D's default system)
        self.draw_line(axes, Vec4(0, 0, 1, 1), (0, 0, 0), (0, 0, 5))
