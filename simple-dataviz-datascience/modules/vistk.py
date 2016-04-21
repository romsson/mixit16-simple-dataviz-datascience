from IPython.core.display import display_html, display, HTML, Javascript
import json
import random
import pandas as pd
import csv

import os
path = os.path.dirname(__file__)

__radius_min = 5
__radius_max = 10
__opacity = 1

class VisTkViz(object):

    JS_LIBS = ['https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js',
               'http://cid-harvard.github.io/vis-toolkit/js/topojson.js',
               'http://cid-harvard.github.io/vis-toolkit/build/vistk.js']

    def create_container(self):
        container_id = "vistk_div_{id}".format(id=random.randint(0, 100000))
        container = """<div id='{id}' style='height:auto;'></div>"""\
            .format(id=container_id)
        display(HTML(container))
        return container_id

    def handle_data(self, data):
        if type(data) == list and len(data) > 0 and type(data[0]) == dict:
            return json.dumps(data)
        elif type(data) == pd.DataFrame:
            return data.to_json(orient="records")
        else:
            raise ValueError()

    def validate_data(self, data):
        raise NotImplementedError()

    def preprocess_data(self, data):
        return data

    def draw(self, data):
        self.container_id = self.create_container()
        self.legend_id = self.create_container()
        data = self.preprocess_data(data)
        json_data = self.handle_data(data)
        self.draw_viz(json_data)

    def draw_viz(self, json_data):
        raise NotImplementedError()

    def update(self):

        js = """
        (function (visualization){
          visualization.params().var_sort_asc = !visualization.params().var_sort_asc;
          visualization.params().init = true
          visualization.params().refresh = true
          d3.select(visualization.container()).call(visualization);
        })(window.visualization)
        """

        display(Javascript(lib=self.JS_LIBS, data=js))

class Scatterplot(VisTkViz):

    def __init__(self, x="x", y="y", id="id", r="r", name=None, color=None, group=None, year=2013):
        super(Scatterplot, self).__init__()
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        self.year = year

        if name is None:
            self.name = id
        else:
            self.name = name

        if group is None:
            self.group = id
        else:
            self.group = group

        if color is None:
            self.color = id
        else:
            self.color = color

    def draw_viz(self, json_data):

        js = """
        (function (){

          var viz_data = %s;
          var viz_container = '#%s';

          var params = {
                type: 'scatterplot',
                width: 800,
                height: 600,
                margin: {top: 10, right: 10, bottom: 30, left: 30},
                container: viz_container,
                data: viz_data,
                var_id: '%s',
                var_group: '%s',
                var_color: '%s',
                color: d3.scale.category10(),
                radius_min: %s,
                radius_max: %s,
                var_x: '%s',
                var_y: '%s',
                var_r: '%s',
                var_text: '%s',
                items: [{
                  marks: [{
                    type: 'circle'
                  }, {
                    var_mark: '__selected',
                    type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                    translate: [10, 10]
                  }, {
                    var_mark: '__highlighted',
                    type: d3.scale.ordinal().domain([true, false]).range(["text", "none"]),
                    translate: [10, 10]
                  }]
                }]
              };

          var visualization = vistk.viz()
            .params(params);

          d3.select(viz_container).call(visualization);

        })();
        """ % (json_data, self.container_id, self.id, self.group, self.color, 5, 10, self.x, self.y, self.r, self.name)

        html_src = """
          <link href='https://cid-harvard.github.io/vis-toolkit/css/vistk.css' rel='stylesheet'>
        """
        display(HTML(data=html_src))

        display(Javascript(lib=self.JS_LIBS, data=js))

