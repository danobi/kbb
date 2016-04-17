import math
from datetime import datetime
from datetime import timedelta

import termbox

from gui.util import ScreenArea as ScreenArea
from gui.util import Drawable as Drawable


class Task(Drawable):
    """Represents a single task to be displayed in a stage"""

    def __init__(self, kb_board, display, screen_area, task, vertical_padding):
        super().__init__(kb_board, display, screen_area)
        self.task = task
        self.vertical_padding = vertical_padding


    def draw(self):
        """Overriden method of superclass"""
        tlx = self.screen_area.upper_left_x
        tly = self.screen_area.upper_left_y
        brx = self.screen_area.bottom_right_x
        bry = self.screen_area.bottom_right_y

        # draw borders
        for x in range(tlx, brx + 1):
            self.display.change_cell(x, tly, ord('-'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(x, bry, ord('-'), termbox.DEFAULT, termbox.DEFAULT)

        # draw task title
        y = tly + self.vertical_padding
        for cell_x, title_idx in zip(range(tlx + 1, brx), range(len(self.task.title))):
            self.display.change_cell(cell_x, y, ord(self.task.title[title_idx]), termbox.DEFAULT, termbox.DEFAULT)

        self.display.present()



class Stage(Drawable):
    """Represents a single stage in the Kanban Board"""

    # how many vertical lines to pad the display content of each task
    TASK_VERTICAL_PADDING = 1

    def draw(self):
        tlx = self.screen_area.upper_left_x
        tly = self.screen_area.upper_left_y
        brx = self.screen_area.bottom_right_x
        bry = self.screen_area.bottom_right_y

        # draw borders
        for y in range(tly, bry + 1):
            self.display.change_cell(tlx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(brx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)
        for x in range(tlx, brx + 1):
            self.display.change_cell(x, tly, ord('-'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(x, bry, ord('-'), termbox.DEFAULT, termbox.DEFAULT)


        # draw tasks
        tasks_in_stage = [t for t in self.kb_board.get_task_list() if t.stage == self.stage_name]
        
        # now filter out all tasks that aren't in our lookahead range
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        date_range = timedelta(days=self.lookahead_days)
        tasks_in_due_range = [t for t in tasks_in_stage if (t.due - today) <= date_range]

        # we may only be able to display a certain number of tasks, so only keep the latest 
        # number of tasks
        total_task_height = 1 + (2 * Stage.TASK_VERTICAL_PADDING)
        account_for_borders = 2
        max_num_tasks = math.floor((bry - tly - account_for_borders) / total_task_height) 
        tasks_to_display = tasks_in_due_range[:max_num_tasks]

        # now we can draw all the tasks to the screen
        for idx, task in enumerate(tasks_to_display):
            task_tlx = tlx + 1
            task_tly = math.floor((idx / max_num_tasks) * (bry - tly)) + 1 # +1 at the end b/c of top border
            task_brx = brx - 1
            task_bry = math.floor(((idx + 1) / max_num_tasks) * (bry - tly)) + 1 # +1 at the end b/c of top border
            disp_area = ScreenArea(task_tlx, task_tly, task_brx, task_bry)

            disp_task = Task(self.kb_board, self.display, disp_area, task, Stage.TASK_VERTICAL_PADDING)
            disp_task.draw()
            
        self.display.present()


    def __init__(self, kb_board, display, screen_area, stage_name, lookahead_days):
        super().__init__(kb_board, display, screen_area)
        self.stage_name = stage_name
        self.lookahead_days = lookahead_days
