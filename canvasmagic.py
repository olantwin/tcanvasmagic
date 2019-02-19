# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
    cell_magic,
    line_cell_magic,
)

from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

import random


def uniqueid():
    seed = random.getrandbits(32)
    while True:
        yield seed
        seed += 1


# The class MUST call this class decorator at creation time
@magics_class
class CanvasMagics(Magics):
    def __init__(self, shell):
        # You must call the parent constructor
        super(CanvasMagics, self).__init__(shell)
        self.unique_sequence = uniqueid()

    @magic_arguments()
    @argument(
        "-s",
        "--size",
        action="store",
        type=str,
        default=None,
        help='Pixel size of plots, "width,height". If not specified, use ROOT default.',
    )
    @argument(
        "-S",
        "--save",
        action="store",
        type=str,
        default=None,
        help="Save a copy to file, e.g., -S filename. Default is None",
    )
    @argument(
        "--name",
        action="store",
        type=str,
        default=None,
        help="Set canvas name for further use.",
    )
    @argument("code", nargs="*")
    @line_cell_magic
    def canvas(self, line, cell=None):
        args = parse_argstring(self.canvas, line)
        size = args.size
        width, height = size.split(",") if size else (None, None)
        uid = next(self.unique_sequence)
        if not cell:
            cell = str("").join(args.code)
        constructor = (
            "ROOT.TCanvas('{uid}', '{uid}', {width}, {height})".format(
                uid=uid, width=width, height=height
            )
            if size
            else "ROOT.TCanvas()"
        )
        canvas_name = args.name if args.name else "__c_{uid}__".format(uid=uid)
        cell = (
            canvas_name
            + " = {constructor}\n".format(constructor=constructor)
            + cell
            + "\n"
            + canvas_name
            + ".Draw()"
        )
        if args.save:
            cell += "\n" + canvas_name + ".SaveAs({})".format(args.save)
        self.shell.run_cell(cell)


# In order to actually use these magics, you must register them with a
# running IPython.


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(CanvasMagics)
