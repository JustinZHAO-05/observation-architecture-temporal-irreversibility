import sys

sys.dont_write_bytecode = True

from common import cli
from fig12 import fig1, fig2

from fig34 import fig3, fig4

from fig56 import fig5, fig6

from supp14 import sup1, sup2, sup3, sup4

from supp58 import sup5, sup6, sup7, sup8

BUILDERS = {"Fig2": fig2, "Fig1": fig1, "Fig3": fig3, "Fig4": fig4, "Fig5": fig5, "Fig6": fig6, "FigS1": sup1, "FigS2": sup2, "FigS3": sup3, "FigS4": sup4, "FigS5": sup5, "FigS6": sup6, "FigS7": sup7, "FigS8": sup8}

if __name__ == "__main__":
    cli(BUILDERS)
