#ifndef _CHANGEBASIS
#define _CHANGEBASIS

#include "tsplinebasis.h"
#include "tboundaryconvention.h"

/*--------------------------------------------------------------------------*/
/**@defgroup SplineTransform Spline transform
   @ingroup BilibLibrary */
//@{

/** Spline transform 1D.
    Change spline coefficients from a source basis into a destination basis.
    InputData is a (double)vector array of size SignalLength.
    OutputData is a (double)vector array of size SignalLength.

    success: return(!ERROR); failure: return(ERROR)
*/
extern int  ChangeBasis
    (
        double InputData[],  /* data to process */
        double OutputData[],  /* result */
        long SignalLength,  /* signal length */
        enum TSplineBasis
        FromBasis,   /* input basis */
        enum TSplineBasis
        ToBasis,   /* output basis */
        long Degree,    /* degree of the representation space */
        enum TBoundaryConvention
        Convention,   /* boundary convention */
        double Tolerance,   /* admissible relative error */
        int  *Status    /* error management */
    );

/*--------------------------------------------------------------------------*/
/** Spline transform 3D.
    Change a volume of spline coefficients from a source basis into a
    destination basis.
    VolumeSource is a (double)volume of size (Nx x Ny x Nz).
    OutputData is a (double)volume of size (Nx x Ny x Nz).

    success: return(!ERROR); failure: return(ERROR)
*/
extern int  ChangeBasisVolume
    (
        double *VolumeSource,  /* data to process */
        double *VolumeDestination, /* result */
        long Nx,     /* width of the volume */
        long Ny,     /* height of the volume */
        long Nz,     /* depth of the volume */
        enum TSplineBasis
        FromBasis,   /* input basis */
        enum TSplineBasis
        ToBasis,   /* output basis */
        long Degree,    /* degree of the representation space */
        enum TBoundaryConvention
        Convention,   /* boundary convention */
        double Tolerance,   /* admissible relative error */
        int  *Status    /* error management */
    );
//@}
#endif
