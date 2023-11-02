#import assimp as ass
#import texture as tx

#used ChatGPT to help gen this code


import glm
import pybullet as p
import os

import Consts # Import the WorldEnum enumeration from enums.py

# Usage
current_world = Consts.WORLD


class ModelMeshComponent:
    def __init__(self, filePathAndName, shaderProgram, updateOrder):
        self.filePathAndName = filePathAndName
        self.modelScale = None
        self.scaleMeshName = None
        self.subMeshes = []
        self.collisionShape = None

    def buildMesh(self):
        modelScale = self.owningGameObject.getScale(current_world)

        self.scaleMeshName = f"{self.filePathAndName} {modelScale[0][0]} {modelScale[1][1]} {modelScale[2][2]}"

        if not self.previouslyLoaded():
            vData = []
            indices = []

            # Create an instance of the Importer class
            importer = p.Importer()

            # Load the scene/model and associated meshes into an aiScene object
            scene = importer.ReadFile(self.filePathAndName, p.aiProcessPreset_TargetRealtime_Quality)

            if not scene:
                print(f"ERROR: Unable to load {self.filePathAndName} {importer.GetErrorString()}")
                return

            modelCompoundShape = p.CompoundShape()

            for i in range(scene.mNumMeshes):
                mesh = scene.mMeshes[i]
                meshCollisionShape = p.ConvexHullShape()

                self.readVertexData(mesh, vData, indices, meshCollisionShape)

                meshMaterial = scene.mMaterials[scene.mMeshes[i].mMaterialIndex]
                material = self.readInMaterialProperties(meshMaterial, self.filePathAndName)

                subMesh = self.buildSubMesh(vData, indices)
                subMesh.material = material

                modelCompoundShape.addChildShape(p.Transform(p.Quaternion(0, 0, 0)), meshCollisionShape)

                self.subMeshes.append(subMesh)

                vData.clear()
                indices.clear()

            self.collisionShape = modelCompoundShape
            self.saveInitialLoad()

    def readVertexData(self, mesh, vertexData, indices, hull):
        if mesh.HasPositions():
            for i in range(mesh.mNumVertices):
                tempPosition = glm.vec4(mesh.mVertices[i].x, mesh.mVertices[i].y, mesh.mVertices[i].z, 1.0)
                scalePos = self.modelScale * tempPosition
                hull.addPoint(p.Vector3(scalePos.x, scalePos.y, scalePos.z), True)

                tempNormal = glm.vec3(mesh.mNormals[i].x, mesh.mNormals[i].y, mesh.mNormals[i].z)
                tempCoord = glm.vec2(0.0, 0.0)
                if mesh.HasTextureCoords(0):
                    tempCoord.x = mesh.mTextureCoords[0][i].x
                    tempCoord.y = mesh.mTextureCoords[0][i].y

                tempTangent = glm.vec3(0, 0, 0)
                tempBitTangent = glm.vec3(0, 0, 0)
                if mesh.HasTangentsAndBitangents():
                    tempTangent.x = mesh.mTangents[i].x
                    tempTangent.y = mesh.mTangents[i].y
                    tempTangent.z = mesh.mTangents[i].z
                    tempTangent = glm.normalize(tempTangent)

                    tempBitTangent.x = mesh.mBitangents[i].x
                    tempBitTangent.y = mesh.mBitangents[i].y
                    tempBitTangent.z = mesh.mBitangents[i].z
                    tempBitTangent = glm.normalize(tempBitTangent)

                vertexData.append(Consts.pntVertexData(tempPosition, tempNormal, tempCoord, tempTangent, tempBitTangent))

        if mesh.HasFaces():
            for i in range(mesh.mNumFaces):
                indices.append(mesh.mFaces[i].mIndices[0])
                indices.append(mesh.mFaces[i].mIndices[1])
                indices.append(mesh.mFaces[i].mIndices[2])

    def getDirectoryPath(self, sFilePath):
        sDirectory = ""
        for i in range(len(sFilePath) - 1, -1, -1):
            if sFilePath[i] == '\\' or sFilePath[i] == '/':
                sDirectory = sFilePath[:i + 1]
                break
        return sDirectory

    def readInMaterialProperties(self, assimpMaterial, filename):
        '''
        meshMaterial = Material()

        name = p.aiString()
        assimpMaterial.Get(AI_MATKEY_NAME, name)
        if VERBOSE:
            print(f"Loading {name.C_Str()} material:")

        matColor = p.Color3D(0.0, 0.0, 0.0)

        if assimpMaterial.Get(AI_MATKEY_COLOR_AMBIENT, matColor) == AI_SUCCESS:
            meshMaterial.setAmbientMat(glm.vec4(matColor[0], matColor[1], matColor[2], 1.0))

        if assimpMaterial.Get(AI_MATKEY_COLOR_DIFFUSE, matColor) == AI_SUCCESS:
            meshMaterial.setDiffuseMat(glm.vec4(matColor[0], matColor[1], matColor[2], 1.0))

        if assimpMaterial.Get(AI_MATKEY_COLOR_SPECULAR, matColor) == AI_SUCCESS:
            meshMaterial.setSpecularMat(glm.vec4(matColor[0], matColor[1], matColor[2], 1.0))

        if assimpMaterial.Get(AI_MATKEY_COLOR_EMISSIVE, matColor) == AI_SUCCESS:
            meshMaterial.setEmissiveMat(glm.vec4(matColor[0], matColor[1], matColor[2], 1.0))

        path = p.aiString()
        if assimpMaterial.GetTextureCount(p.aiTextureType_DIFFUSE) > 0:
            if AI_SUCCESS == assimpMaterial.GetTexture(p.aiTextureType_DIFFUSE, 0, path, None, None, None, None, None):
                relativeFilePath = self.getDirectoryPath(filename) + path.C_Str()
                if VERBOSE:
                    print(f"Loading diffuse texture: {relativeFilePath}")
                meshMaterial.setDiffuseTexture(Texture.GetTexture(relativeFilePath).getTextureObject())

        if assimpMaterial.GetTextureCount(p.aiTextureType_SPECULAR) > 0:
            if AI_SUCCESS == assimpMaterial.GetTexture(p.aiTextureType_SPECULAR, 0, path, None, None, None, None, None):
                relativeFilePath = self.getDirectoryPath(filename) + path.C_Str()
                if VERBOSE:
                    print(f"Loading specular texture: {relativeFilePath}")
                meshMaterial.setSpecularTexture(Texture.GetTexture(relativeFilePath).getTextureObject())

        if assimpMaterial.GetTextureCount(p.aiTextureType_NORMALS) > 0:
            if AI_SUCCESS == assimpMaterial.GetTexture(p.aiTextureType_NORMALS, 0, path, None, None, None, None, None):
                relativeFilePath = self.getDirectoryPath(filename) + path.C_Str()
                if VERBOSE:
                    print(f"Loading Normal Map texture: {relativeFilePath}")
                meshMaterial.setNormalMap(Texture.GetTexture(relativeFilePath).getTextureObject())

        meshMaterial.setTextureMode(REPLACE_AMBIENT_DIFFUSE)

        return meshMaterial
        '''
#
