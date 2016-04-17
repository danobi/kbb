class ScreenArea(object):
    """Struct class for representing a rectangular section of the screen

    (upper_left_x, 
     upper_left_y)
               *-------------------
               |                  |
               |                  |
               |                  |
               |                  |
               -------------------*
                                (bottom_left_x,
                                 bottom_left_y)
    """ 

    def __init__(self, upper_left_x, upper_left_y, bottom_right_x, bottom_right_y):
        self.upper_left_x = upper_left_x
        self.upper_left_y = upper_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y


class Drawable(object):
    """Base class for representing a drawable object

    Provided base class functions are:
        - __init__
        - resize
        - draw

    Note that before :func:`draw` is called, the internal cell buffer for the
    entire :var:`display` must be cleared
    """

    def resize(self, new_screen_area):
        """Resize the drawable area of this object
        
        Args:
            new_screen_area: the new screen area of type :class:`ScreenArea`
        """
        self.screen_area = screen_area


    def draw(self):
        """Draw the contents of the area belonging to this object

        Precondition: the internal cell buffer for :var:`display` must be
        cleared before this funciton is called
        """
        raise NotImplementedError('draw() not implemented')


    def __init__(self, kb_board, display, screen_area):
        self.kb_board = kb_board
        self.display = display
        self.screen_area = screen_area

