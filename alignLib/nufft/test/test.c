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
  // Does not work for odd sized data! OMG!!!
  int L = 15;
  int N=L; // length of spatial domain
  int M=1; // number of sampling nodes (in Fourier space)

  p.m = 6;
  nfft_init_1d(&p,N,M);

  // sampling positions in Fourier space
  // could be irregular!
  p.x[0] = 0.0;

  if(p.nfft_flags & PRE_ONE_PSI)
      nfft_precompute_one_psi(&p);

  // don't confused with the name! Have a look at the formular!
  // in this case, real space!
  // Regular! Remember the layout must be in the order: [-N/2 ... N/2-1]
  // p.f_hat[0] = 5;
  // p.f_hat[1] = 6;
  // p.f_hat[2] = 7;
  // p.f_hat[3] = 8;
  // p.f_hat[4] = 1;
  // p.f_hat[5] = 2;
  // p.f_hat[6] = 3;
  // p.f_hat[7] = 4;

  float sum = 0.0;
  for (int i = 0; i < L; ++i)
  {
    p.f_hat[i] = i;
    sum += i;
  }

  // do the transform
  nfft_trafo(&p);

  // show it
  for (int i = 0; i < p.M_total; ++i)
  {
    printf("%4.3f %4.3f i\n", creal(p.f[i]), cimag(p.f[i]));
  }

  printf("%4.3f\n", sum);

  // // do the adjoint transform
  // nfft_adjoint(&p);

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

// int main(void)
// {
//   nfft_plan p;

//   int N=8; // length of spatial domain
//   int M=5; // number of sampling nodes (in Fourier space)

//   nfft_init_1d(&p,N,M);

//   // sampling positions in Fourier space
//   // could be irregular!
//   // p.x[0] = 0.0;
//   p.x[0] = 0.121;
//   p.x[1] = 0.122;
//   p.x[2] = 0.123;
//   p.x[3] = 0.124;
//   p.x[4] = 0.125;

//   if(p.nfft_flags & PRE_ONE_PSI)
//       nfft_precompute_one_psi(&p);

//   for (int i = 0; i < p.N_total; ++i)
//   {
//     p.f_hat[i] = i;
//   }

//   // do the transform
//   nfft_trafo(&p);

//   // show it
//   for (int i = 0; i < p.M_total; ++i)
//   {
//     printf("%4.3f %4.3f i\n", creal(p.f[i]), cimag(p.f[i]));
//   }

//   nfft_finalize(&p);

//   return 1;

// }