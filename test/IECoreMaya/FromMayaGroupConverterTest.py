##########################################################################
#
#  Copyright (c) 2008-2010, Image Engine Design Inc. All rights reserved.
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

import maya.cmds

import IECore
import IECoreScene
import IECoreMaya

class FromMayaGroupConverterTest( IECoreMaya.TestCase ) :

	def testFactory( self ) :

		sphereTransform = maya.cmds.polySphere( subdivisionsX=10, subdivisionsY=5, constructionHistory=False )[0]

		converter = IECoreMaya.FromMayaDagNodeConverter.create( str( sphereTransform ), IECoreScene.TypeId.Group )
		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreMaya.TypeId.FromMayaGroupConverter ) ) )

	def testConversion( self ) :

		cubeTransform = maya.cmds.polyCube()[0]
		maya.cmds.move( 1, 2, 3, cubeTransform )

		converter = IECoreMaya.FromMayaDagNodeConverter.create( str( cubeTransform ), IECoreScene.TypeId.Group )

		converted = converter.convert()

		self.assert_( converted.isInstanceOf( IECoreScene.Group.staticTypeId() ) )
		self.assertEqual( converted.getTransform().transform(), IECore.M44f.createTranslated( IECore.V3f( 1, 2, 3 ) ) )

		self.assertEqual( len( converted.children() ), 1 )
		convertedCube = converted.children()[0]
		self.assert_( convertedCube.isInstanceOf( IECoreScene.MeshPrimitive.staticTypeId() ) )


if __name__ == "__main__":
	IECoreMaya.TestProgram()
