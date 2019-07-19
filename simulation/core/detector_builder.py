import bornagain as ba


class DetectorBuilder:
    """
    Creates rectangular detector corresponding to 004_230_P144_im_full.int.gz
    """
    def __init__(self, exp_config):
        self.m_config = exp_config
        self.m_distance = 909.99  # mm
        self.m_pixel_size = 4 * 41.74e-3  # mm
        self.m_nx = 1024
        self.m_ny = 1024
        # probably specular beam position in pixel coordinates
        self.m_center_x = exp_config["center_x"]  # distance from left in pixels
        self.m_center_y = exp_config["center_y"]  # distance from top in pixels
        self.m_xpeaks = exp_config["xpeaks"]
        self.m_ypeaks = exp_config["ypeaks"]
        self.peak_radius = 1.6

    def pixel_size(self):
        return self.m_pixel_size

    def create_detector(self):
        width, height = self.m_nx*self.m_pixel_size, self.m_ny*self.m_pixel_size
        u0 = self.m_center_x*self.m_pixel_size
        v0 = (self.m_ny - self.m_center_y)*self.m_pixel_size
        result = ba.RectangularDetector(self.m_nx, width, self.m_ny, height)
        result.setPerpendicularToDirectBeam(self.m_distance, u0, v0)
        return result

    def apply_masks(self, simulation):
        if self.m_config["apply_masks"]:
            simulation.maskAll()
            for xp, yp in zip(self.m_xpeaks, self.m_ypeaks):
                simulation.addMask(ba.Ellipse(xp, yp, self.peak_radius, self.peak_radius*2), False)
