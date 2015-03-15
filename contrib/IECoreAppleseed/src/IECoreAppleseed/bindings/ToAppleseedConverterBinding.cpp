//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2014, Esteban Tovagliari. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "Python.h"

#include "IECoreAppleseed/ToAppleseedConverter.h"
#include "IECoreAppleseed/bindings/ToAppleseedConverterBinding.h"

#include "IECorePython/RunTimeTypedBinding.h"

#include "IECore/Object.h"

#include "foundation/utility/autoreleaseptr.h"
#include "renderer/modeling/entity/entity.h"

using namespace boost::python;
using namespace IECoreAppleseed;

namespace asf = foundation;
namespace asr = renderer;

object IECoreAppleseed::entityToPythonObject( asr::Entity *entity )
{
	if( !entity )
		return object();

	asf::auto_release_ptr<asr::Entity> pointer( entity );
	return object( pointer );
}

static object convertWrapper( ToAppleseedConverter &converter )
{
	return entityToPythonObject( converter.convert() );
}

void IECoreAppleseed::bindToAppleseedConverter()
{
	IECorePython::RunTimeTypedClass<ToAppleseedConverter>()
		.def( "convert", &convertWrapper )
		.def( "create", &ToAppleseedConverter::create )
		.staticmethod( "create" )
	;
}
