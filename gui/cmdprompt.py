import termbox

from gui.util import ScreenArea as ScreenArea
from gui.util import Drawable as Drawable

class CmdPrompt(Drawable):
    """Represents the command prompt bar in the Kanban Board"""

    DEFAULT_CMD_PROMPT = ">> "
    CMD_ERROR = '(Previous command invalid) >> '

    CMD_ACTION_QUIT = 0
    CMD_ACTION_ERROR = 1
    CMD_ACTION_OK = 2

    def _buffer_error(self):
        """Set the buffer to the error string

        Returns:
            Error code (CmdPrompt constant)
        """
        self._buffer = CmdPrompt.CMD_ERROR
        return CmdPrompt.CMD_ACTION_ERROR


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

        Returns:
            Action to perform (as a CmdPrompt constant)
        """
        buf = self._buffer

        # strip the command prompt if it exists
        if buf.startswith(CmdPrompt.DEFAULT_CMD_PROMPT):
            buf = buf[len(CmdPrompt.DEFAULT_CMD_PROMPT):]
        elif buf.startswith(CmdPrompt.CMD_ERROR):
            buf = buf[len(CmdPrompt.CMD_ERROR):]


        command_tokens = [tok.lower() for tok in buf.split(' ')]

        if len(command_tokens) == 1 and command_tokens[0] == '/sync':
            self.kb_board.sync()

        elif len(command_tokens) >= 1 and command_tokens[0] == '/new':
            self.kb_board.new_task(' '.join(command_tokens[1:]))

        elif len(command_tokens) == 4 and command_tokens[0] == '/move':
            task = self._task_id_map[int(command_tokens[1])]
            dest_stage = str(command_tokens[3])

            # some basic error checking
            if dest_stage not in self.kb_board.get_stage_names():
                self._buffer_error()
            elif command_tokens[2] != "to":
                self._buffer_error()

            # call kbb API
            self.kb_board.move_task(task.task_id, dest_stage)

        elif len(command_tokens) == 2 and command_tokens[0] == '/delete':
            task = self._task_id_map[int(command_tokens[1])]
            self.kb_board.delete_task(task.task_id)

        elif len(command_tokens) == 1 and command_tokens[0] == '/quit':
            return CmdPrompt.CMD_ACTION_QUIT

        else:
            return self._buffer_error()

        # empty/reset the buffer
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
            display_buffer = self._buffer[-display_width:]
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


    def __init__(self, kb_board, display, screen_area, task_id_map):
        super().__init__(kb_board, display, screen_area)
        self._buffer = CmdPrompt.DEFAULT_CMD_PROMPT
        self._task_id_map = task_id_map

