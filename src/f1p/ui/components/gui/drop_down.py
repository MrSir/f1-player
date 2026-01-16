from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import B1RELEASE, RAISED, WITHIN, WITHOUT
from direct.gui.DirectOptionMenu import DirectOptionMenu
from panda3d.core import NodePath, StaticTextFont, TextNode

from f1p.ui.components.gui.button import BlackButton


class BlackDropDown(DirectOptionMenu):
    def __init__(
        self,
        parent: NodePath | None = None,
        width: int = 30,
        height: int = 30,
        font: StaticTextFont | None = None,
        font_scale: float = 1.0,
        popup_menu_below: bool = True,
        scale: float = 1.0,
        item_scale: float = 1.0,
        frameColor: tuple[float, float, float, float] = (0.15, 0.15, 0.15, 1),
        highlightColor: tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1),
        highlightScale: tuple[float, float] = (0.9, 0.9),
        borderWidth: tuple[float, float] = (3, 3),
        pressEffect: int = 1,
        text_fg: tuple[float, float, float, float] = (1, 1, 1, 1),
        text_pos: tuple[float, float] = (0, 0),
        items: list[str] | None = None,
        **kwargs,
    ):
        self.width = width
        self.height = height
        self.font = font
        self.font_scale = font_scale
        self.popup_menu_below = popup_menu_below

        self.scale = scale
        self.item_scale = item_scale
        self.frame_size = (0, width, -height / 2, height / 2)
        self.frame_color = frameColor
        self.highlight_color = highlightColor
        self.highlight_scale = highlightScale
        self.border_width = borderWidth
        self.press_effect = pressEffect
        self.text_font = self.font
        self.text_scale = self.font_scale
        self.text_fg = text_fg
        self.text_pos = text_pos
        self.items = items if items else []
        self.item_frame_size = (0, width, -(height * self.item_scale) / 2, (height * self.item_scale) / 2)
        self.item_frame_color = frameColor
        self.item_text_font = self.font
        self.item_text_scale = self.font_scale * self.item_scale
        self.item_text_fg = text_fg
        self.item_text_pos = (text_pos[0], text_pos[1] * self.item_scale)
        self.item_border_width = borderWidth
        self.item_press_effect = pressEffect

        default_options = (
            ("scale", self.scale, None),
            ("frameSize", self.frame_size, None),
            ("frameColor", self.frame_color, None),
            ("highlightColor", self.highlight_color, None),
            ("highlightScale", self.highlight_scale, None),
            ("relief", RAISED, None),
            ("borderWidth", self.border_width, None),
            ("pressEffect", self.press_effect, None),
            ("text_font", self.font, None),
            ("text_scale", self.font_scale, None),
            ("text_fg", self.text_fg, None),
            ("text_pos", self.text_pos, None),
            ("items", self.items, self.setItems),
            ("item_frameSize", self.item_frame_size, None),
            ("item_frameColor", self.item_frame_color, None),
            ("item_text_font", self.item_text_font, None),
            ("item_text_scale", self.item_text_scale, None),
            ("item_text_fg", self.item_text_fg, None),
            ("item_text_pos", self.item_text_pos, None),
            ("item_relief", RAISED, None),
            ("item_borderWidth", self.item_border_width, None),
            ("item_pressEffect", self.item_press_effect, None),
        )
        self.defineoptions(kwargs, default_options)

        DirectOptionMenu.__init__(self, parent, **kwargs)

        self.initialiseoptions(BlackDropDown)

    def setItems(self):
        """
        self['items'] = itemList
        Create new popup menu to reflect specified set of items
        """
        # Remove old component if it exits
        if self.popupMenu is not None:
            self.destroycomponent("popupMenu")
        # Create new component
        self.popupMenu = self.createcomponent(
            "popupMenu",
            (),
            None,
            DirectFrame,
            (self,),
            frameColor=(0, 0, 0, 0),
            relief=RAISED,
        )
        # Make sure it is on top of all the other gui widgets
        self.popupMenu.setBin("gui-popup", 0)
        self.highlightedIndex = None
        if not self["items"]:
            return
        # Create a new component for each item
        # Find the maximum extents of all items
        itemIndex = 0
        self.minX = self.maxX = self.minZ = self.maxZ = None
        for item in self["items"]:
            c = self.createcomponent(
                "item%d" % itemIndex,
                (),
                "item",
                BlackButton,
                (self.popupMenu,),
                text=item,
                frameSize=self.item_frame_size,
                frameColor=self.item_frame_color,
                text_align=TextNode.ALeft,
                text_font=self.item_text_font,
                text_scale=self.item_text_scale,
                text_fg=self.item_text_fg,
                text_pos=self.item_text_pos,
                relief=RAISED,
                borderWidth=self.item_border_width,
                pressEffect=self.item_press_effect,
                command=lambda i=itemIndex: self.set(i),
            )
            bounds = c.getBounds()

            if self.minX is None:
                self.minX = bounds[0]
            elif bounds[0] < self.minX:
                self.minX = bounds[0]
            if self.maxX is None:
                self.maxX = bounds[1]
            elif bounds[1] > self.maxX:
                self.maxX = bounds[1]
            if self.minZ is None:
                self.minZ = bounds[2]
            elif bounds[2] < self.minZ:
                self.minZ = bounds[2]
            if self.maxZ is None:
                self.maxZ = bounds[3]
            elif bounds[3] > self.maxZ:
                self.maxZ = bounds[3]
            itemIndex += 1
        # Calc max width and height
        self.maxWidth = self.maxX - self.minX
        self.maxHeight = self.maxZ - self.minZ
        # Adjust frame size for each item and bind actions to mouse events
        for i in range(itemIndex):
            item = self.component("item%d" % i)
            # So entire extent of item's slot on popup is reactive to mouse
            item["frameSize"] = self.item_frame_size
            # Move it to its correct position on the popup
            item.setPos(0, 0, (i * (-self.height * self.item_scale)))
            item.bind(B1RELEASE, self.hidePopupMenu)
            # Highlight background when mouse is in item
            item.bind(WITHIN, lambda _, index=i, the_item=item: self._highlightItem(the_item, index))
            # Restore specified color upon exiting
            fc = item["frameColor"]
            item.bind(WITHOUT, lambda _, the_item=item, frame_color=fc: self._unhighlightItem(the_item, frame_color))
        # Set popup menu frame size to encompass all items
        f = self.component("popupMenu")
        f["frameSize"] = (0, self.width, -self.maxHeight * itemIndex, 0)

        # Determine what initial item to display and set text accordingly
        if self["initialitem"]:
            self.set(self["initialitem"], fCommand=0)
        else:
            # No initial item specified, just use first item
            self.set(0, fCommand=0)

        # Position popup Marker to the right of the button
        pm = self.popupMarker
        pmw = pm.getWidth() * pm.getScale()[0] + 2 * self["popupMarkerBorder"][0]
        if self.initFrameSize:
            # Use specified frame size
            bounds = list(self.initFrameSize)
        else:
            # Or base it upon largest item
            bounds = [self.minX, self.maxX, self.minZ, self.maxZ]
        if self.initPopupMarkerPos:
            # Use specified position
            pmPos = list(self.initPopupMarkerPos)
        else:
            # Or base the position on the frame size.
            pmPos = [bounds[1] + pmw / 2.0, 0, bounds[2] + (bounds[3] - bounds[2]) / 2.0]
        pm.setPos(pmPos[0], pmPos[1], pmPos[2])
        # Adjust popup menu button to fit all items (or use user specified
        # frame size
        bounds[1] += pmw
        self["frameSize"] = (bounds[0], bounds[1], bounds[2], bounds[3])
        # Set initial state
        self.hidePopupMenu()

    def showPopupMenu(self, event=None):
        super().showPopupMenu(event=event)

        self.popupMenu.setX(0)

        z_coordinate = -self.height + 6
        if not self.popup_menu_below:
            z_coordinate = self.height * self.item_scale * len(self.items)
        self.popupMenu.setZ(z_coordinate)

    def _highlightItem(self, item, index):
        self._prevItemTextScale = item["text_scale"]
        item["frameColor"] = self.highlight_color
        item["frameSize"] = self.item_frame_size
        item["text_scale"] = (self.item_text_scale, self.item_text_scale)  # OVERRODE THE INSANITY THAT WAS THIS LINE
        self.highlightedIndex = index

    def _unhighlightItem(self, item, frameColor):
        item["frameColor"] = frameColor
        item["frameSize"] = self.item_frame_size
        item["text_scale"] = self._prevItemTextScale
        self.highlightedIndex = None
