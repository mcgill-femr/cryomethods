/***************************************************************************
  **************************************************************************

                     Python interface of NFFT

   AUTHOR:
   Yuxiang Chen 
   Contact: chenyxkk@hotmail.com 

   Copyright 2011 Yuxiang Chen

   HOW TO USE:
   1. run mkswig.sh, which should generate shared library called _swig_nufft.so
   2. start python, import swig_nufft and enjoy!

  ************************************************************************
  ************************************************************************/

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <complex.h>

#include "nfft3util.h"
#include "nfft3.h"

/**
  v: input, the input volume (linearlized)
  n1, n2, n3: input, dimension of the volume
  x: input, the fourier sampling nodes (linearlized)
  res: output, the result fourier coefficients at those nodes (linearlized)
 */
int fourier_interpolate_3d(float *v, int dim1, int n1, int n2, int n3, double *x, int dim2, float *res, int dim3)
{
  int N[3] = {n1, n2, n3};
  int n[3] = {n1*2, n2*2, n3*2}; // oversampling ratio = 2
  int M = dim2/3;
  int i;

  nfft_plan p;

  nfft_init_guru(&p, 3, N, M, n, 6, // spatial cutoff = 6
     PRE_PHI_HUT| PRE_PSI | MALLOC_F_HAT| MALLOC_X| MALLOC_F |
     FFTW_INIT | FFT_OUT_OF_PLACE,
     FFTW_ESTIMATE | FFTW_DESTROY_INPUT);
  
  // assign f_hat
  for (i = 0; i < p.N_total; ++i)
  {
    p.f_hat[i] = v[i];
  }

  // assign nodes, for some stupid reason the x and z should be swtiched!
  for (i = 0; i < p.M_total; ++i)
  {
    p.x[3*i] = x[3*i+2];
    p.x[3*i+1] = x[3*i+1];
    p.x[3*i+2] = x[3*i];
  }
  
  if(p.nfft_flags & PRE_ONE_PSI)
    nfft_precompute_one_psi(&p);
  
  // do the transform
  nfft_trafo(&p);

  // assign output
  for (i = 0; i < p.M_total; ++i)
  {
    res[2*i] = creal(p.f[i]);
    res[2*i+1] = cimag(p.f[i]);
  }

  nfft_finalize(&p);

  return 1;
}

int fourier_rotate_vol(float *v, int dim1, int n1, int n2, int n3, double *rot, int dim2, float *res, int dim3)
{
  int i,j,k;
  int center_x = n1/2;
  int center_y = n2/2;
  int center_z = n3/2;

  // prepare the plan
  int N[3] = {n1, n2, n3};
  int n[3] = {n1*2, n2*2, n3*2}; // oversampling ratio = 2
  int M = n1*n2*n3;
  nfft_plan p;

  nfft_init_guru(&p, 3, N, M, n, 6, // spatial cutoff = 6
     PRE_PHI_HUT| PRE_PSI | MALLOC_F_HAT| MALLOC_X| MALLOC_F |
     FFTW_INIT | FFT_OUT_OF_PLACE,
     FFTW_ESTIMATE | FFTW_DESTROY_INPUT);
  
  // assign f_hat
  for (i = 0; i < p.N_total; ++i)
  {
    p.f_hat[i] = v[i];
  }

  // calculate the nodes
  double xx, yy, zz;
  for (k = 0; k < n3; ++k)
  {
    for (j = 0; j < n2; ++j)
    {
      for (i = 0; i < n1; ++i)
      {
        // caculate the rotated position in original volume
        xx = (i-center_x)*rot[0]+(j-center_y)*rot[1]+(k-center_z)*rot[2];
        yy = (i-center_x)*rot[3]+(j-center_y)*rot[4]+(k-center_z)*rot[5];
        zz = (i-center_x)*rot[6]+(j-center_y)*rot[7]+(k-center_z)*rot[8];

        p.x[3*(k*n1*n2+j*n1+i)]   = zz/n3;
        p.x[3*(k*n1*n2+j*n1+i)+1] = yy/n2;
        p.x[3*(k*n1*n2+j*n1+i)+2] = xx/n1;
      }
    }
  }

  if(p.nfft_flags & PRE_ONE_PSI)
    nfft_precompute_one_psi(&p);

  // do the transform
  nfft_trafo(&p);

  // assign output
  for (i = 0; i < p.M_total; ++i)
  {
    res[2*i] = creal(p.f[i]);
    res[2*i+1] = cimag(p.f[i]);
  }

  nfft_finalize(&p);

  return 1;
}