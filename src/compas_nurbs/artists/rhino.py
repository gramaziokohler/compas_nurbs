import compas
from compas.utilities import flatten
from compas_rhino.artists import BaseArtist

if compas.IPY:
    import Rhino.Geometry as rg
    import rhinoscriptsyntax as rs


class CurveArtist(BaseArtist):
    """
    """

    def __init__(self, curve):
        self.curve = curve

    def draw(self):
        points = [rg.Point3d(*p) for p in self.curve.control_points]
        knots = self.curve.knot_vector[1:-1]
        return rs.AddNurbsCurve(points, knots, self.curve.degree, self.curve.weights)

    def draw_points(self):
        return rs.AddPoints(self.curve.control_points)


class SurfaceArtist(BaseArtist):
    """
    """

    def __init__(self, surface):
        self.surface = surface

    def draw(self):
        point_count = self.surface.count
        points = [rg.Point3d(*p) for pl in self.surface.control_points for p in pl]
        weights = list(flatten(self.surface.weights))
        knots_u = self.surface.knot_vector[0][1:-1]
        knots_v = self.surface.knot_vector[1][1:-1]
        degree = self.surface.degree
        ns = rg.NurbsSurface.Create(3, weights is not None, degree[0] + 1, degree[1] + 1, point_count[0], point_count[1])
        index = 0
        for i in range(point_count[0]):
            for j in range(point_count[1]):
                if weights:
                    cp = rg.ControlPoint(points[index], weights[index])
                    ns.Points.SetControlPoint(i, j, cp)
                else:
                    cp = rg.ControlPoint(points[index])
                    ns.Points.SetControlPoint(i, j, cp)
                index += 1
        for i in range(ns.KnotsU.Count):
            ns.KnotsU[i] = knots_u[i]
        for i in range(ns.KnotsV.Count):
            ns.KnotsV[i] = knots_v[i]
        assert(ns.IsValid)
        return ns

    def draw_points(self):
        return rs.AddPoints(self.surface.control_points)
