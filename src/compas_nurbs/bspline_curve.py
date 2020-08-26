import compas

from compas.geometry import Primitive
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame

from compas_nurbs.knot_vectors import knot_vector_uniform
from compas_nurbs.knot_vectors import normalize_knot_vector

if not compas.IPY:
    import numpy as np
    from compas_nurbs.evaluators_numpy import evaluate_curve
    from compas_nurbs.evaluators_numpy import evaluate_curve_derivatives
    from compas_nurbs.calculations_numpy import normalize
else:
    from compas_nurbs.evaluators import evaluate_curve
    from compas_nurbs.evaluators import evaluate_curve_derivatives


class Curve(Primitive):
    """Represents a base class for n-variate B-spline (non-rational) curves.

    Parameters
    ----------
    control_points : list of point
        The curve's control points.
    degree : int
        The degree of the curve.
    knot_vector : list of float
        The knot vector of the curve.

    Attributes
    ----------
    data : dict
        The data representation of the curve.
    control_points : list of class:`compas.geometry.Point`
        The curve's control points.
    degree : int
        The degree of the curve.
    knot_vector : list of float
        The knot vector of the curve.

    Examples
    --------
    >>> control_points = [(0.68, 0.44, 0.00), (0.27, 2.50, 0.00), (6.03, 2.18, 0.00), (4.77, 4.50, 0.00)]
    >>> knot_vector = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    >>> curve = Curve(control_points, 3, knot_vector)

    Notes
    -----
    https://github.com/orbingol/NURBS-Python/tree/5.x/geomdl
    """

    def __init__(self, control_points, degree, knot_vector):
        self.degree = degree
        self.knot_vector = knot_vector
        self.rational = False
        if compas.IPY:
            self.control_points = control_points
        else:
            self.control_points = np.array(control_points)

    @property
    def knot_vector(self):
        """list of float : The knot vector of the curve."""
        return self._knot_vector

    @knot_vector.setter
    def knot_vector(self, knot_vector):
        self._knot_vector = normalize_knot_vector(knot_vector)

    @property
    def domain(self):
        return [0., 1.]

    # ==========================================================================
    # constructors
    # ==========================================================================

    @classmethod
    def from_uniform_knot_style(cls, control_points, degree, periodic=False):
        """
        """
        number_of_control_points = len(control_points)
        knot_vector = knot_vector_uniform(degree, number_of_control_points, open=True, periodic=periodic)
        return cls(control_points, degree, knot_vector)

    @classmethod
    def from_chord_knot_style(cls, control_points, degree, periodic=False):
        """
        """
        raise NotImplementedError

    @classmethod
    def from_chord_sqrt_knot_style(cls, control_points, degree, periodic=False):
        """
        """
        raise NotImplementedError

    # ==========================================================================
    # evaluate
    # ==========================================================================

    def points_at(self, params):
        """Evaluates the curve's points at the given parametric positions.

        Parameters
        ----------
        params: list of float
            Evaluation parameters within the curve's domain of [0, 1]

        Returns
        -------
        points : list of :class:`Point`
            Point locations on curve at the parameters.

        Examples
        --------
        >>> curve.points_at([0.0, 0.5, 1.0])
        [Point(0.000, 0.000, 0.000), Point(-0.750, 3.000, 0.000), Point(-4.000, -3.000, 0.000)]
        """
        points = evaluate_curve(self.control_points, self.degree, self.knot_vector, params, self.rational)
        return [Point(*p) for p in points]

    def tangents_at(self, params):
        """Evaluates the unit tangent vector at the given parametric positions.

        Parameters
        ----------
        params: list of float

        Returns
        -------
        list of :class:`Vector`
            Unit tangent vectors of the curve at the given parametric positions.

        Examples
        --------
        >>> curve.tangents_at([0.0, 0.5, 1.0])
        [Vector(0.600, 0.800, 0.000), Vector(-0.868, -0.496, 0.000), Vector(0.000, -1.000, 0.000)]
        """
        st = evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=1)
        return [Vector(*v) for v in normalize(st)]

    def curvatures_at(self, params):
        """Evaluates the curvature at the given parametric positions.

        Parameters
        ----------
        params: list of float

        Returns
        -------
        list of float
            Curvature values of the curve at the given parametric positions.

        Examples
        --------
        >>> curvature = curve.curvatures_at([0.0, 0.5])
        >>> allclose(curvature, [0.042667, 0.162835])
        True
        """
        st = evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=1)
        nd = evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=2)
        k = np.linalg.norm(np.cross(st, nd, axis=1), axis=1) / np.linalg.norm(st, axis=1)**3
        return list(k)

    def frames_at(self, params):
        """Evaluates the curve's frames at the given parametric positions.

        Parameters
        ----------
        params: list of float

        Returns
        -------
        list of :class:`Frame`

        Examples
        --------
        >>> curve.frames_at([0.5])
        [Frame(Point(-0.750, 3.000, 0.000), Vector(-0.868, -0.496, 0.000), Vector(0.496, -0.868, 0.000))]
        """
        points = self.points_at(params)
        st = evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=1)
        nd = evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=2)
        binormal = normalize(np.cross(st, nd, axis=1))
        tangents = normalize(st)
        normals = np.cross(binormal, tangents, axis=1)
        return [Frame(pt, xaxis, yaxis) for pt, xaxis, yaxis in zip(points, tangents, normals)]

    def derivatives_at(self, params):
        return evaluate_curve_derivatives(self.control_points, self.degree, self.knot_vector, params, order=1)

    # ==========================================================================
    # operations
    # ==========================================================================

    def reverse(self):
        raise NotImplementedError

    def split(self):
        raise NotImplementedError

    def trim(self):
        raise NotImplementedError

    def to_nurbs_curve(self):  # from bspline
        raise NotImplementedError

    def get_bounding_box(self):
        raise NotImplementedError

    def point_at_length(self):
        raise NotImplementedError

    # ==========================================================================
    # queries
    # ==========================================================================

    def is_linear(self):
        raise NotImplementedError

    def is_periodic(self):
        raise NotImplementedError

    @property
    def is_planar(self):
        """Returns ``True`` if the curve is planar.
        """
        # TODO: only checks if the curve is planar in xy-, xz-, yz-plane, oriented bounding box to check?
        ranges = np.ptp(self.control_points, axis=0)
        is_planar = not ranges.all()
        ix, iy, iz = np.argsort(ranges)[::-1]
        return is_planar, np.take(self.control_points, [ix, iy], axis=1)

    # ==========================================================================
    # serialisation
    # ==========================================================================

    @property
    def data(self):
        """dict: The data dictionary that represents the curve."""
        return {'control_points': [list(point) for point in self.control_points],
                'knot_vector': self.knot_vector,
                'degree': self.degree}

    @classmethod
    def from_data(cls, data):
        return cls(data['control_points'], data['degree'], data['knot_vector'])


if __name__ == '__main__':

    import doctest
    from compas.geometry import allclose  # noqa: F401

    control_points = [(0, 0, 0), (3, 4, 0), (-1, 4, 0), (-4, 0, 0), (-4, -3, 0)]
    curve = Curve.from_uniform_knot_style(control_points, degree=3)

    doctest.testmod(globs=globals())