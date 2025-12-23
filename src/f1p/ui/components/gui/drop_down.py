from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import RAISED, B1RELEASE, WITHIN, WITHOUT
from direct.gui.DirectOptionMenu import DirectOptionMenu
from panda3d.core import StaticTextFont, NodePath, TextNode


class BlackDropDown(DirectOptionMenu):
    def __init__(
        self,
        parent: NodePath | None = None,
        width: int = 30,
        height: int = 30,
        font: StaticTextFont | None = None,
        font_scale: float = 1.0,
        popup_menu_below: bool = True,
        **kwargs,
    ):
        self.width = width
        self.height = height
        self.font = font
        self.font_scale = font_scale
        self.popup_menu_below = popup_menu_below

        default_options = (
            ("scale", 1, None),
            ("frameSize", (0, width, -height / 2, height / 2), None),
            ("frameColor", (0.1, 0.1, 0.1, 1), None),
            ("highlightColor", (0.2, 0.2, 0.2, 1), None),
            ("highlightScale", (1, 1), None),
            ("relief", RAISED, None),
            ("borderWidth", (3, 3), None),
            ("pressEffect", 1, None),
            ("text_font", self.font, None),
            ("text_scale", self.font_scale, None),
            ("text_fg", (1, 1, 1, 1), None),
            ("item_frameColor", (0.1, 0.1, 0.1, 1), None),
            ("item_text_font", self.font, None),
            ("item_text_scale", self.font_scale, None),
            ("item_text_fg", (1, 1, 1, 1), None),
            ("item_relief", RAISED, None),
            ("item_borderWidth", (3, 3), None),
            ("item_pressEffect", 1, None),
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
        if self.popupMenu != None:
            self.destroycomponent('popupMenu')
        # Create new component
        self.popupMenu = self.createcomponent(
            'popupMenu',
            (),
            None,
            DirectFrame,
            (self,),
            relief='raised',
        )
        # Make sure it is on top of all the other gui widgets
        self.popupMenu.setBin('gui-popup', 0)
        self.highlightedIndex = None
        if not self['items']:
            return
        # Create a new component for each item
        # Find the maximum extents of all items
        itemIndex = 0
        self.minX = self.maxX = self.minZ = self.maxZ = None
        for item in self['items']:
            c = self.createcomponent(
                'item%d' % itemIndex,
                (),
                'item',
                DirectButton,
                (self.popupMenu,),
                text=item,
                text_align=TextNode.ALeft,
                command=lambda i=itemIndex: self.set(i)
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
            item = self.component('item%d' % i)
            # So entire extent of item's slot on popup is reactive to mouse
            item['frameSize'] = (0, self.width, -self.height / 2, self.height / 2)
            # Move it to its correct position on the popup
            item.setPos(0, 0, (i * (-self.height)) + 5)
            item.bind(B1RELEASE, self.hidePopupMenu)
            # Highlight background when mouse is in item
            item.bind(WITHIN, lambda x, i=i, item=item: self._highlightItem(item, i))
            # Restore specified color upon exiting
            fc = item['frameColor']
            item.bind(WITHOUT, lambda x, item=item, fc=fc: self._unhighlightItem(item, fc))
        # Set popup menu frame size to encompass all items
        f = self.component('popupMenu')
        f['frameSize'] = (0, self.width, -self.maxHeight * itemIndex, 0)

        # Determine what initial item to display and set text accordingly
        if self['initialitem']:
            self.set(self['initialitem'], fCommand=0)
        else:
            # No initial item specified, just use first item
            self.set(0, fCommand=0)

        # Position popup Marker to the right of the button
        pm = self.popupMarker
        pmw = (pm.getWidth() * pm.getScale()[0] +
               2 * self['popupMarkerBorder'][0])
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
        self['frameSize'] = (bounds[0], bounds[1], bounds[2], bounds[3])
        # Set initial state
        self.hidePopupMenu()

    def showPopupMenu(self, event=None):
        super().showPopupMenu(event=event)

        self.popupMenu.setX(0)
        self.popupMenu.setZ(-self.height + 3 if self.popup_menu_below else self.popupMenu.getHeight() + self.height / 2)

    def _highlightItem(self, item, index):
        self._prevItemTextScale = item['text_scale']
        item['frameColor'] = self['highlightColor']
        item['frameSize'] = (0, self.width, -self.height / 2, self.height / 2)
        item['text_scale'] = (self.font_scale, self.font_scale)  # OVERRODE THE INSANITY THAT WAS THIS LINE
        self.highlightedIndex = index

    def _unhighlightItem(self, item, frameColor):
        item['frameColor'] = frameColor
        item['frameSize'] = (0, self.width, -self.height / 2, self.height / 2)
        item['text_scale'] = self._prevItemTextScale
        self.highlightedIndex = None
