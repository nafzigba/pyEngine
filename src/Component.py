class Component:
    VERBOSE = False

    def __init__(self, updateOrder):
        self.updateOrder = updateOrder

    def initialize(self):
        pass

    def __del__(self):
        if Component.VERBOSE:
            print("Component destructor called")

    def update(self, delta_time):
        pass
