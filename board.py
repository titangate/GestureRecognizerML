import pygame
import numpy as np

LEFT = 1

running = 1
screen = pygame.display.set_mode((320, 320))

class Stroker(object):
    """docstring for stroker"""
    def __init__(self):
        super(Stroker, self).__init__()
        self.point_queue = []
        self.threshold = 10
        self.sample_size = 10
        self.paths = []
        self.path_to_draw = None

    def finish_path(self, path):
        path = self.finalize_path(path)
        if path is not None:
            self.paths.append(path)

            vecfunc = np.vectorize(lambda a: (a * 100) + 160)
            path_array = vecfunc(path_array)
            print path
        else:
            print 'path too short'


    def start_stroke(self, pos):
        self.point_queue = [pos]

    def end_stroke(self, pos):
        self.point_queue.append(pos)
        self.finish_path(self.point_queue)
        self.point_queue = []

    def insert_point(self, pos):
        if not self.point_queue:return
        #import ipdb; ipdb.set_trace()
        diff = map(lambda a,b : a - b, pos, self.point_queue[-1])
        dis = (diff[0] ** 2 + diff[1] ** 2) ** 0.5
        if dis < self.threshold:
            return
        diff = map(lambda a: a / dis, diff)
        while dis > self.threshold * 2:
            p = map(lambda a, b: a + self.threshold * b, self.point_queue[-1], diff)
            self.point_queue.append(p)
            dis -= self.threshold
        self.point_queue.append(pos)

    def feature_scale(self, path):
        path_array = np.array(path)
        path_array = path_array.astype(np.float)
        means = [np.mean(path_array[:,i]) for i in xrange(path_array.shape[1])]
        stds = [np.std(path_array[:,i]) for i in xrange(path_array.shape[1])]
        g_std = max(stds)
        for i in xrange(path_array.shape[1]):
            vecfunc = np.vectorize(lambda a: (a-means[i]) / g_std)
            path_array[:,i] = vecfunc(path_array[:,i])
        return path_array

    def finalize_path(self, path):
        if len(path) < self.sample_size:
            return None
        final_path = []
        for i in xrange(self.sample_size):
            index = min(len(path) - 1, max(0, i / float(self.sample_size) * len(path)))
            final_path.append(path[int(index)])
        return self.feature_scale(final_path)

    def draw(self):
        if len(self.point_queue) >= 2:
            pygame.draw.lines(screen, (255,255,255), False, self.point_queue)
        elif self.path_to_draw:
            pygame.draw.lines(screen, (255,255,255), False, self.path_to_draw)

        

stroker = Stroker()

while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        stroker.start_stroke(event.pos)
    elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
        stroker.end_stroke(event.pos)
    elif event.type == pygame.MOUSEMOTION:
        stroker.insert_point(event.pos)

    screen.fill((0, 0, 0))
    stroker.draw()
    pygame.display.flip()