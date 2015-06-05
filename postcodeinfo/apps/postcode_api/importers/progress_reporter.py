from datetime import datetime
import logging
import subprocess


log = logging.getLogger(__name__)


def lines_in_file(filename):
    output = subprocess.Popen(
        ['wc', '-l', filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT).communicate()[0]
    # allow value error if wc reports an error
    return int(output.strip().partition(b' ')[0])


def timestamp():
    return "{0:%a, %d %b %Y %H:%M:%S +0000}".format(datetime.now())


class ProgressReporter(object):

    def __init__(self, total_items):
        self.total = total_items

    def __enter__(self):
        self.progress = 0
        self.remaining = self.total
        self.start_time = datetime.now()
        self.on_start()
        return self

    def on_start(self):
        raise NotImplementedError

    def increment(self, data=None):
        self.progress += 1
        self.remaining -= 1
        self.on_increment(data)

    def on_increment(self, data=None):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback):
        self.on_finish(exc_value)

    def on_finish(self, exception):
        raise NotImplementedError

    @property
    def time_remaining(self):
        return self.remaining * self.time_per_item

    @property
    def time_per_item(self):
        return self.elapsed / self.progress

    @property
    def elapsed(self):
        return datetime.now() - self.start_time


class ImporterProgress(ProgressReporter):

    def put(self, msg, level=logging.DEBUG):
        log.log(level, msg)

    def on_start(self):
        self.put("starting import of {self.total} lines at {timestamp}".format(
            self=self,
            timestamp=timestamp()))

    def on_increment(self, data=None):
        self.put((
            "{timestamp} ({self.elapsed} taken), processed: {self.progress}, "
            "remaining: {self.remaining}, "
            "time_per_row: {self.time_per_item}, "
            "est. time remaining {self.time_remaining}, {data}").format(
                timestamp=timestamp(),
                self=self,
                data=data))

    def on_finish(self, exception):
        self.put((
            'ALL DONE at {timestamp}\n'
            '{self.progress} lines processed in {self.elapsed}').format(
                timestamp=timestamp(),
                self=self))
