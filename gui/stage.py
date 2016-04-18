import math
from datetime import datetime
from datetime import timedelta

import termbox

from gui.util import ScreenArea as ScreenArea
from gui.util import Drawable as Drawable


class Task(Drawable):
    """Represents a single task to be displayed in a stage"""

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

        # generate task title
        disp_task_title = "[{0}] {1}".format(self._id_num, self._task.title)

        # draw task title
        y = tly + self._vertical_padding
        for cell_x, title_idx in zip(range(tlx + 1, brx), range(len(disp_task_title))):
            self.display.change_cell(cell_x, y, ord(disp_task_title[title_idx]), termbox.DEFAULT, termbox.DEFAULT)

        self.display.present()


    def __init__(self, kb_board, display, screen_area, task, vertical_padding, id_num):
        super().__init__(kb_board, display, screen_area)
        self._task = task
        self._vertical_padding = vertical_padding
        self._id_num = id_num


class Stage(Drawable):
    """Represents a single stage in the Kanban Board"""

    # how many vertical lines to pad the display content of each task
    TASK_VERTICAL_PADDING = 1

    # how many cells to left pad the stage name
    STAGE_NAME_LEFT_PAD = 2;


    @staticmethod
    def _get_lowest_unused_display_id(task_id_map):
        """Gets the lowest unused display id

        Args:
            task_id_map: dictionary of task->id mappings

        Returns:
            Lowest unused integer in :var:`task_id_map`
        """
        lowest = 0
        while True:
            if lowest not in task_id_map.keys():
                return lowest
            else:
                lowest += 1


    def draw(self):
        tlx = self.screen_area.upper_left_x
        tly = self.screen_area.upper_left_y
        brx = self.screen_area.bottom_right_x
        bry = self.screen_area.bottom_right_y

        # draw stage title
        if self._stage_name == self.kb_board.get_stage_names()[0]:
            # red for first stage tasks
            stage_name_color = termbox.RED
        elif self._stage_name == self.kb_board.get_stage_names()[-1]:
            # green for final stage tasks
            stage_name_color = termbox.GREEN
        else:
            # all other stages get yellow
            stage_name_color = termbox.YELLOW
        for xcoord, name_idx in zip(range(tlx + Stage.STAGE_NAME_LEFT_PAD, brx), range(len(self._stage_name))):
            self.display.change_cell(xcoord, tly, ord(self._stage_name[name_idx]), termbox.BLACK, stage_name_color)

        # now the top of the "rest of the stage" is 1 cell down
        tly += 1

        # draw borders
        for y in range(tly, bry + 1):
            self.display.change_cell(tlx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(brx, y, ord('|'), termbox.DEFAULT, termbox.DEFAULT)
        for x in range(tlx, brx + 1):
            self.display.change_cell(x, tly, ord('-'), termbox.DEFAULT, termbox.DEFAULT)
            self.display.change_cell(x, bry, ord('-'), termbox.DEFAULT, termbox.DEFAULT)


        # draw tasks
        tasks_in_stage = [t for t in self.kb_board.get_task_list() if t.stage == self._stage_name]
        
        # now filter out all tasks that aren't in our lookahead range
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        date_range = timedelta(days=self._lookahead_days)
        # Note: timedelta() == 0
        tasks_in_due_range = [t for t in tasks_in_stage if ((t.due - today) <= date_range) and ((t.due - today) >= timedelta())]

        # we may only be able to display a certain number of tasks, so only keep the latest 
        # number of tasks
        total_task_height = 1 + (2 * Stage.TASK_VERTICAL_PADDING)
        account_for_borders = 2
        max_num_tasks = math.floor((bry - tly - account_for_borders) / total_task_height) 
        tasks_to_display = tasks_in_due_range[:max_num_tasks]

        # now we can draw all the tasks to the screen
        for idx, task in enumerate(tasks_to_display):
            task_tlx = tlx + 1
            task_tly = math.floor((idx / max_num_tasks) * (bry - tly)) + 2 # +2 at the end b/c of top border & stage title
            task_brx = brx - 1
            task_bry = math.floor(((idx + 1) / max_num_tasks) * (bry - tly)) + 2 # +2 at the end b/c of top border & stage title
            disp_area = ScreenArea(task_tlx, task_tly, task_brx, task_bry)

            # set the id->task mapping
            lowest_id_num = Stage._get_lowest_unused_display_id(self._task_id_map)
            self._task_id_map[lowest_id_num] = task

            # create & display task
            disp_task = Task(self.kb_board, self.display, disp_area, task, Stage.TASK_VERTICAL_PADDING, lowest_id_num)
            disp_task.draw()
            
        self.display.present()


    def __init__(self, kb_board, display, screen_area, stage_name, lookahead_days, task_id_map):
        super().__init__(kb_board, display, screen_area)
        self._stage_name = stage_name
        self._lookahead_days = lookahead_days
        self._task_id_map = task_id_map
