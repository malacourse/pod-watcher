class PodStatus:

    def __init__(self,name,restart,image):
        self.name = name
        self.restartCount = restart
        self.image = image

    def name(self):
        return self.name

    def restartCount(self):
        return self.restartCount
  
    def image(self):
        return self.image
