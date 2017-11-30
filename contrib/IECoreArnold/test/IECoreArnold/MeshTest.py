##########################################################################
#
#  Copyright (c) 2012, John Haddon. All rights reserved.
#  Copyright (c) 2012, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import unittest

import arnold

import IECore
import IECoreScene
import IECoreImage
import IECoreArnold

class MeshTest( unittest.TestCase ) :

	def testUVs( self ) :

		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		uvData = m["uv"].data

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )

			uvs = arnold.AiNodeGetArray( n, "uvlist" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvs.contents ), 4 )

			uvIndices = arnold.AiNodeGetArray( n, "uvidxs" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvIndices.contents ), 4 )

			for i in range( 0, 4 ) :
				p = arnold.AiArrayGetVec2( uvs, i )
				self.assertEqual( arnold.AiArrayGetVec2( uvs, i ), arnold.AtVector2( uvData[i][0], uvData[i][1] ) )
				self.assertEqual( arnold.AiArrayGetInt( uvIndices, i ), i )

	def testIndexedUVs( self ) :

		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		m["uv"] = IECoreScene.PrimitiveVariable( IECoreScene.PrimitiveVariable.Interpolation.FaceVarying, m["uv"].data, IECore.IntVectorData( [ 0, 3, 1, 2 ] ) )
		uvData = m["uv"].data
		uvIds = m["uv"].indices

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )

			uvs = arnold.AiNodeGetArray( n, "uvlist" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvs.contents ), 4 )

			uvIndices = arnold.AiNodeGetArray( n, "uvidxs" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvIndices.contents ), 4 )

			for i in range( 0, 4 ) :
				aiUv = arnold.AiArrayGetVec2( uvs, i )
				aiUVId = arnold.AiArrayGetInt( uvIndices, i )
				aiIndexedUV = arnold.AiArrayGetVec2( uvs, aiUVId )
				self.assertEqual( aiUVId, uvIds[i] )
				self.assertEqual( aiUv, arnold.AtVector2( uvData[i][0], uvData[i][1] ) )
				self.assertEqual( aiIndexedUV, arnold.AtVector2( uvData[uvIds[i]][0], uvData[uvIds[i]][1] ) )

	def testAdditionalUVs( self ) :

		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		m["myMap"] = m["uv"]
		uvData = m["uv"].data

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )

			uvs = arnold.AiNodeGetArray( n, "myMap" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvs.contents ), 4 )

			uvIndices = arnold.AiNodeGetArray( n, "myMapidxs" )
			self.assertEqual( arnold.AiArrayGetNumElements( uvIndices.contents ), 4 )

			for i in range( 0, 4 ) :
				p = arnold.AiArrayGetVec2( uvs, i )
				self.assertEqual( arnold.AiArrayGetVec2( uvs, i ), arnold.AtVector2( uvData[i][0], uvData[i][1] ) )
				self.assertEqual( arnold.AiArrayGetInt( uvIndices, i ), i )

	def testNormals( self ) :

		r = IECoreArnold.Renderer()
		r.display( "test", "ieDisplay", "rgba", { "driverType" : "ImageDisplayDriver", "handle" : "testHandle" } )
		with IECoreScene.WorldBlock( r ) :
			r.concatTransform( IECore.M44f.createTranslated( IECore.V3f( 0, 0, -5 ) ) )
			r.shader( "surface", "utility", { "shade_mode" : "flat", "color_mode" : "n" } )
			m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -0.9 ), IECore.V2f( 0.9 ) ) )
			m["N"] = IECoreScene.PrimitiveVariable(
					IECoreScene.PrimitiveVariable.Interpolation.Vertex,
					IECore.V3fVectorData( [ IECore.V3f( 1, 0, 0 ), IECore.V3f( 1, 0, 0 ), IECore.V3f( 1, 0, 0 ), IECore.V3f( 1, 0, 0 ) ] )
			)
			m.render( r )

		del r

		image = IECoreImage.ImageDisplayDriver.removeStoredImage( "testHandle" )

		# the utility shader encodes the normals in the range 0-1 rather than -1-1,
		# which is why we're checking G and B against .5 rather than 0.
		dimensions = image.dataWindow.size() + IECore.V2i( 1 )
		index = dimensions.x * int(dimensions.y * 0.5) + int(dimensions.x * 0.5)
		self.assertAlmostEqual( image["R"][index], 1, 4 )
		self.assertAlmostEqual( image["G"][index], 0.5, 4 )
		self.assertAlmostEqual( image["B"][index], 0.5, 4 )

	def testVertexPrimitiveVariables( self ) :

		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		m["myPrimVar"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.FloatVectorData( [ 0, 1, 2, 3 ] )
		)
		m["myV3fPrimVar"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.V3fVectorData( [ IECore.V3f( v ) for v in range( 0, 4 ) ] )
		)

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )
			a = arnold.AiNodeGetArray( n, "myPrimVar" )
			v = arnold.AiNodeGetArray( n, "myV3fPrimVar" )
			self.assertEqual( arnold.AiArrayGetNumElements( a.contents ), 4 )
			for i in range( 0, 4 ) :
				self.assertEqual( arnold.AiArrayGetFlt( a, i ), i )
				self.assertEqual( arnold.AiArrayGetVec( v, i ), i )

	def testFaceVaryingPrimitiveVariables( self ) :

		m = IECoreScene.MeshPrimitive.createPlane(
			IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ),
			IECore.V2i( 2 ),
		)
		self.assertEqual( m.variableSize( IECoreScene.PrimitiveVariable.Interpolation.FaceVarying ), 16 )

		m["myPrimVar"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.FaceVarying,
			IECore.FloatVectorData( range( 0, 16 ) )
		)

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )
			a = arnold.AiNodeGetArray( n, "myPrimVar" )
			ia = arnold.AiNodeGetArray( n, "myPrimVaridxs" )
			self.assertEqual( arnold.AiArrayGetNumElements( a.contents ), 16 )
			self.assertEqual( arnold.AiArrayGetNumElements( ia.contents ), 16 )
			for i in range( 0, 16 ) :
				self.assertEqual( arnold.AiArrayGetFlt( a, i ), i )
				self.assertEqual( arnold.AiArrayGetUInt( ia, i ), i )

	def testMotion( self ) :

		m1 = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		IECoreScene.MeshNormalsOp()( input = m1, copyInput = False )

		m2 = m1.copy()
		m2["P"].data[0] -= IECore.V3f( 0, 0, 1 )
		m2["P"].data[1] -= IECore.V3f( 0, 0, 1 )
		IECoreScene.MeshNormalsOp()( input = m2, copyInput = False )

		with IECoreArnold.UniverseBlock( writable = True ) :

			node = IECoreArnold.NodeAlgo.convert( [ m1, m2 ], -0.25, 0.25, "testMesh" )

			vList = arnold.AiNodeGetArray( node, "vlist" )
			self.assertEqual( arnold.AiArrayGetNumElements( vList.contents ), 4 )
			self.assertEqual( arnold.AiArrayGetNumKeys( vList.contents ), 2 )

			nList = arnold.AiNodeGetArray( node, "nlist" )
			self.assertEqual( arnold.AiArrayGetNumElements( nList.contents ), 4 )
			self.assertEqual( arnold.AiArrayGetNumKeys( nList.contents ), 2 )

			for i in range( 0, 4 ) :
				p = arnold.AiArrayGetVec( vList, i )
				self.assertEqual( IECore.V3f( p.x, p.y, p.z ), m1["P"].data[i] )
				n = arnold.AiArrayGetVec( nList, i )
				self.assertEqual( IECore.V3f( n.x, n.y, n.z ), m1["N"].data[i] )

			for i in range( 4, 8 ) :
				p = arnold.AiArrayGetVec( vList, i )
				self.assertEqual( IECore.V3f( p.x, p.y, p.z ), m2["P"].data[i-4] )
				n = arnold.AiArrayGetVec( nList, i )
				self.assertEqual( IECore.V3f( n.x, n.y, n.z ), m2["N"].data[i-4] )

			self.assertEqual( arnold.AiNodeGetFlt( node, "motion_start" ), -0.25 )
			self.assertEqual( arnold.AiNodeGetFlt( node, "motion_end" ), 0.25 )

	def testClashingPrimitiveVariables( self ) :
		# make sure that names of arnold built-in's can't be used as names for primitive variables
		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )

		m["name"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Uniform,
			IECore.StringData( "CannotRenameMe" )
		)

		expectedMsg = 'Primitive variable "name" will be ignored because it clashes with Arnold\'s built-in parameters'

		with IECoreArnold.UniverseBlock( writable = True ) :
			msg = IECore.CapturingMessageHandler()
			with msg :
				IECoreArnold.NodeAlgo.convert( m, "testMesh" )

			self.assertEqual( len(msg.messages), 1 )
			self.assertEqual( msg.messages[-1].message, expectedMsg )
			self.assertEqual( msg.messages[-1].level, IECore.Msg.Level.Warning )

	def testPointTypePrimitiveVariables( self ) :
		# make sure that we can add prim vars of both vector and point type, and differentiate between the two.
		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )

		points = IECore.V3fVectorData( [] )
		IECore.setGeometricInterpretation( points, IECore.GeometricData.Interpretation.Point )
		m["points"] = IECoreScene.PrimitiveVariable( IECoreScene.PrimitiveVariable.Interpolation.Vertex, points )

		vectors = IECore.V3fVectorData( [] )
		IECore.setGeometricInterpretation( vectors, IECore.GeometricData.Interpretation.Vector )
		m["vectors"] = IECoreScene.PrimitiveVariable( IECoreScene.PrimitiveVariable.Interpolation.Vertex, vectors )

		with IECoreArnold.UniverseBlock( writable = True ) :
			node = IECoreArnold.NodeAlgo.convert( m, "testMesh" )
			p = arnold.AiNodeGetArray( node, "points" )
			self.assertEqual( arnold.AiArrayGetType( p.contents ), arnold.AI_TYPE_VECTOR )

			v = arnold.AiNodeGetArray( node, "vectors" )
			self.assertEqual( arnold.AiArrayGetType( v.contents ), arnold.AI_TYPE_VECTOR )

	def testBoolVectorPrimitiveVariables( self ) :

		m = IECoreScene.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		m["myBoolPrimVar"] = IECoreScene.PrimitiveVariable(
			IECoreScene.PrimitiveVariable.Interpolation.Vertex,
			IECore.BoolVectorData( [ True, False, True, False ] )
		)

		with IECoreArnold.UniverseBlock( writable = True ) :

			n = IECoreArnold.NodeAlgo.convert( m, "testMesh" )
			a = arnold.AiNodeGetArray( n, "myBoolPrimVar" )

			self.assertEqual( arnold.AiArrayGetNumElements( a.contents ), 4 )
			self.assertEqual( arnold.AiArrayGetBool( a, 0 ), True )
			self.assertEqual( arnold.AiArrayGetBool( a, 1 ), False )
			self.assertEqual( arnold.AiArrayGetBool( a, 2 ), True )
			self.assertEqual( arnold.AiArrayGetBool( a, 3 ), False )

if __name__ == "__main__":
    unittest.main()
