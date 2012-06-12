# Copyright (C) 2012  Josh Willis, Andrew Miller
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#
"""
This module provides the cufft backend of the fast Fourier transform
for the PyCBC package.
"""

import pycbc.array
import scikits.cuda.fft as cu_fft

_forward_plans = {}
_reverse_plans = {}

#These dicts need to be cleared before the cuda context is destroyed
def _clear_plan_dicts():
    _forward_plans.clear()
    _reverse_plans.clear()

pycbc.scheme.register_clean_cuda(_clear_plan_dicts)

#itype and otype are actual dtypes here, not strings
def _get_fwd_plan(itype,otype,inlen):
    try:
        theplan = _forward_plans[(itype,otype,inlen)]
    except KeyError:
        theplan = cu_fft.Plan((inlen,),itype,otype)
        _forward_plans.update({(itype,otype,inlen) : theplan })

    return theplan

#The complex to real plan wants the actual size, not the N/2+1
#That's why the inverse plans use the outvec length, instead of the invec
def _get_inv_plan(itype,otype,outlen):
    try:
        theplan = _reverse_plans[(itype,otype,outlen)]
    except KeyError:
        theplan = cu_fft.Plan((outlen,),itype,otype)
        _reverse_plans.update({(itype,otype,outlen) : theplan })

    return theplan


def fft(invec,outvec,prec,itype,otype):
    
    if itype =='complex' and otype == 'complex':
        cuplan = _get_fwd_plan(invec.dtype,outvec.dtype,len(invec))
        cu_fft.fft(invec.data,outvec.data,cuplan)

    elif itype=='real' and otype=='complex':
        #The cufft algorithm doesn't return exact zeros for imaginary parts of this transform
        #it returns imaginary components on the order of 10^-16 for double, and 10^-8 for single. Because of this, the forward
        #real to complex tests do not currently pass the unit tests.
        cuplan = _get_fwd_plan(invec.dtype,outvec.dtype,len(invec))
        cu_fft.fft(invec.data,outvec.data,cuplan)

def ifft(invec,outvec,prec,itype,otype):
    
    if itype =='complex' and otype == 'complex':
        cuplan = _get_inv_plan(invec.dtype,outvec.dtype,len(outvec))
        cu_fft.ifft(invec.data,outvec.data,cuplan)

    elif itype=='complex' and otype=='real':
        cuplan = _get_inv_plan(invec.dtype,outvec.dtype,len(outvec))
        cu_fft.ifft(invec.data,outvec.data,cuplan)

