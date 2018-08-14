#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <complex.h>

#include "nfft3util.h"
#include "nfft3.h"

int main(void)
{
  nfft_plan p;
  int N=8; // length of spatial domain
  int M=N*N; // number of sampling nodes (in Fourier space)

  nfft_init_2d(&p,N,N,M);

  // sampling positions in Fourier space
  // could be irregular!
  // must not be [-0.5, 0.5], can also range [0 1] (in this case, dont have to shift)
  for (int i = 0; i < p.M_total; ++i)
  {
    p.x[2*i] = 1.0/N*(i/N) - 0.5;
    p.x[2*i+1] = 1.0/N*(i%N) - 0.5;
    // printf("%f %f\n", p.x[2*i], p.x[2*i+1]);
  }

  if(p.nfft_flags & PRE_ONE_PSI)
      nfft_precompute_one_psi(&p);

  // don't confused with the name! Have a look at the formular!
  // in this case, real space!
  // Regular! Remember the layout must be in the order: [-N/2 ... N/2-1]
  // which means, should shift beforehands!
  for (int i = 0; i < N*N; ++i)
  {
    p.f_hat[i] = i;
    // printf("%4.3f %4.3f i\n", creal(p.f_hat[i]), cimag(p.f_hat[i]));
  }

  // do the transform
  nfft_trafo(&p);

  // show it
  for (int i = 0; i < p.M_total; ++i)
  {
    printf("%4.3f %4.3f i\n", creal(p.f[i]), cimag(p.f[i]));
  }

  // // do the adjoint transform
  // ndft_adjoint(&p);

  // // show it
  // printf("\n");
  // for (int i = 0; i < p.N_total; ++i)
  // {
  //   printf("%4.3f %4.3f i\n", creal(p.f_hat[i]), cimag(p.f_hat[i]));
  // }

  /** finalise the two dimensional plan */
  nfft_finalize(&p);

  return 1;
}

