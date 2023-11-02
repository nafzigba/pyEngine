class GameObject:
    VERBOSE = False
    OwningGame = None
    PendingChildren = []
    RemovedGameObjects = []
    ReparentedGameObjects = []

    class STATE:
        ACTIVE = 1

    class ReparentPair:
        def __init__(self, newParent, child):
            self.newParent = newParent
            self.child = child

    def __init__(self):
        self.gameObjectState = GameObject.STATE.ACTIVE
        self.parent = None
        self.components = []
        self.children = []
        self.localTransform = None  # Define this as needed

    def initialize(self):
        for component in self.components:
            component.initialize()
        self.updateModelingTransformation()
        for child in self.children:
            child.initialize()

    def update(self, delta_time):
        if self.gameObjectState == GameObject.STATE.ACTIVE:
            for component in self.components:
                component.update(delta_time)
            self.updateModelingTransformation()
            for child in self.children:
                child.update(delta_time)

    def processInput(self):
        if self.gameObjectState == GameObject.STATE.ACTIVE:
            for component in self.components:
                component.processInput()
        for child in self.children:
            child.processInput()

    def addComponent(self, component):
        component.owningGameObject = self
        self.components.append(component)
        self.components.sort(key=lambda x: x.updateOrder)
        if component.getComponentType() == MESH:
            MeshComponent.addMeshComp(component)
        if component.getComponentType() == CAMERA:
            pass  # Add to the camera component list if needed

    def removeComponent(self, component):
        if component in self.components:
            if GameObject.VERBOSE:
                print(f"Component removed.")
            self.components.remove(component)
            if component.getComponentType() == MESH:
                MeshComponent.removeMeshComp(component)
            if component.getComponentType() == CAMERA:
                pass  # Remove from the camera component list if needed

    def setState(self, state):
        self.gameObjectState = state

    def addChildGameObject(self, child):
        if child is not None:
            child.parent = self
            if GameObject.OwningGame.isRunning:
                if GameObject.VERBOSE:
                    print("pending add")
                GameObject.PendingChildren.append(child)
            else:
                if GameObject.VERBOSE:
                    print("direct add")
                self.children.append(child)

    def removeAndDelete(self):
        GameObject.RemovedGameObjects.append(self)

    def reparent(self, child):
        GameObject.ReparentedGameObjects.append(GameObject.ReparentPair(self, child))

    def updateModelingTransformation(self):
        # Implement the transformation logic here
        pass

    @staticmethod
    def UpdateSceneGraph():
        GameObject.AddPendingGameObjects()
        GameObject.RemoveDeletedGameObjects()
        GameObject.ReparentGameObjects()

    @staticmethod
    def RemoveDeletedGameObjects():
        found = False
        for gameObject in GameObject.RemovedGameObjects:
            parentGameObject = gameObject.parent
            if gameObject in parentGameObject.children:
                found = True
                index = parentGameObject.children.index(gameObject)
                parentGameObject.children[index] = parentGameObject.children[-1]
                parentGameObject.children.pop()
            if not found:
                if gameObject in GameObject.PendingChildren:
                    found = True
                    index = GameObject.PendingChildren.index(gameObject)
                    GameObject.PendingChildren[index] = GameObject.PendingChildren[-1]
                    GameObject.PendingChildren.pop()
        GameObject.RemovedGameObjects.clear()

    @staticmethod
    def AddPendingGameObjects():
        for pending in GameObject.PendingChildren:
            if GameObject.VERBOSE:
                print("Delayed addition of pending object")
            parentGameObject = pending.parent
            parentGameObject.children.append(pending)
            pending.initialize()
            pending.updateModelingTransformation()
            pending.update(0.0)
        GameObject.PendingChildren.clear()

    @staticmethod
    def ReparentGameObjects():
        pass  # Implement reparenting logic here

