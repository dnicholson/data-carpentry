import pdb
import argparse
import calendar

import warnings
import numpy
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.coord_categorisation
import cmocean


def read_data(fname, month):
    """Read an input data file"""

    cube = iris.load_cube(fname, 'precipitation_flux')

    iris.coord_categorisation.add_month(cube, 'time')
    cube = cube.extract(iris.Constraint(month=month))

    return cube


def convert_pr_units(cube):
    """Convert kg m-2 s-1 to mm day-1"""

    cube.data = cube.data * 86400
    cube.units = 'mm/day'

    return cube


def plot_data(cube, month, gridlines=False,levels=None):
    """Plot the data."""

    fig = plt.figure(figsize=[12,5])
    iplt.contourf(cube, cmap=cmocean.cm.haline_r,
                  levels=levels,
                  extend='max')

    plt.gca().coastlines()
    if gridlines:
        plt.gca().gridlines()
    cbar = plt.colorbar()
    cbar.set_label(str(cube.units))

    title = '%s precipitation climatology (%s)' %(cube.attributes['model_id'], month)
    plt.title(title)

def apply_mask(cube,maskfile,realm):
    sftlf_cube = iris.load_cube(maskfile, 'land_area_fraction')
    pdb.set_trace()
    if realm == 'ocean':
        mask = numpy.where(sftlf_cube.data < 50, True, False)
    elif realm == 'land':
        mask = numpy.where(sftlf_cube.data > 50, True, False)
    cube.data = numpy.ma.asarray(cube.data)
    cube.data.mask = mask
    return cube

def main(inargs):
    """Run the program."""
    warnings.filterwarnings('ignore')
    cube = read_data(inargs.infile, inargs.month)
    cube = apply_mask(cube,inargs.mask[0],inargs.mask[1])
    #pdb.set_trace()
    cube = convert_pr_units(cube)
    clim = cube.collapsed('time', iris.analysis.MEAN)
    plot_data(clim, inargs.month,gridlines=inargs.gridlines,levels=inargs.cbar_levs)
    plt.savefig(inargs.outfile)


if __name__ == '__main__':
    description='Plot the precipitation climatology.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("month", type=str, choices=['Jan','Feb','Mar','Apr',
        'May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],help="Month to plot")
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("-g", "--gridlines", action="store_true",
        help="add gridlines to plot")
    parser.add_argument('--cbar_levs', type=float,nargs='*', default=None,
        help='contour levels')
    parser.add_argument("--mask", type=str, nargs=2,
                    metavar=('SFTLF_FILE', 'REALM'), default=None,
                    help='Apply a land or ocean mask (specify the realm to mask)')

    args = parser.parse_args()

    main(args)
