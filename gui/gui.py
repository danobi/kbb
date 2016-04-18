import time
import math
import sys

import termbox

import kbb
from gui.util import ScreenArea as ScreenArea
from gui.util import Drawable as Drawable
from gui.stage import Stage as Stage
from gui.cmdprompt import CmdPrompt as CmdPrompt



class GUI(object):
    """Top level object for creating & using the kbb GUI"""

    WINDOW_EDGE_LEEWAY = 1
    CMD_PROMPT_HEIGHT = 2
    LOOKAHEAD_DAYS = 7


    def _create_stages(self):
        """Inits all the stages

        Returns:
            list of :class:`Stage` objects
        """
        ret_stages = list() 
        stage_height = self.display.height() - GUI.WINDOW_EDGE_LEEWAY - GUI.CMD_PROMPT_HEIGHT
        stage_width = self.display.width() - GUI.WINDOW_EDGE_LEEWAY 
        stages = self.kb_board.get_stage_names()
        num_stages = len(stages)

        for idx, stage_name in enumerate(stages):
            # correctly size each stage
            upper_left_x = math.floor(stage_width / num_stages * idx)
            if upper_left_x == 0:
                upper_left_x += GUI.WINDOW_EDGE_LEEWAY  # do this for very left edge
            upper_left_y = GUI.WINDOW_EDGE_LEEWAY
            bottom_right_x = math.floor(stage_width / num_stages * (idx + 1))
            bottom_right_y = stage_height

            screen_area = ScreenArea(upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
            stage = Stage(self.kb_board, self.display, screen_area, stage_name, GUI.LOOKAHEAD_DAYS, self._task_id_map)
            ret_stages.append(stage)

        return ret_stages

    
    def _create_cmd_prompt(self):
        """Inits the command prompt

        Returns:
            :class:`CmdPrompt` object
        """
        upper_left_x = GUI.WINDOW_EDGE_LEEWAY
        upper_left_y = self.display.height() - GUI.CMD_PROMPT_HEIGHT - 1
        bottom_right_x = self.display.width() - GUI.WINDOW_EDGE_LEEWAY
        bottom_right_y = self.display.height() - GUI.WINDOW_EDGE_LEEWAY

        screen_area = ScreenArea(upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
        cmd_prompt = CmdPrompt(self.kb_board, self.display, screen_area, self._task_id_map)

        return cmd_prompt

    
    def receive_input(self, char):
        """Receive one character of input

        Args:
            char: one unicode character
        """
        self._cmd_prompt.receive_input(char)

    
    def receive_backspace(self):
        """Receive a backspace character"""
        self._cmd_prompt.receive_backspace()


    def receive_space(self):
        """Receive a backspace character"""
        self._cmd_prompt.receive_space()



    def evaluate_buffer(self):
        """Evaluate the cmd_prompt buffer
        
        Returns:
            The propagated return value from CmdPrompt.evaluate_buffer()
        """
        return self._cmd_prompt.evaluate_buffer()


    def draw(self):
        """Overriden draw() method from superclass"""
        # as a precondition to drawing, we need to clear the cell bufffer
        self.display.clear()

        # we have to clear out the "global" _task_id_map because the mappings might
        # change if the window resizes or tasks get moved around
        self._task_id_map.clear()

        # now we can draw all our objects
        [stage.draw() for stage in self._stages]
        self._cmd_prompt.draw()
        self.display.present()
                

    def __init__(self):
        """Init

        _task_id_map is essentially a global dictionary mapping low value integers
        to tasks. This is necessary to manipulate the tasks through the command prompt.
        It's 50% a hack so TODO: fix this
        """
        self.kb_board = kbb.Kbb()
        self.display = termbox.Termbox()
        self._task_id_map = dict()
        self._stages = self._create_stages()
        self._cmd_prompt = self._create_cmd_prompt()
        self.draw()


def main():
    g = GUI()

    while True:
        e_type, unicode_key, key, _, _, _, _, _ = g.display.poll_event()

        if e_type == termbox.EVENT_KEY:
            # quit conditions
            if key == termbox.KEY_CTRL_C:
                g.display.close()
                break

            # character input
            elif unicode_key:
                g.receive_input(unicode_key)

            # space key
            elif key == termbox.KEY_SPACE:
                g.receive_space()

            # backspace
            elif key == termbox.KEY_BACKSPACE or key == termbox.KEY_BACKSPACE2:
                #print('backspace')
                g.receive_backspace()

            # evaluate
            elif key == termbox.KEY_ENTER:
                ret = g.evaluate_buffer()

                if ret == CmdPrompt.CMD_ACTION_QUIT:
                    g.display.close()
                    break

        # enabling this will resolve some bugs (if any) at the cost of decreasing draw performance
        g.draw()
        

if __name__ == '__main__':
    main()
