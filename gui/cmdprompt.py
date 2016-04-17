import termbox

from gui.util import ScreenArea as ScreenArea
from gui.util import Drawable as Drawable

class CmdPrompt(Drawable):
    """Represents the command prompt bar in the Kanban Board"""

    DEFAULT_CMD_PROMPT = ">> "

    def receive_input(self, char):
        """Recieve one character of input into the internal buffer

        Args:
            char: one unicode character
        """
        self._buffer += char


    def receive_backspace(self):
        """Receives a backspace

        Manipulates the buffer accordingly
        """
        # remove the last character in the buffer
        self._buffer = self._buffer[:-1]


    def receive_space(self):
        """Receives a space

        Manipulates the buffer accordingly
        """
        self._buffer += " "


    def evaluate_buffer(self):
        """Evaluate the current contents of the internal buffer

        This function will then clear out the buffer again
        """
        # TODO: evaluate buffer
        self._buffer = CmdPrompt.DEFAULT_CMD_PROMPT


    def draw(self):
        """Overridden draw() function from drawable superclass"""
        tlx = self.screen_area.upper_left_x
        tly = self.screen_area.upper_left_y
        brx = self.screen_area.bottom_right_x
        bry = self.screen_area.bottom_right_y

        # draw borders
        for x in range(tlx, brx + 1):
            self.display.change_cell(x, tly, ord('-'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(x, bry, ord('-'), termbox.DEFAULT, termbox.DEFAULT)
        for y in range(tly, bry):
            self.display.change_cell(tlx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(brx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)

        # draw buffer
        #
        # we first want to remove any characters in the beginning that can't be displayed
        display_width = (brx - tlx) - 2  # 2 for the 2 ends of the border
        if len(self._buffer) > display_width:
            display_buffer = self._buffer[:display_buffer]
        else:
            display_buffer = self._buffer[:] # make a copy

        y_coord = bry - 1  # implicit assumption that (bry - tly) > 2
        for x_coord,str_idx in zip(range(tlx + 1, brx), range(len(display_buffer))):
            self.display.change_cell(x_coord, 
                                     y_coord, 
                                     ord(display_buffer[str_idx]), 
                                     termbox.DEFAULT, 
                                     termbox.DEFAULT)

        # draw the cursor in the correct spot
        x_curs_coord = tlx + len(display_buffer) + 1
        self.display.set_cursor(x_curs_coord ,y_coord)


        self.display.present()


    def __init__(self, kb_board, display, screen_area):
        super().__init__(kb_board, display, screen_area)
        self._buffer = CmdPrompt.DEFAULT_CMD_PROMPT

