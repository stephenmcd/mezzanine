from ..mezzanine import MezzanineTask


class AbstractWebsiteTask(MezzanineTask):
    def __init__(self, environment, *args, **kwargs):
        super(MezzanineTask, self).__init__(*args, **kwargs)
        self.env = environment