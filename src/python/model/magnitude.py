from model import configureFreqAxisFormatting
from model.measurement import REAL_WORLD_DATA, ANALYSED, CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, type=REAL_WORLD_DATA, modelListener=None):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.set_xlim(left=20, right=20000)
        self._axes.grid(linestyle='-', which='major')
        self._axes.grid(linestyle='--', which='minor')
        self._axes.set_ylabel('dBFS')
        self._axes.set_xlabel('Hz')
        self._curves = {}
        self._refreshData = False
        self._type = type
        self._measurementModel = measurementModel
        self._modelListener = modelListener
        self._measurementModel.registerListener(self)

    def shouldRefresh(self):
        return self._refreshData

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        if self.shouldRefresh():
            for idx, x in enumerate(self._measurementModel.getMagnitudeData(type=self._type, ref=1)):
                curve = self._curves.get(x.name)
                if curve:
                    curve.set_data(x.x, x.y)
                else:
                    # todo consider making the reference user selectable, e.g. to allow for dB SPL output
                    self._curves[x.name] = self._axes.semilogx(x.x, x.y,
                                                               linewidth=2,
                                                               antialiased=True,
                                                               linestyle='solid',
                                                               color=self._chart.getColour(idx,
                                                                                           len(self._measurementModel)),
                                                               label=x.name)[0]
            configureFreqAxisFormatting(self._axes)
            if self._axes.get_legend() is None:
                self.makeClickableLegend()
            self._chart.canvas.draw()
            self._refreshData = False

    def makeClickableLegend(self):
        '''
        Add a legend that allows you to make a line visible or invisible by clicking on it.
        ripped from https://matplotlib.org/2.0.0/examples/event_handling/legend_picking.html
        and https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        '''
        # box = self._axes.get_position()
        # self._axes.set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8])
        # # Put a legend below current axis
        # legend = self._axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        legend = self._axes.legend(loc='best', fancybox=True, shadow=True)
        lined = dict()
        for legline, origline in zip(legend.get_lines(), self._curves.values()):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        def onpick(event):
            # on the pick event, find the orig line corresponding to the legend proxy line, and toggle the visibility
            legline = event.artist
            origline = lined[legline]
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            self._chart.canvas.draw()

        self._chart.canvas.mpl_connect('pick_event', onpick)

    def onUpdate(self, type, **kwargs):
        '''
        handles measurement model changes
        If event type is activation toggle then changes the associated curve visibility.
        If event type is analysis change then the model is marked for refresh.
        :param idx: the measurement idx.
        '''
        if self._modelListener:
            self._modelListener.onUpdate(type, kwargs)
        if type == ANALYSED or type == LOAD_MEASUREMENTS:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._curves = {}
