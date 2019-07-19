# Convert edf data to BornAgain histogram

from matplotlib import pyplot as plt
from matplotlib import colors
import fabio
import bornagain as ba

DISTANCE = 909.99  # mm
PIX_SIZE = 4*41.74e-6  # m
CENTER_X = 108.2
CENTER_Y = 942.0

# 004_230_P144_im_full.edf - Fig 4.17 on page 64 of Elisabeth's PhD
# 001_150_P109_im_full.edf - Fig 4.19 on page 65 of Elisabeth's PhD

def convert(filename):
    img = fabio.open(filename)
    print(img.header)

    data = img.data.astype("float64")

    nx, ny = 1024, 1024
    hist = ba.Histogram2D(nx, 0.0, nx*PIX_SIZE*1000., ny, 0.0, ny*PIX_SIZE*1000.)
    hist.setContent(data)

    plt.figure()
    plt.imshow(img.data, norm=colors.LogNorm(100, 1e+07))

    plt.figure()
    ba.plot_histogram(hist)
    #hist.save("004_230_P144_im_full.int.gz")

    plt.show()


if __name__ == '__main__':
    convert('004_230_P144_im_full.edf.gz')
