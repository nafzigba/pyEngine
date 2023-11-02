from enum import Enum

class WorldEnum(Enum):
    WORLD = 1  # You can assign any integer or value you prefer
    LOCAL = 2
# Usage
current_world = WorldEnum.WORLD

class pntVertexData:
    def __init__(self, pos=(0.0, 0.0, 0.0, 0.0), normal=(0.0, 0.0, 0.0), text_coord=(0.0, 0.0), tangent=(0.0, 0.0, 0.0), bitangent=(0.0, 0.0, 0.0)):
        self.m_pos = pos
        self.m_normal = normal
        self.m_textCoord = text_coord
        self.m_tangent = tangent
        self.m_bitangent = bitangent