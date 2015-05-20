import subprocess
import time
from time import gmtime, strftime


class ProgressReporter(object):

    def __init__(self):
        self.start_time = None
        self.total_lines = None
        self.lines_processed = None

    def start(self, filename):
        self.total_lines = self.lines_in_file(filename)
        self.lines_processed = 0
        self.start_time = time.time()
        print "starting import of %i lines at %s" % \
            (self.total_lines, self.human_time())

    def row_processed(self, row_identifier=''):
        self.lines_processed += 1
        cumulative_time = self.time_taken()
        print "%s (%s taken), processed: %i, '\
                'remaining: %i, '\
                'time_per_row: %f, '\
                'est. time remaining %s, %s" %  \
            (self.human_time(),
             self.hours_minutes_seconds(cumulative_time),
             self.lines_processed, self.lines_remaining(),
             self.time_per_row(),
             self.hours_minutes_seconds(self.time_remaining()),
             row_identifier
             )

    def finish(self):
        print 'ALL DONE at ' + self.human_time()
        print '%i lines processed in %s' % \
            (self.lines_processed,
             self.hours_minutes_seconds(self.time_taken()))

    def human_time(self):
        return strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    def time_remaining(self):
        cumulative_time = self.time_taken()
        return self.lines_remaining() * self.time_per_row()

    def time_per_row(self):
        return self.time_taken() / self.lines_processed

    def lines_remaining(self):
        return self.total_lines - self.lines_processed

    def time_taken(self):
        return time.time() - self.start_time

    def hours_minutes_seconds(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    def lines_in_file(self, filename):
        output = subprocess.check_output(['wc', '-l', filename], shell=False)
        lines = int(output.split()[0].strip())
        return lines
