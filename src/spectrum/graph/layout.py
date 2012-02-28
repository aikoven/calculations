from random import random
import math
from spectrum.graph.geometry import Point

__author__ = 'Daniel Lytkin'

class Layout(object):
    """Basic abstract implementation of layout.
    Layout provides map vertices -> coordinates
    """

    def __init__(self, graph, default_location=Point(), width=400, height=400):
        self.size = Point(width, height)
        self._locked = set()
        self._graph = graph
        self.__locations = dict()
        self._defaultLocation = default_location

    @property
    def graph(self):
        return self._graph

    def set_unlocked_location(self, vertex, point):
        """Sets location of specified vertex if it is not locked."""
        if vertex not in self._locked:
            self.__locations[vertex] = point

    def __setitem__(self, vertex, point):
        """Sets location of specified vertex."""
        self.__locations[vertex] = point

    def __getitem__(self, vertex):
        if not self.__locations.has_key(vertex):
            self.__locations[vertex] = self._defaultLocation
        return self.__locations[vertex]

    def set_lock(self, vertex, locked):
        """Sets a lock on vertex, so that it won't be moved by layout."""
        if locked:
            self._locked.add(vertex)
        else:
            if vertex in self._locked:
                self._locked.remove(vertex)

    def is_locked(self, vertex):
        return vertex in self._locked

    def update(self):
        """Remove deleted vertices
        """
        deleted_vertices = (self.__locations.viewkeys() -
                            set(range(len(self._graph.vertices))))
        for vertex in deleted_vertices:
            del self.__locations[vertex]

    def reset(self):
        self._locked.clear()
        self.__locations.clear()


class RandomLayout(Layout):
    def __init__(self, graph):
        super(RandomLayout, self).__init__(graph)
        self.reset()

    def __getitem__(self, vertex):
        if not self.__locations.has_key(vertex):
            self.set_unlocked_location(vertex, Point(self.size.x * random(),
                self.size.y * random()))
        return self.__locations[vertex]


class CircleLayout(Layout):
    def __init__(self, graph, r, center=(50, 50), **kw):
        super(CircleLayout, self).__init__(graph, **kw)
        self._center = Point(*center)
        self._radius = r
        self.reset()

    def reset(self):
        super(CircleLayout, self).reset()
        step = 2 * math.pi / len(self.graph.vertices)
        r = self._radius
        for i in range(len(self._graph.vertices)):
            v = Point(math.sin(step * i), math.cos(step * i))
            self.set_unlocked_location(i, self._center + r * v)


class SpringLayout(Layout):
    """Provides force-based layout. Edges are springs, vertices are charged
    particles.
    """

    def __init__(self, graph, spring_rate=1.0, spring_length=200,
                 electric_rate=1.0, damping=0.5, **kw):
        super(SpringLayout, self).__init__(graph, **kw)
        self._spring_rate = spring_rate
        self._spring_length = spring_length
        self._electric_rate = electric_rate
        self._damping = damping

        self.reset()


    def reset(self):
        super(SpringLayout, self).reset()
        # set random initial positions
        for vertex in range(len(self._graph.vertices)):
            self.set_unlocked_location(vertex, Point(self.size.x * random(),
                self.size.y * random()))
        self._velocities = dict.fromkeys(
            range(len(self._graph.vertices)), Point())


    def _repulsion_force(self, vertex, other):
        r = (self[vertex] - self[other]).square()
        if r == 0.0:
            return Point()#random(), random())
        c = 10 ** 6 * self._electric_rate / (r ** 1.5)
        return (self[vertex] - self[other]) * c

    def _attraction_force(self, vertex, other):
        r = (self[vertex] - self[other]).square() ** 0.5
        if r == 0.0:
            return Point()
        c = 10 * self._spring_rate * (self._spring_length - r) / r
        return (self[vertex] - self[other]) * c

    def step(self, time_step):
        """Calculates position of vertices after a lapse of `time_step' after
        last position.
        """
        for vertex in xrange(len(self._graph.vertices)):
            force = Point()

            # repulsion between vertices
            for other in xrange(len(self._graph.vertices)):
                if other == vertex: continue
                force += self._repulsion_force(vertex, other)

            # attraction between edges' ends
            for other in self._graph.neighbors(vertex):
                force += self._attraction_force(vertex, other)

            # border contact force
            def transform_force(coord, right_border, f):
                if coord == 0:
                    return max(0, f)
                if coord == right_border:
                    return min(0, f)
                return f

            force = Point(
                transform_force(self[vertex].x, self.size.x, force.x),
                transform_force(self[vertex].y, self.size.y, force.y))

            vel = self._damping * (self._velocities[vertex] +
                                   time_step * force)
            vel = Point(
                transform_force(self[vertex].x, self.size.x, vel.x),
                transform_force(self[vertex].y, self.size.y, vel.y))
            self._velocities[vertex] = vel

            # this is to prevent going behind borders:
            fx = lambda a: min(max(0, a), self.size.x)
            fy = lambda b: min(max(0, b), self.size.y)
            p = self[vertex] + time_step * vel  # next position of vertex

            self.set_unlocked_location(vertex, Point(fx(p.x), fy(p.y)))

    def total_kinetic_energy(self):
        return sum((v.square() for v in self._velocities))


