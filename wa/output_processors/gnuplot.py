#    Copyright 2021 ARM Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Description:
#   This is a derivative of the csvproc parser to additionally generate graphs using GNUplot
#   This is an extension of work done for the auto-generation of plots from SPEC results

from wa import Parameter, OutputProcessor
from wa.framework.exception import ConfigError
from wa.utils.types import list_of_strings
import subprocess

class GNUPlotProcessor(OutputProcessor):
    name = 'gnuplot'
    description = """
    Invokes a local instance of GNUplot to plot the results extracted through
    the original 'csv' parser.
    (Note that this currently only works for results from the SPEC(int,fp) WL.
    
    """
    
    parameters = [
        Parameter('plot_title', kind=str, default="<!SET TITLE!>",
                    global_alias='plot_title',
                    description="""
                    Sets the output plot title.
                    
                    """),
        Parameter
    ]
    
    def __init__(self, *args, **kwargs):
        super(GNUPlotProcessor, self).__init__(*args, **kwargs)
        self.outputs_so_far = []
        self.artifact_added = False
        
    def validate(self):
        super(GNUPlotProcessor, self).validate()
        
    # pylint: disable=unused-argument
    def process_job_output(self, output, target_info, run_output):
        self.outputs_so_far.append(output)
        self._generate_dat(outputs_so_far, run_output)
        if not self.artifact_added:
            output.add_artifact('run_result_gnuplot_dat', 'results.dat', 'export')
            self.artifact_added = True

    def process_run_output(self, output, target_info):  # pylint: disable=unused-argument
        pass # TODO
        
    def _generate_dat(self, outputs, output):
        outfile = output.get_path('results.dat')
        with open(outfile, 'w') as f:
            for o in outputs:
                if o.kind == 'job':  # For the moment, only handle individual jobs
                    job_benchmark = [o.label]
                    for metric in o.result.metrics:
                        row = (job_benchmark + [str(metric.value), metric.units or ''])
                        print(*row, file=f)
                else:
                    raise RuntimeError(
                        'job type {} unrecognised by gnuplot processor'.format(o.kind))
                        
    def _do_plot(self, output):
        self.gp = subprocess.Popen(['gnuplot', '-p'], shell=True, stdin=subprocess.PIPE)
        sendcmd = self.gp.stdin.write
        
        sendcmd("set title '{}'\n".format(plot_title))
        sendcmd("set xlabel 'Workload Label'\n")
        sendcmd("set ylabel 'Metric Value'\n")
        sendcmd('plot "results.dat" using 2:xtics(1) with bars\n')
        sendcmd('pause -1 "Hit <Enter> to exit"\n')
        sendcmd('exit\n')
            
        

        